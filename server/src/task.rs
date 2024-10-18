use std::path::PathBuf;

use anyhow::Result;
use log::info;

mod inbox;
mod repo;
mod sync;
mod watch;

pub struct TaskConfig {
    pub dry_run: bool,

    pub enable_repo: bool,
    pub enable_inbox: bool,
    pub enable_sync: bool,

    pub inbox_dir: PathBuf,
    pub repo_dir: PathBuf,
    pub sync_dir: PathBuf,

    pub keep_count: u32,
    pub keep_days: u32,
    pub keep_size: u64,
}

pub fn run(config: &TaskConfig) -> Result<()> {
    prepair(config)?;

    if config.enable_repo {
        repo::run(config)?;
    }
    if config.enable_inbox {
        inbox::run(config)?;
    }
    if config.enable_sync {
        sync::run(config)?;
    }

    Ok(())
}

/// Watch config.inbox_dir and call [run]
pub fn watch(config: &TaskConfig) -> Result<()> {
    watch::watch(&config.inbox_dir, || run(config))
}

fn prepair(config: &TaskConfig) -> Result<()> {
    info!("mkdir: {}", config.inbox_dir.to_string_lossy());
    std::fs::create_dir_all(&config.inbox_dir)?;
    info!("mkdir: {}", config.repo_dir.to_string_lossy());
    std::fs::create_dir_all(&config.repo_dir)?;
    info!("mkdir: {}", config.sync_dir.to_string_lossy());
    std::fs::create_dir_all(&config.sync_dir)?;

    Ok(())
}
