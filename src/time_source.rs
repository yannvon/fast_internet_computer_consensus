use serde::{Deserialize, Serialize};
//use std::sync::RwLock;
use std::time::Duration;
use std::time::SystemTime;

/// Time since UNIX_EPOCH (in nanoseconds). Just like 'std::time::Instant' or
/// 'std::time::SystemTime', [Time] does not implement the [Default] trait.
#[derive(Clone, Copy, PartialEq, Eq, PartialOrd, Ord, Debug, Hash, Serialize, Deserialize)]
pub struct Time(pub u64);

impl Time {
    /// A private function to cast from [Duration] to [Time].
    pub fn from_duration(t: Duration) -> Self {
        Time(t.as_nanos() as u64)
    }
}
impl std::ops::Add<Duration> for Time {
    type Output = Time;
    fn add(self, dur: Duration) -> Time {
        Time::from_duration(Duration::from_nanos(self.0) + dur)
    }
}

impl std::ops::Sub<Time> for Time {
    type Output = std::time::Duration;

    fn sub(self, other: Time) -> std::time::Duration {
        let lhs = Duration::from_nanos(self.0);
        let rhs = Duration::from_nanos(other.0);
        lhs - rhs
    }
}

/// The unix epoch.
pub const UNIX_EPOCH: Time = Time(0);

/// Return the current system time. Note that the value returned is not
/// guaranteed to be monotonic.
pub fn system_time_now() -> Time {
    UNIX_EPOCH
        + SystemTime::now()
            .duration_since(SystemTime::UNIX_EPOCH)
            .expect("SystemTime is before UNIX EPOCH!")
}

pub fn get_absolute_end_time(starting_time: Time, relative_duration: Duration) -> Time {
    starting_time + relative_duration
}
