pub mod networking {

    use async_std::{fs::File, prelude::*, task};
    use futures::{channel::mpsc::Sender, prelude::stream::StreamExt, stream::SelectNextSome};
    use libp2p::{
        floodsub::{Floodsub, FloodsubEvent, Topic},
        identity::Keypair,
        mdns::{Mdns, MdnsConfig, MdnsEvent},
        swarm::SwarmEvent,
        Multiaddr, NetworkBehaviour, PeerId, Swarm,
    };

    use crate::consensus_layer::blockchain::{Block, Blockchain, InputPayloads};

    // We create a custom network behaviour that combines floodsub and mDNS.
    // Use the derive to generate delegating NetworkBehaviour impl.
    #[derive(NetworkBehaviour)]
    #[behaviour(out_event = "OutEvent")]
    pub struct P2PBehaviour {
        floodsub: Floodsub,
        mdns: Mdns,
    }

    #[allow(clippy::large_enum_variant)]
    #[derive(Debug)]
    pub enum OutEvent {
        Floodsub(FloodsubEvent),
        Mdns(MdnsEvent),
    }

    impl From<MdnsEvent> for OutEvent {
        fn from(v: MdnsEvent) -> Self {
            Self::Mdns(v)
        }
    }

    impl From<FloodsubEvent> for OutEvent {
        fn from(v: FloodsubEvent) -> Self {
            Self::Floodsub(v)
        }
    }

    pub struct Peer {
        node_number: u8,
        round: usize,
        rank: u8,
        floodsub_topic: Topic,
        swarm: Swarm<P2PBehaviour>,
        blockchain: Blockchain,
    }

    impl Peer {
        pub async fn new(node_number: u8, topic: &str) -> Self {
            let starting_round = 1;
            // Create a random PeerId
            let local_key = Keypair::generate_ed25519();
            let local_peer_id = PeerId::from(local_key.public());

            // Set up an encrypted DNS-enabled TCP Transport
            let transport = libp2p::development_transport(local_key).await.unwrap();

            // Create a Floodsub topic
            let floodsub_topic = Topic::new(topic);

            // Create a Swarm to manage peers and events
            let local_peer = Self {
                node_number,
                round: starting_round,
                rank: (starting_round as u8 + node_number - 2) % 4,
                floodsub_topic: floodsub_topic.clone(),
                swarm: {
                    let mdns = task::block_on(Mdns::new(MdnsConfig::default())).unwrap();
                    let mut behaviour = P2PBehaviour {
                        floodsub: Floodsub::new(local_peer_id),
                        mdns,
                    };

                    behaviour.floodsub.subscribe(floodsub_topic);
                    Swarm::new(transport, behaviour, local_peer_id)
                },
                blockchain: Blockchain::new(),
            };
            println!("Local node initialized with number: {} and peer id: {:?}", local_peer.node_number, local_peer_id);
            println!("Local node has rank: {} in round: {}", local_peer.rank, local_peer.round);
            local_peer
        }

        pub fn listen_for_dialing(&mut self) {
            self.swarm
                .listen_on(
                    "/ip4/0.0.0.0/tcp/0"
                        .parse()
                        .expect("can get a local socket"),
                )
                .expect("swarm can be started");
        }

        pub fn create_block(&mut self, next_proposed_block_height: u32, mut tx: Sender<Block>) {
            // attach new block to last block in vinalized blockchain
            let parent_hash = self
                .blockchain
                .block_tree
                .get_parent_hash(
                    next_proposed_block_height,
                    self.blockchain.finalized_chain_index,
                )
                .expect("can get parent hash");
            println!("Appending block to parent with hash: {}", parent_hash);
            let round = self.round;
            task::spawn(async move {
                // mine block in a separate non-blocking task
                match get_next_block(round, parent_hash, next_proposed_block_height as u64).await
                {
                    Some(block) => tx.try_send(block).expect("can push into channel"), // push block into channel so that it can later be broadcasted
                    None => (),
                };
            });
        }

