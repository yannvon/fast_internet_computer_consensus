use serde::{Deserialize, Serialize};

use crate::{
    consensus_layer::{artifacts::ConsensusMessage, height_index::Height, pool_reader::PoolReader},
    crypto::{CryptoHashOf, TurboHash},
    time_source::Time,
    SubnetParams,
};

use super::block_maker::{Block, BlockProposal};

#[derive(Clone, Debug, PartialEq, Eq, PartialOrd, Ord, Hash, Serialize, Deserialize)]
pub struct GoodnessArtifact {
    pub children_height: Height,
    pub most_acks_child: String,
    pub most_acks_child_count: usize,
    total_acks_for_children: usize,
    pub all_children_good: bool,
    pub timestamp: Time,
}

impl TurboHash for GoodnessArtifact {
    fn tubro_hash(&self) -> String {
        format!(
            "Good{}.{}",
            self.children_height, self.total_acks_for_children
        )
    }
}

#[derive(Clone, Debug, PartialEq, Eq, PartialOrd, Ord, Hash, Serialize, Deserialize)]
pub struct IMadeABlockArtifact {
    pub block_height: Height,
    pub maker_time: Time,
    pub my_id: u8,
}

impl TurboHash for IMadeABlockArtifact {
    fn tubro_hash(&self) -> String {
        format!("imab{}", self.block_height)
    }
}

pub struct Goodifier {
    _node_id: u8,
    _subnet_params: SubnetParams,
}

impl Goodifier {
    pub fn new(_node_id: u8, _subnet_params: SubnetParams) -> Self {
        Self {
            _node_id,
            _subnet_params,
        }
    }

