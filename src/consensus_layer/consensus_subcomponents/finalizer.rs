use std::cell::RefCell;

use serde::{Deserialize, Serialize};

use crate::{
    consensus_layer::{artifacts::ConsensusMessage, height_index::Height, pool_reader::PoolReader},
    crypto::{CryptoHashOf, Hashed, Signed},
    SubnetParams,
};

use super::block_maker::Block;

/// FinalizationShareContent holds the values that are signed in a finalization share
#[derive(Clone, Debug, PartialEq, Eq, PartialOrd, Ord, Hash, Serialize, Deserialize)]
pub struct FinalizationShareContent {
    pub height: Height,
    pub block: CryptoHashOf<Block>,
}

impl FinalizationShareContent {
    pub fn new(height: Height, block: CryptoHashOf<Block>) -> Self {
        FinalizationShareContent { height, block }
    }
}

/// A finalization share is a multi-signature share on a finalization content.
/// If sufficiently many replicas create finalization shares, the shares can be
/// aggregated into a full finalization.
pub type FinalizationShare = Signed<FinalizationShareContent, u8>;

pub struct Finalizer {
    node_id: u8,
    _subnet_params: SubnetParams,
    _prev_finalized_height: RefCell<Height>,
}

impl Finalizer {
    #[allow(clippy::too_many_arguments)]
    pub fn new(node_id: u8, subnet_params: SubnetParams) -> Self {
        Self {
            node_id,
            _subnet_params: subnet_params,
            _prev_finalized_height: RefCell::new(0),
        }
    }

    /// Attempt to:
    /// * deliver finalized blocks (as `Batch`s) via `Messaging`
    /// * publish finalization shares for relevant rounds
    pub fn on_state_change(&self, pool: &PoolReader<'_>) -> Vec<ConsensusMessage> {
        // println!("\n########## Finalizer ##########");
        let notarized_height = pool.get_notarized_height();
        let finalized_height = pool.get_finalized_height();
        let mut stuff = vec![];
        for height in finalized_height + 1..=notarized_height {
            if !pool
                .get_finalization_shares(height, height)
                .any(|share| share.signature == 50 + self.node_id)
            {
                let content = FinalizationShareContent::new(
                    height,
                    CryptoHashOf::new(Hashed::crypto_hash(
                        &pool.get_notarized_blocks(height).next().unwrap(),
                    )),
                );
                let signature = 50 + self.node_id;

                stuff.push(ConsensusMessage::FinalizationShare(FinalizationShare {
                    content,
                    signature,
                }));
            }
        }

        stuff
    }
}