        pub fn broadcast_block(&mut self, next_proposed_block_height: u32, block: Option<Block>) {
            match block {
                Some(block) => {
                    println!("Sent block with sequence number {}", block.id);
                    self.round += 1; // used to index the next local block to broadcast
                    self.swarm.behaviour_mut().floodsub.publish(
                        self.floodsub_topic.clone(),
                        serde_json::to_string(&block).unwrap(),
                    );
                    self.blockchain.block_tree.create_child_at_height(
                        next_proposed_block_height,
                        self.blockchain.finalized_chain_index,
                        block,
                    )
                }
                None => (),
            }
        }

        pub fn keep_alive(&mut self) {
            self.swarm.behaviour_mut().floodsub.publish(
                self.floodsub_topic.clone(),
                serde_json::to_string("Keep alive!").unwrap(),
            );
        }

        pub fn get_next_event(&mut self) -> SelectNextSome<'_, Swarm<P2PBehaviour>> {
            self.swarm.select_next_some()
        }

        pub fn match_event<T>(&mut self, event: SwarmEvent<OutEvent, T>) {
            match event {
                SwarmEvent::NewListenAddr { address, .. } => {
                    println!("Listening on {:?}", address);
                }
                SwarmEvent::Behaviour(OutEvent::Floodsub(FloodsubEvent::Message(message))) => {
                    let block_content = String::from_utf8_lossy(&message.data);
                    if !block_content.eq("\"Keep alive!\"") {
                        handle_incoming_block(self, &block_content, message.source)
                    } else {
                        // println!("Keep connection alive");
                    }
                }
                SwarmEvent::Behaviour(OutEvent::Mdns(MdnsEvent::Discovered(list))) => {
                    for (peer, _) in list {
                        self.swarm
                            .behaviour_mut()
                            .floodsub
                            .add_node_to_partial_view(peer);
                    }
                }
                SwarmEvent::Behaviour(OutEvent::Mdns(MdnsEvent::Expired(list))) => {
                    for (peer, _) in list {
                        if !self.swarm.behaviour_mut().mdns.has_node(&peer) {
                            self.swarm
                                .behaviour_mut()
                                .floodsub
                                .remove_node_from_partial_view(&peer);
                        }
                    }
                    // println!("Ignoring Mdns expired event");
                }
                _ => {
                    // println!("Unhandled swarm event");
                }
            }
        }
    }

    async fn get_next_block(
        round: usize,   // used to read next payload from local pool
        parent_hash: String,
        local_blockchain_height: u64,
    ) -> Option<Block> {
        match get_next_payload(round).await {
            Some(payload) => {
                // setting block id according to the length of the local blockchain
                let new_block = Block::new(local_blockchain_height, parent_hash, payload);
                Some(new_block)
            }
            None => {
                println!("No more payloads");
                None
            }
        }
    }

    async fn get_next_payload(round: usize) -> Option<String> {
        let input_payloads: InputPayloads = read_file("payloads_pool.txt").await;
        let next_payload = if round < input_payloads.len() {
            Some(input_payloads[round].clone())
        } else {
            None
        };
        next_payload
    }

    async fn read_file(path: &str) -> InputPayloads {
        let mut file = File::open(path).await.expect("txt file in path");
        let mut content = String::new();
        file.read_to_string(&mut content)
            .await
            .expect("read content as string");

        let mut input_payloads: InputPayloads = vec![];
        for line in content.lines() {
            input_payloads.push(String::from(line));
        }
        input_payloads
    }

    pub fn handle_incoming_block(local_peer: &mut Peer, block_content: &str, block_source: PeerId) {
        println!("\nPeer: {} sent block: {}", block_source, block_content);
        let block = serde_json::from_str::<Block>(block_content).expect("can parse block");
        local_peer.blockchain.try_add_block(block);
    }
}
