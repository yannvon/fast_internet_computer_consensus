use serde::{Deserialize, Serialize};

use crate::{
    consensus_layer::{
        artifacts::ConsensusMessage, consensus_subcomponents::goodifier::IMadeABlockArtifact,
        height_index::Height, pool_reader::PoolReader,
    },
    crypto::{Hashed, Signed, TurboHash},
    time_source::system_time_now,
    SubnetParams,
};

#[derive(Clone, Debug, Eq, PartialEq, Ord, PartialOrd, Hash, Serialize, Deserialize)]
pub struct Payload {
    //#[serde(with = "serde_bytes")]
    pl: String,
}

/*impl Default for Payload {
    fn default() -> Self {
        Self::new()
    }
}*/

impl Payload {
    pub fn new(size: usize) -> Self {
        Self {
            pl: "a".repeat(size),
        }
    }
}

// Block is the type that is used to create blocks out of which we build a
// block chain
#[derive(Clone, Debug, PartialEq, Eq, Hash, Serialize, Deserialize, PartialOrd, Ord)]
pub struct Block {
    // the parent block that this block extends, forming a block chain
    pub parent: String,
    // the payload of the block
    pub payload: Payload,
    // the height of the block, which is the height of the parent + 1
    pub height: u64,
    // rank indicates the rank of the block maker that created this block
    pub rank: u8,
}

impl Block {
    // Create a new block
    pub fn new(parent: String, payload: Payload, height: u64, rank: u8) -> Self {
        Block {
            parent,
            payload,
            height,
            rank,
        }
    }
}

impl TurboHash for Block {
    fn tubro_hash(&self) -> String {
        format!("block{}", self.height)
    }
}

/// HashedBlock contains a Block together with its hash
pub type HashedBlock = Hashed<Block>;

pub type BlockProposal = Signed<HashedBlock, u8>;

pub struct RandomBeacon {}

pub struct BlockMaker {
    node_id: u8,
    subnet_params: SubnetParams,
}

impl BlockMaker {
    pub fn new(node_id: u8, subnet_params: SubnetParams) -> Self {
        Self {
            node_id,
            subnet_params,
        }
    }

    pub fn on_state_change(&self, pool: &PoolReader<'_>) -> Vec<ConsensusMessage> {
        // println!("\n########## Block maker ##########");
        let my_node_id = self.node_id;
        let (beacon, parent) =
            get_dependencies(pool, self.subnet_params.fast_internet_computer_consensus).unwrap();
        let height: u64 = parent.height + 1;
        let rank = self.get_block_maker_rank(height, &beacon, my_node_id);

        if !already_proposed(pool, height, my_node_id)
            && !self.is_better_block_proposal_available(pool, height, rank)
            && is_time_to_make_block(
                pool,
                height,
                rank,
                my_node_id,
                self.subnet_params.artifact_delay,
            )
        {
            let block_proposal = self
                .propose_block(pool, rank, parent)
                .map(ConsensusMessage::BlockProposal);
            println!("\nCreated block proposal: {:?}", block_proposal);
            if block_proposal.is_some() {
                let block_proposed_artifact = IMadeABlockArtifact {
                    block_height: height,
                    maker_time: system_time_now(),
                    my_id: self.node_id,
                };
                vec![
                    block_proposal.unwrap(),
                    ConsensusMessage::IMadeABlockArtifact(block_proposed_artifact),
                ]
            } else {
                vec![]
            }
        } else {
            vec![]
        }
    }

    fn get_block_maker_rank(&self, height: u64, _beacon: &RandomBeacon, my_node_id: u8) -> u8 {
        //let rank =
        ((height + my_node_id as u64 - 2) % self.subnet_params.total_nodes_number as u64) as u8
        // println!("Local rank for height {} is: {}", height, rank);
        //rank
    }

