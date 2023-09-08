//! The share aggregator is responsible for the aggregation of different types
//! of shares into full objects. That is, it constructs Random Beacon objects
//! from random beacon shares, Notarizations from notarization shares and
//! Finalizations from finalization shares.

use crate::consensus_layer::height_index::Height;
use crate::consensus_layer::{artifacts::ConsensusMessage, pool_reader::PoolReader};
use crate::crypto::{CryptoHashOf, Hashed, Signed, TurboHash};
use crate::{FinalizationType, HeightMetrics, SubnetParams};
use serde::{Deserialize, Serialize};
use std::collections::BTreeMap;
use std::sync::{Arc, RwLock};

use super::block_maker::Block;
use super::notary::NotarizationShareContent;

// NotarizationContent holds the values that are signed in a notarization
#[derive(Clone, Debug, PartialEq, Eq, PartialOrd, Ord, Hash, Serialize, Deserialize)]
pub struct NotarizationContent {
    pub height: Height,
    pub block: CryptoHashOf<Block>,
}

impl NotarizationContent {
    pub fn new(block_height: Height, block_hash: CryptoHashOf<Block>) -> Self {
        Self {
            height: block_height,
            block: block_hash,
        }
    }
}

impl TurboHash for NotarizationContent {
    fn tubro_hash(&self) -> String {
        format!("NCA{}", self.height)
    }
}

pub type Notarization = Signed<NotarizationContent, u8>;

/// FinalizationContent holds the values that are signed in a finalization
#[derive(Clone, Debug, PartialEq, Eq, PartialOrd, Ord, Hash, Serialize, Deserialize)]
pub struct FinalizationContent {
    pub height: Height,
    pub block: CryptoHashOf<Block>,
}

impl FinalizationContent {
    pub fn new(height: Height, block: CryptoHashOf<Block>) -> Self {
        FinalizationContent { height, block }
    }
}

impl TurboHash for FinalizationContent {
    fn tubro_hash(&self) -> String {
        format!("FCA{}", self.height)
    }
}

/// A finalization is a multi-signature on a FinalizationContent. A finalization
/// proves that the block identified by the block hash in the finalization
/// content (and the block chain it implies) is agreed upon.
pub type Finalization = Signed<FinalizationContent, u8>;

pub struct ShareAggregator {
    node_id: u8,
    subnet_params: SubnetParams,
}

impl ShareAggregator {
    pub fn new(node_id: u8, subnet_params: SubnetParams) -> Self {
        Self {
            node_id,
            subnet_params,
        }
    }

    /// Attempt to construct artifacts from artifact shares in the artifact
    /// pool
    pub fn on_state_change(
        &self,
        pool: &PoolReader<'_>,
        finalization_times: Arc<RwLock<BTreeMap<Height, Option<HeightMetrics>>>>,
    ) -> Vec<ConsensusMessage> {
        // println!("\n########## Aggregator ##########");
        let mut messages = Vec::new();
        messages.append(&mut self.aggregate_notarization_shares(pool, finalization_times.clone()));
        messages.append(&mut self.aggregate_finalization_shares(pool, finalization_times));
        messages
    }

    /// Attempt to construct `Notarization`s at `notarized_height + 1`
    fn aggregate_notarization_shares(
        &self,
        pool: &PoolReader<'_>,
        finalization_times: Arc<RwLock<BTreeMap<Height, Option<HeightMetrics>>>>,
    ) -> Vec<ConsensusMessage> {
        let fin_height = pool.get_finalized_height() + 1;
        let mut stuff = vec![];

        let mut turbo_height = pool.get_notarized_height() + 1;
        while {
            let notarization_shares = pool.get_notarization_shares(turbo_height);
            if notarization_shares.count()
                > ((self.subnet_params.total_nodes_number
                    + self.subnet_params.byzantine_nodes_number)
                    / 2) as usize
            {
                stuff.extend({
                    let notary_content = pool
                        .get_notarization_shares(turbo_height)
                        .next()
                        .unwrap()
                        .content;
                    let notary_content = match notary_content {
                        NotarizationShareContent::COD(notary_content) => NotarizationContent {
                            height: notary_content.height,
                            block: notary_content.block,
                        },
                        NotarizationShareContent::ICC(notary_content) => NotarizationContent {
                            height: notary_content.height,
                            block: notary_content.block,
                        },
                    };
                    Some(ConsensusMessage::Notarization(Notarization {
                        content: NotarizationContent {
                            height: notary_content.height,
                            block: notary_content.block,
                        },
                        signature: 0, // committee signature
                    }))
                });
                turbo_height += 1;
                true
            } else {
                false
            }
        } {}

        if self.subnet_params.fast_internet_computer_consensus {
            for height in fin_height..turbo_height {
                let shares_num = pool.get_notarization_shares(height).count();
                if shares_num
                    >= (self.subnet_params.total_nodes_number
                        - self.subnet_params.disagreeing_nodes_number)
                        as usize
                {
                    let finalization_content = pool.get_block(height).unwrap();
                    if !finalization_times.read().unwrap().contains_key(&height) {
                        let finalization_time = pool.get_finalization_time(height, self.node_id);
                        let height_metrics = HeightMetrics {
                            latency: finalization_time,
                            fp_finalization: FinalizationType::FP,
                        };
                        finalization_times
                            .write()
                            .unwrap()
                            .insert(finalization_content.height, Some(height_metrics));

                        stuff.append(&mut vec![ConsensusMessage::Finalization(Finalization {
                            content: FinalizationContent {
                                height: finalization_content.height,
                                block: CryptoHashOf::new(Hashed::crypto_hash(
                                    &finalization_content,
                                )),
                            },
                            signature: 50, // committee signature
                        })]);
                    };
                }
            }
        }

        stuff
    }

