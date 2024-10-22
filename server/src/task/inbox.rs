use std::path::Path;

use anyhow::{Context, Result};
use log::{info, warn};

use super::TaskConfig;
use crate::fssys;

pub fn run(config: &TaskConfig) -> Result<()> {
    let inbox_dir = std::path::absolute(&config.inbox_dir)?;
    let repo_dir = std::path::absolute(&config.repo_dir)?;

    info!("[inbox] scan start: {}", inbox_dir.to_string_lossy());

    let rd = inbox_dir
        .read_dir()
        .with_context(|| format!("cannot read directory: {}", inbox_dir.to_string_lossy()))?;

    // filter by is_file()
    let rd = rd.filter(|sub| {
        sub.as_ref()
            .is_ok_and(|sub| sub.file_type().is_ok_and(|t| t.is_file()))
    });
    for sub in rd {
        if let Err(err) = sub {
            warn!("{err:#}");
            continue;
        }
        let sub = sub.unwrap();

        let path = sub.path();
        let parts = fssys::parse_file_name(&path);
        let Some((name, tag, _date)) = parts else {
            warn!("ignore: {}", path.to_string_lossy());
            continue;
        };
        info!("find: {}", path.to_string_lossy());
        accept_move(config.dry_run, &repo_dir, &path, &name, &tag)?;
    }

    info!("[inbox] scan end: {}", inbox_dir.to_string_lossy());

    Ok(())
}

fn accept_move(dry_run: bool, repo_dir: &Path, src: &Path, name: &str, tag: &str) -> Result<()> {
    // dstdir = repo/tag/
    let dir = repo_dir.join(tag);
    // dstfile = repo/tag/filename
    let dst = dir.join(name);

    info!("mkdir: {}", dir.to_string_lossy());
    if !dry_run {
        std::fs::create_dir_all(&dir)
            .with_context(|| format!("mkdir failed: {}", dir.to_string_lossy()))?;
    } else {
        info!("(dry run)");
    }

    info!(
        "move: {} => {}",
        src.to_string_lossy(),
        dst.to_string_lossy()
    );
    if !dry_run {
        // NOTE: it would be better to check if kind() is ErrorKind::CrossesDevices
        // after stabilized
        if let Err(err) = std::fs::rename(src, &dst) {
            warn!("{err:#}");
            warn!("rename failed, try copy-and-remove");

            std::fs::copy(src, &dst)?;
            std::fs::remove_file(src)?;
        }
    } else {
        info!("(dry run)");
    }

    Ok(())
}
