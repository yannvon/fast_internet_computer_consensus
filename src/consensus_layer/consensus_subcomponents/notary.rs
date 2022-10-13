use crate::consensus_layer::{pool_reader::PoolReader};

pub struct NotarizationShare {}

pub struct Notary {
    time: u64,
}

impl Notary {
    pub fn new() -> Self {
        Self {
            time: 0,
        }
    }

    pub fn on_state_change(&self, pool: &PoolReader<'_>) -> Vec<NotarizationShare> {
        vec![]
    }
}