    /// Attempt to construct `Finalization`s
    fn aggregate_finalization_shares(
        &self,
        pool: &PoolReader<'_>,
        finalization_times: Arc<RwLock<BTreeMap<Height, Option<HeightMetrics>>>>,
    ) -> Vec<ConsensusMessage> {
        let mut stuff = vec![];
        for height in pool.get_finalized_height() + 1..=pool.get_notarized_height() {
            let finlization_shares = pool.get_finalization_shares(height, height);
            if finlization_shares.count()
                > ((self.subnet_params.total_nodes_number
                    + self.subnet_params.byzantine_nodes_number)
                    / 2) as usize
            {
                let finalization_content = pool.get_block(height).unwrap();
                if !finalization_times.read().unwrap().contains_key(&height) {
                    let finalization_time =
                        pool.get_finalization_time(finalization_content.height, self.node_id);
                    let height_metrics = HeightMetrics {
                        latency: finalization_time,
                        fp_finalization: FinalizationType::IC,
                    };

                    finalization_times
                        .write()
                        .unwrap()
                        .insert(finalization_content.height, Some(height_metrics));

                    stuff.push(ConsensusMessage::Finalization(Finalization {
                        content: FinalizationContent {
                            height: finalization_content.height,
                            block: CryptoHashOf::new(Hashed::crypto_hash(&finalization_content)),
                        },
                        signature: 50, // committee signature
                    }))
                };
            }
        }
        stuff
    }
}
/*
pub fn aggregate<T: Ord>(
    shares: Box<dyn Iterator<Item = Signed<T, u8>>>,
) -> BTreeMap<T, BTreeSet<u8>> {
    shares.fold(
        BTreeMap::<T, BTreeSet<u8>>::new(),
        |mut grouped_shares, share| {
            match grouped_shares.get_mut(&share.content) {
                Some(existing) => {
                    existing.insert(share.signature);
                }
                None => {
                    let mut new_set = BTreeSet::<u8>::new();
                    new_set.insert(share.signature);
                    grouped_shares.insert(share.content, new_set);
                }
            };
            grouped_shares
        },
    )
}
*/
/*
fn _group_shares_and_acks(
    grouped_shares_separated_from_acks: BTreeMap<NotarizationShareContent, BTreeSet<u8>>,
) -> BTreeMap<NotarizationShareContent, BTreeSet<u8>> {
    // println!("\nGrouped shares separated from acks {:?}", grouped_shares_separated_from_acks);
    // we need to aggregate shares and acks for the same block proposal
    // if there are only acks for a proposal, we might still need to aggregate them into a notarization as
    // the acknowledger might not be able to create an FP-finalization even if it received n-p acks
    // this happens due to rule 2 of CoD which requires the parent of a block to be finalized in order for the block to be FP-finalized
    let grouped_shares_and_acks = grouped_shares_separated_from_acks.iter().fold(
        BTreeMap::<NotarizationShareContent, BTreeSet<u8>>::new(),
        |mut grouped_shares_and_acks, (notary_content, committee)| {
            match notary_content {
                NotarizationShareContent::COD(notary_content) => {
                    // here we only try to notarize blocks, therefore it is not important whether a notarization share is an acknowledgement or not
                    // we group all notarization shares (also acks) in one entry in order to count all the ones received for a block proposal
                    let generic_notary_content =
                        NotarizationShareContent::COD(NotarizationShareContentCOD {
                            is_ack: false, // set "is_ack" to false fopr each entry so that the acks are grouped with the shares for the same proposal
                            ..notary_content.clone()
                        });
                    match grouped_shares_and_acks.get_mut(&generic_notary_content) {
                        Some(grouped_by_proposal) => {
                            for share in committee {
                                grouped_by_proposal.insert(share.to_owned());
                            }
                        }
                        None => {
                            grouped_shares_and_acks
                                .insert(generic_notary_content.clone(), committee.clone());
                        }
                    }
                }
                // if only ICC is used, as there are no acks, there is no need to group them with the shares
                // shares for the same proposal are already aggregated by the "aggregate" function
                NotarizationShareContent::ICC(notary_content) => {
                    grouped_shares_and_acks.insert(
                        NotarizationShareContent::ICC(notary_content.clone()),
                        committee.clone(),
                    );
                }
            }
            grouped_shares_and_acks
        },
    );
    // println!("Grouped shares and acks {:?}", grouped_shares_and_acks);
    grouped_shares_and_acks
}
*/
