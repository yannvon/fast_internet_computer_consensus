use std::time::Duration;

use serde::{Deserialize, Serialize};

use crate::{
    consensus_layer::{artifacts::ConsensusMessage, height_index::Height, pool_reader::PoolReader},
    crypto::{CryptoHashOf, Hashed, Signed, TurboHash},
    SubnetParams,
};

use super::block_maker::{Block, BlockProposal};

#[derive(Clone, Debug, PartialEq, Eq, PartialOrd, Ord, Hash, Serialize, Deserialize)]
pub enum NotarizationShareContent {
    COD(NotarizationShareContentCOD), // content of notarization share when Consensus on Demand is used
    ICC(NotarizationShareContentICC), // content of notarization share when only Internet Computer Consensus is used
}

impl TurboHash for NotarizationShareContent {
    fn tubro_hash(&self) -> String {
        match self {
            Self::COD(stuf) => {
                format!("NShCOD{}.{}", stuf.height, stuf.is_ack,)
            }
            Self::ICC(stuf) => {
                format!("NShICC{}", stuf.height,)
            }
        }
    }
}

// NotarizationShareContentICC holds the values that are signed in a notarization share when only IC Consensus is used
#[derive(Clone, Debug, PartialEq, Eq, PartialOrd, Ord, Hash, Serialize, Deserialize)]
pub struct NotarizationShareContentICC {
    pub height: u64,
    pub block: CryptoHashOf<Block>,
}

impl NotarizationShareContentICC {
    pub fn new(
        block_height: Height,
        block_hash: CryptoHashOf<Block>,
        _is_ack: Option<bool>,
    ) -> Self {
        Self {
            height: block_height,
            block: block_hash,
        }
    }
}

// NotarizationShareContentCOD holds the values that are signed in a notarization share when Consensus on Demand is used
#[derive(Clone, Debug, PartialEq, Eq, PartialOrd, Ord, Hash, Serialize, Deserialize)]
pub struct NotarizationShareContentCOD {
    pub height: u64,
    pub block: CryptoHashOf<Block>,
    pub block_parent_hash: String,
    pub is_ack: bool,
}

impl NotarizationShareContentCOD {
    pub fn new(
        block_height: Height,
        block_hash: CryptoHashOf<Block>,
        block_parent_hash: String,
        is_ack: Option<bool>,
    ) -> Self {
        Self {
            height: block_height,
            block: block_hash,
            block_parent_hash,
            is_ack: is_ack.unwrap(),
        }
    }
}

/// A notarization share is a multi-signature share on a notarization content.
/// If sufficiently many replicas create notarization shares, the shares can be
/// aggregated into a full notarization.
pub type NotarizationShare = Signed<NotarizationShareContent, u8>;

pub struct Notary {
    node_id: u8,
    subnet_params: SubnetParams,
}

impl Notary {
    pub fn new(node_id: u8, subnet_params: SubnetParams) -> Self {
        Self {
            node_id,
            subnet_params,
        }
    }

    pub fn on_state_change(&self, pool: &PoolReader<'_>) -> Vec<ConsensusMessage> {
        // println!("\n########## Notary ##########");
        let notarized_height = pool.get_notarized_height();
        let mut notarization_shares = Vec::new();
        let height = notarized_height + 1;
        // CoD implementation change: cannot use find_lowest_ranked_proposals.
        // in case there is only one 'good' block, it might not be the one with the lowest rank
        // therefore, we consider all proposals
        for proposal in get_proposals(pool, height) {
            let _rank = proposal.content.value.rank;
            /*if self.time_to_notarize(pool, height, rank)
            &&*/
            if !self.is_proposal_already_notarized_by_me(pool, &proposal) {
                if let Some(s) = self.notarize_block(pool, proposal) {
                    // println!(
                    //     "\nCreated notarization share: {:?} for proposal of rank: {:?}",
                    //     s, rank
                    // );
                    notarization_shares.push(ConsensusMessage::NotarizationShare(s));
                }
            }
        }
        notarization_shares
    }

    /// Return the time since round start, if it is greater than required
    /// notarization delay for the given block rank, or None otherwise.
    /*fn _time_to_notarize(&self, pool: &PoolReader<'_>, height: Height, rank: u8) -> bool {
        let adjusted_notary_delay =
            get_adjusted_notary_delay(pool, height, rank, self.subnet_params.artifact_delay);
        if let Some(start_time) = pool.get_round_start_time(height) {
            let now = self._time_source.get_relative_time();
            return now >= start_time + adjusted_notary_delay;
        }
        height == 1
    }*/

