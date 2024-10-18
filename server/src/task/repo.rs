use anyhow::Result;
use log::info;
use std::path::Path;

use crate::fssys::Repository;

pub fn run(_dry_run: bool, repo_dir: &Path, _sync_dir: &Path) -> Result<()> {
    let _repo = Repository::init(repo_dir)?;

    info!("repo task");

    Ok(())
}
