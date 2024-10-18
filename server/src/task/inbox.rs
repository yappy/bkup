use anyhow::{Context, Result};
use log::{info, warn};
use std::path::Path;

use crate::fssys;

pub fn run(_dry_run: bool, inbox_dir: &Path, repo_dir: &Path) -> Result<()> {
    let inbox_dir = std::path::absolute(inbox_dir)?;
    let _repo_dir = std::path::absolute(repo_dir)?;

    info!("scan start: {}", inbox_dir.to_string_lossy());
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
        let Some((tag, date)) = parts else {
            warn!("ignore: {}", path.to_string_lossy());
            continue;
        };
        info!("find: {}, tag={tag}, date={date}", path.to_string_lossy());
    }

    info!("scan end: {}", inbox_dir.to_string_lossy());

    Ok(())
}
