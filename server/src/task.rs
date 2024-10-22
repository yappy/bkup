use std::{fs::Permissions, os::unix::fs::PermissionsExt, path::PathBuf};

use anyhow::Result;
use log::{info, warn};

mod inbox;
mod repo;
mod sync;
mod watch;

#[derive(Default)]
pub struct TaskConfig {
    pub dry_run: bool,

    pub enable_repo: bool,
    pub enable_inbox: bool,
    pub enable_sync: bool,

    pub inbox_dir: PathBuf,
    pub repo_dir: PathBuf,
    pub sync_dir: PathBuf,

    pub keep_count: u32,
    pub keep_size: u64,
}

pub fn run(config: &TaskConfig) -> Result<()> {
    prepair(config)?;

    let mut any = false;
    if config.enable_repo {
        any = true;
        repo::run(config)?;
    }
    if config.enable_inbox {
        any = true;
        inbox::run(config)?;
    }
    if config.enable_sync {
        any = true;
        sync::run(config)?;
    }

    if !any {
        warn!("No tasks were executed");
        warn!("Enable --task-* option");
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
    info!("chmod 770: {}", config.inbox_dir.to_string_lossy());
    std::fs::set_permissions(&config.inbox_dir, Permissions::from_mode(0o770))?;

    info!("mkdir: {}", config.repo_dir.to_string_lossy());
    std::fs::create_dir_all(&config.repo_dir)?;
    info!("chmod 700: {}", config.repo_dir.to_string_lossy());
    std::fs::set_permissions(&config.repo_dir, Permissions::from_mode(0o700))?;

    info!("mkdir: {}", config.sync_dir.to_string_lossy());
    std::fs::create_dir_all(&config.sync_dir)?;
    info!("chmod 700: {}", config.sync_dir.to_string_lossy());
    std::fs::set_permissions(&config.sync_dir, Permissions::from_mode(0o700))?;

    Ok(())
}