    pub fn on_state_change(&self, _pool: &PoolReader<'_>) -> Vec<ConsensusMessage> {
        vec![] /*
               // println!("\n########## Goodifier ##########");
               let notarized_height = pool.get_notarized_height();
               let finalized_height = pool.get_finalized_height();
               // heights before the last finalized block do not need to be checked
               // check heights in which it is still possible for a goodness artifact to be updated
               (finalized_height..=notarized_height + 1)
                   .filter_map(|h| {
                       let consensus_messages_at_height = self.goodify_height(pool, h);
                       match consensus_messages_at_height.len() {
                           0 => None,
                           _ => Some(consensus_messages_at_height),
                       }
                   })
                   .flatten()
                   .collect()*/
    }
    /*
        fn goodify_height(&self, pool: &PoolReader<'_>, h: Height) -> Vec<ConsensusMessage> {
            // group acks according to the parent of the block they are acknowledging
            // then for each parent group, group acks according to the block they are acknowledging
            let grouped_acks = pool.get_notarization_shares(h).fold(
                BTreeMap::<String, BTreeMap<String, BTreeSet<u8>>>::new(),
                // NEW RULES: also terrible code. Don't group by parent, get all height.
                |mut grouped_acks_by_parent, signed_share| {
                    if let NotarizationShareContent::COD(notarization_share) = signed_share.content {
                        if notarization_share.is_ack {
                            let ack = notarization_share;
                            let signature = signed_share.signature;
                            match grouped_acks_by_parent.get_mut(&"same parent hash lol".to_string()) {
                                Some(existing_parent_map) => {
                                    match existing_parent_map.get_mut(ack.block.get_ref()) {
                                        Some(existing_block_set) => {
                                            existing_block_set.insert(signature);
                                        }
                                        None => {
                                            let mut block_set = BTreeSet::<u8>::new();
                                            let block_hash = ack.block.get_ref().clone();
                                            block_set.insert(signature);
                                            existing_parent_map.insert(block_hash, block_set);
                                        }
                                    }
                                }
                                None => {
                                    let mut grouped_acks_by_block =
                                        BTreeMap::<String, BTreeSet<u8>>::new();
                                    let mut block_set = BTreeSet::<u8>::new();
                                    let block_hash = ack.block.get_ref().clone();
                                    let block_parent_hash = "same parent hash lol".to_string();
                                    block_set.insert(signature);
                                    grouped_acks_by_block.insert(block_hash, block_set);
                                    grouped_acks_by_parent
                                        .insert(block_parent_hash, grouped_acks_by_block);
                                }
                            };
                        }
                    } else {
                        panic!("goodifier called while running original IC consensus");
                    }
                    grouped_acks_by_parent
                },
            );
            // println!("Grouped acks {:?}", grouped_acks);

            grouped_acks.into_iter().fold(
                Vec::new(),
                |mut goodness_consensus_messages_at_height, (_parent_hash, grouped_acks_by_block)| {
                    // initialize "goodness" artifact for a particular parent
                    let mut children_goodness_artifact = GoodnessArtifact {
                        children_height: h,
                        most_acks_child: String::from(""),
                        most_acks_child_count: 0,
                        total_acks_for_children: 0,
                        all_children_good: false,
                        timestamp: self.time_source.get_relative_time(),
                    };

                    // count total number of acks on children and determine which child is the one with the most acks
                    for (block_hash, acks_for_block) in grouped_acks_by_block {
                        let acks_for_current_block_count = acks_for_block.len();
                        if acks_for_current_block_count
                            > children_goodness_artifact.most_acks_child_count
                        {
                            children_goodness_artifact.most_acks_child = block_hash.clone();
                            children_goodness_artifact.most_acks_child_count =
                                acks_for_current_block_count;
                        }
                        children_goodness_artifact.total_acks_for_children +=
                            acks_for_current_block_count;
                    }

                    // for each parent, check conditions to determine which children are "good"
                    match pool.get_latest_goodness_artifact_for_parent(h) {
                        // if "goodness" artifact does not exist, we check whether it can be created according to currently received acks
                        None => {
                            if children_goodness_artifact.total_acks_for_children
                                - children_goodness_artifact.most_acks_child_count
                                > (self.subnet_params.byzantine_nodes_number
                                    + self.subnet_params.disagreeing_nodes_number)
                                    as usize
                            {
                                // println!("\nAll children of: {} at height: {} are good", children_goodness_artifact.parent_hash, h);
                                children_goodness_artifact.all_children_good = true;
                                goodness_consensus_messages_at_height.push(
                                    ConsensusMessage::GoodnessArtifact(children_goodness_artifact),
                                );
                            } else if children_goodness_artifact.most_acks_child_count
                                > (self.subnet_params.disagreeing_nodes_number
                                    + self.subnet_params.byzantine_nodes_number)
                                    as usize
                            {
                                // println!("\nFor parent: {} at height: {}, the good child with most acks is: {} and received: {} acks out of: {}", children_goodness_artifact.parent_hash, children_goodness_artifact.children_height-1, children_goodness_artifact.most_acks_child, children_goodness_artifact.most_acks_child_count, children_goodness_artifact.total_acks_for_children);
                                goodness_consensus_messages_at_height.push(
                                    ConsensusMessage::GoodnessArtifact(children_goodness_artifact),
                                );
                            }
                        }
                        // if the "goodness" artifact already exists, we must check whether it should be updated
                        Some(previous_goodness_artifact) => {
                            // if all children are "good", the "goodness" artifact for this parent does not have to be updated as all children will remain "good"
                            // and in this case we do not care about which one is the one with the most acks
                            if !previous_goodness_artifact.all_children_good {
                                // if all children become "good" we create an updated "goodness" artifact
                                if children_goodness_artifact.total_acks_for_children
                                    - children_goodness_artifact.most_acks_child_count
                                    > (self.subnet_params.byzantine_nodes_number
                                        + self.subnet_params.disagreeing_nodes_number)
                                        as usize
                                {
                                    // println!("\nAll children of: {} at height: {} are good", children_goodness_artifact.parent_hash, h);
                                    children_goodness_artifact.all_children_good = true;
                                    goodness_consensus_messages_at_height.push(
                                        ConsensusMessage::GoodnessArtifact(children_goodness_artifact),
                                    );
                                }
                            }
                        }
                    };

                    goodness_consensus_messages_at_height
                },
            )
        }
    }*/
}

pub fn _get_block_by_hash_and_height(
    pool: &PoolReader<'_>,
    hash: &CryptoHashOf<Block>,
    h: Height,
) -> Option<Block> {
    // return a valid block with the matching hash and height if it exists.
    let mut blocks: Vec<BlockProposal> = pool
        .pool()
        .validated()
        .block_proposal()
        .get_by_height(h)
        .filter(|x| x.content.get_hash() == hash.get_ref())
        .collect();
    match blocks.len() {
        1 => Some(blocks.remove(0).content.value),
        _ => None,
    }
}

pub fn _block_is_good(_pool: &PoolReader<'_>, _block: &Block) -> bool {
    true /*
         // block is one of the children for the latest "goodness" artifact
         // pool.print_goodness_artifacts_at_height(block.height);
         match pool.get_latest_goodness_artifact_for_parent(block.height) {
             Some(goodness_artifact) => {
                 // println!("\nLatest goodness artifact {:?}", goodness_artifact);
                 if goodness_artifact.all_children_good {
                     return true;
                 }
                 let block_hash = Hashed::crypto_hash(&block);
                 // println!("Block to be checked: {}", block_hash);
                 goodness_artifact.most_acks_child == block_hash
             }
             None => {
                 if block.height == 0 {
                     return true; // genesis is good
                 }
                 false
             }
         }*/
}