    /// Return true if this node has already published a notarization share
    /// for the given block proposal. Return false otherwise.
    fn is_proposal_already_notarized_by_me(
        &self,
        pool: &PoolReader<'_>,
        proposal: &BlockProposal,
    ) -> bool {
        let height = proposal.content.value.height;
        pool.get_notarization_shares(height)
            .filter(|s| s.signature == self.node_id)
            .any(|s| match s.content {
                NotarizationShareContent::COD(share_content) => {
                    proposal.content.hash.eq(share_content.block.get_ref())
                }
                NotarizationShareContent::ICC(share_content) => {
                    proposal.content.hash.eq(share_content.block.get_ref())
                }
            })
    }

    /// Notarize and return a `NotarizationShare` for the given block
    fn notarize_block(
        &self,
        _pool: &PoolReader<'_>,
        proposal: Signed<Hashed<Block>, u8>,
    ) -> Option<NotarizationShare> {
        let _height = proposal.content.value.height;
        let content: NotarizationShareContent = {
            if self.subnet_params.fast_internet_computer_consensus {
                // CoD rule 1: first child of each block is acknowledged
                let is_ack = true;
                /*pool
                .get_notarization_shares(height)
                .filter(|s| s.signature == self.node_id) // filter out shares not sent by local replica */
                /* NEW RULES: first block per height
                .filter(|s| {
                    if let NotarizationShareContent::COD(notarization_share_content_cod) = &s.content {
                        notarization_share_content_cod.block_parent_hash == proposal.content.value.parent   // filter out shares for blocks that do not have the same parent of the block being proposed
                    }
                    else {
                        panic!("no notarization shares of ICC variant when fast_internet_computer_consensus parameter is true");
                    }
                })*/
                //.count()
                //== 0; // set 'is_ack' to true if 'proposal' is the first child of its parent for which the local replica creates a notarization share, the latter is also an acknowledgement
                NotarizationShareContent::COD(NotarizationShareContentCOD::new(
                    proposal.content.value.height,
                    CryptoHashOf::from(proposal.content.hash),
                    proposal.content.value.parent,
                    Some(is_ack),
                ))
            } else {
                NotarizationShareContent::ICC(NotarizationShareContentICC::new(
                    proposal.content.value.height,
                    CryptoHashOf::from(proposal.content.hash),
                    None,
                ))
            }
        };
        let signature = self.node_id;
        Some(NotarizationShare { content, signature })
    }
}

fn get_proposals(pool: &PoolReader<'_>, h: Height) -> Vec<BlockProposal> {
    pool.pool()
        .validated()
        .block_proposal()
        .get_by_height(h)
        .collect()
}

/// Return the validated block proposals with the lowest rank at height `h`, if
/// there are any. Else return `None`.
/*
fn find_lowest_ranked_proposals(pool: &PoolReader<'_>, h: Height) -> Vec<BlockProposal> {
    let (_, best_proposals) = pool
        .pool()
        .validated()
        .block_proposal()
        .get_by_height(h)
        .fold(
            (None, Vec::new()),
            |(mut best_rank, mut best_proposals), proposal| {
                if best_rank.is_none() || best_rank.unwrap() > proposal.content.value.rank {
                    best_rank = Some(proposal.content.value.rank);
                    best_proposals = vec![proposal];
                } else if Some(proposal.content.value.rank) == best_rank {
                    best_proposals.push(proposal);
                }
                (best_rank, best_proposals)
            },
        );
    best_proposals
}
*/

/// Calculate the required delay for notary based on the rank of block to
/// notarize, adjusted by a multiplier depending the gap between finalized and
/// notarized heights, by how far the certified height lags behind the finalized
/// height, and by how far we have advanced beyond a summary block without
/// creating a CUP.

pub fn get_adjusted_notary_delay(
    pool: &PoolReader<'_>,
    _height: Height,
    rank: u8,
    notarization_delay: u64,
) -> Duration {
    // We adjust regular delay based on the gap between finalization and
    // notarization to make it exponentially longer to keep the gap from growing too
    // big. This is because increasing delay leads to higher chance of notarizing
    // only 1 block, which leads to higher chance of getting a finalization for that
    // round.  This exponential backoff does not apply to block rank 0.
    let finalized_height = pool.get_finalized_height();
    let ranked_delay = notarization_delay as f32 * rank as f32;
    let finality_gap = (pool.get_notarized_height() - finalized_height) as i32;
    let finality_adjusted_delay = (ranked_delay * 1.5_f32.powi(finality_gap)) as u64;
    Duration::from_millis(finality_adjusted_delay)
}