    /// Return true if the validated pool contains a better (lower ranked) block
    /// proposal than the given rank, for the given height.
    fn is_better_block_proposal_available(
        &self,
        pool: &PoolReader<'_>,
        height: Height,
        rank: u8,
    ) -> bool {
        if let Some(block) = find_lowest_ranked_proposals(pool, height).first() {
            return block.content.value.rank < rank;
        }
        false
    }

    // Construct a block proposal
    fn propose_block(
        &self,
        _pool: &PoolReader<'_>,
        rank: u8,
        parent: Block,
    ) -> Option<BlockProposal> {
        let parent_hash = Hashed::crypto_hash(&parent);
        let height: u64 = parent.height + 1;
        self.construct_block_proposal(parent_hash, height, rank)
    }

    // Construct a block proposal with specified validation context, parent
    // block, rank, and batch payload. This function completes the block by
    // adding a DKG payload and signs the block to obtain a block proposal.
    #[allow(clippy::too_many_arguments)]
    fn construct_block_proposal(
        &self,
        parent_hash: String,
        height: u64,
        rank: u8,
    ) -> Option<BlockProposal> {
        let payload = Payload::new(self.subnet_params.blocksize);
        let block = Block::new(parent_hash, payload, height, rank);
        Some(BlockProposal {
            signature: self.node_id,
            content: Hashed::new(block),
        })
    }
}

// Return the parent random beacon and block of the latest round for which
// this node might propose a block.
// Return None otherwise.
fn get_dependencies(
    pool: &PoolReader<'_>,
    _is_fast_internet_computer_consensus: bool,
) -> Option<(RandomBeacon, Block)> {
    let notarized_height = pool.get_notarized_height();
    // println!("Last block notarized at height: {}", notarized_height);
    // the only "good" block might not be the rank 0 block
    // therefore, we must first filter out the notarized blocks that are not "good"
    // and then choose the one with the smallest rank among the "good" ones
    let parent = pool
        .get_notarized_blocks(notarized_height)
        .min_by(|block1, block2| block1.rank.cmp(&block2.rank));
    match parent {
        Some(parent) => {
            // println!("Parent block: {:?}", parent);
            Some((RandomBeacon {}, parent))
        }
        None => Some((
            RandomBeacon {},
            Block {
                parent: String::from("block-1"),
                payload: Payload::new(3),
                height: 0,
                rank: 0,
            },
        )),
    }
}

// Return true if this node has already made a proposal at the given height.
fn already_proposed(pool: &PoolReader<'_>, h: u64, this_node: u8) -> bool {
    pool.pool()
        .validated()
        .block_proposal()
        .get_by_height(h)
        .any(|p| p.signature == this_node)
}

// Return true if the time since round start is greater than the required block
// maker delay for the given rank.
fn is_time_to_make_block(
    _pool: &PoolReader<'_>,
    _height: u64,
    rank: u8,
    _node_id: u8,
    _proposer_delay: u64,
) -> bool {
    rank == 0
    /*
    let block_maker_delay = get_block_maker_delay(rank, proposer_delay);
    let just_make_sure_omg = Duration::from_secs(60);
    match pool.get_round_start_time(height) {
        Some(start_time) => {
            let current_time = time_source.get_relative_time();
            if current_time + just_make_sure_omg >= start_time + block_maker_delay {
                return true;
            }
            false
        }
        None => {
            // if there is no previous notarization, node 1 proposes the first block (has rank 0 in the first round)
            if node_id == 1 && rank == 0 {
                return true;
            }
            false
        }
    }*/
}

/// Calculate the required delay for block making based on the block maker's
/// rank.
/*fn get_block_maker_delay(rank: u8, proposer_delay: u64) -> Duration {
    if rank == 0 {
        Duration::from_millis(0)
    } else {
        (Duration::from_millis(proposer_delay) * rank as u32) + Duration::from_secs(60)
    }
}*/

/// Return the validated block proposals with the lowest rank at height `h`, if
/// there are any. Else return `None`.
pub fn find_lowest_ranked_proposals(pool: &PoolReader<'_>, h: Height) -> Vec<BlockProposal> {
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
