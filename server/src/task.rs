use std::path::PathBuf;

use anyhow::Result;

mod inbox;
mod sync;
mod watch;

pub struct TaskConfig {
    pub dry_run: bool,

    pub enable_inbox: bool,
    pub enable_sync: bool,

    pub inbox_dir: PathBuf,
    pub repo_dir: PathBuf,
    pub sync_dir: PathBuf,
}

pub fn run(config: &TaskConfig) -> Result<()> {
    if config.enable_inbox {
        inbox::run(config.dry_run, &config.inbox_dir, &config.repo_dir)?;
    }
    if config.enable_sync {
        sync::run(config.dry_run, &config.repo_dir, &config.sync_dir)?;
    }

    Ok(())
}

/// Watch config.inbox_dir and call [run]
pub fn watch(config: &TaskConfig) -> Result<()> {
    watch::watch(&config.inbox_dir, || run(config))
}
