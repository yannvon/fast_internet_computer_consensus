use std::{
    collections::BTreeMap,
    sync::{Arc, RwLock},
};

use crate::{HeightMetrics, SubnetParams};

use super::{
    artifacts::{ChangeAction, ChangeSet, ConsensusMessage},
    consensus_subcomponents::{
        acknowledger::Acknowledger, aggregator::ShareAggregator, block_maker::BlockMaker,
        finalizer::Finalizer, goodifier::Goodifier, notary::Notary, validator::Validator,
    },
    height_index::Height,
    pool::ConsensusPoolImpl,
    pool_reader::PoolReader,
};

// Rotate on_state_change calls with a round robin schedule to ensure fairness.
#[derive(Default)]
pub struct RoundRobin {
    index: std::cell::RefCell<usize>,
}

impl RoundRobin {
    // Call the next function in the given list of calls according to a round
    // robin schedule. Return as soon as a call returns a non-empty ChangeSet.
    // Otherwise try calling the next one, and return empty ChangeSet if all
    // calls from the given list have been tried.
    pub fn call_next<T>(&self, calls: &[&dyn Fn() -> (Vec<T>, bool)]) -> (Vec<T>, bool) {
        let mut result;
        let mut to_broadcast;
        let index = self.index.borrow_mut();
        let mut next = *index;
        loop {
            (result, to_broadcast) = calls[next]();
            next = (next + 1) % calls.len();
            if !result.is_empty() || *index == next {
                return (result, to_broadcast);
            };
        }
        //*index = next;
        //(result, to_broadcast)
    }
}

pub struct ConsensusImpl {
    goodifier: Goodifier,
    acknowledger: Acknowledger,
    finalizer: Finalizer,
    block_maker: BlockMaker,
    notary: Notary,
    aggregator: ShareAggregator,
    validator: Validator,
    schedule: RoundRobin,
    subnet_params: SubnetParams,
}

impl ConsensusImpl {
    pub fn new(replica_number: u8, subnet_params: SubnetParams) -> Self {
        Self {
            goodifier: Goodifier::new(replica_number, subnet_params.clone()),
            acknowledger: Acknowledger::new(replica_number, subnet_params.clone()),
            finalizer: Finalizer::new(replica_number, subnet_params.clone()),
            block_maker: BlockMaker::new(replica_number, subnet_params.clone()),
            notary: Notary::new(replica_number, subnet_params.clone()),
            aggregator: ShareAggregator::new(replica_number, subnet_params.clone()),
            validator: Validator::new(replica_number),
            schedule: RoundRobin::default(),
            subnet_params,
        }
    }

    pub fn on_state_change(
        &self,
        pool: &ConsensusPoolImpl,
        finalization_times: Arc<RwLock<BTreeMap<Height, Option<HeightMetrics>>>>,
    ) -> (ChangeSet, bool) {
        // Invoke `on_state_change` on each subcomponent in order.
        // Return the first non-empty [ChangeSet] as returned by a subcomponent.
        // Otherwise return an empty [ChangeSet] if all subcomponents return
        // empty.
        //
        // There are two decisions that ConsensusImpl makes:
        //
        // 1. It must return immediately if one of the subcomponent returns a
        // non-empty [ChangeSet]. It is important that a [ChangeSet] is fully
        // applied to the pool or timer before another subcomponent uses
        // them, because each subcomponent expects to see full state in order to
        // make correct decisions on what to do next.
        //
        // 2. The order in which subcomponents are called also matters. At the
        // moment it is important to call finalizer first, because otherwise
        // we'll just keep producing notarized blocks indefintely without
        // finalizing anything, due to the above decision of having to return
        // early. The order of the rest subcomponents decides whom is given
        // a priority, but it should not affect liveness or correctness.

        let pool_reader = PoolReader::new(pool);

        let validate = || {
            self.validator
                .on_state_change(&pool_reader, Arc::clone(&finalization_times))
        };

        let acknowledge = || {
            if self.subnet_params.fast_internet_computer_consensus {
                let change_set = add_all_to_validated(
                    self.acknowledger
                        .on_state_change(&pool_reader, Arc::clone(&finalization_times)),
                );
                let to_broadcast = true;
                (change_set, to_broadcast)
            } else {
                (vec![], false)
            }
        };

        let finalize = || {
            let change_set = add_all_to_validated(self.finalizer.on_state_change(&pool_reader));
            let to_broadcast = true;
            (change_set, to_broadcast)
        };

        let notarize = || {
            let change_set = add_all_to_validated(self.notary.on_state_change(&pool_reader));
            let to_broadcast = true;
            (change_set, to_broadcast)
        };

        let make_block = || {
            let change_set = add_all_to_validated(self.block_maker.on_state_change(&pool_reader));
            let to_broadcast = true;
            (change_set, to_broadcast)
        };

        let aggregate = || {
            let change_set = add_all_to_validated(
                self.aggregator
                    .on_state_change(&pool_reader, Arc::clone(&finalization_times)),
            );
            // aggregation of shares does not have to be broadcasted as each node can compute it locally based on its consensus pool
            let to_broadcast = false;
            (change_set, to_broadcast)
        };

        // must be the last component called as it can return the same artifact in multiple iterations
        // running it before the other components might starve them as we break out of the loop
        // as soon as a component returns an artifact
        let goodify = || {
            if self.subnet_params.fast_internet_computer_consensus {
                let change_set = add_all_to_validated(self.goodifier.on_state_change(&pool_reader));
                let to_broadcast = false;
                (change_set, to_broadcast)
            } else {
                (vec![], false)
            }
        };

        let calls: [&'_ dyn Fn() -> (ChangeSet, bool); 7] = [
            &acknowledge,
            &finalize,
            &aggregate,
            &notarize,
            &make_block,
            &validate,
            &goodify,
        ];

        let (changeset, to_broadcast) = self.schedule.call_next(&calls);

        (changeset, to_broadcast)
    }
}

fn add_all_to_validated(messages: Vec<ConsensusMessage>) -> ChangeSet {
    messages
        .into_iter()
        .map(ChangeAction::AddToValidated)
        .collect()
}
/*
fn add_to_validated(msg: Option<ConsensusMessage>) -> ChangeSet {
    msg.map(|msg| ChangeAction::AddToValidated(msg).into())
        .unwrap_or_default()
}
*/
