use anyhow::Result;
use log::info;

use super::TaskConfig;
use crate::fssys::Repository;

pub fn run(config: &TaskConfig) -> Result<()> {
    info!("[repository] start");

    let _repo = Repository::init(&config.repo_dir)?;

    info!("dry_run {}", config.dry_run);
    info!(
        "{} {} {}",
        config.keep_count, config.keep_days, config.keep_size
    );

    info!("[repository] finish");
    Ok(())
}
