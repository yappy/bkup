use anyhow::Result;
use log::info;

use super::TaskConfig;
use crate::fssys::{Entry, Repository};

pub fn run(config: &TaskConfig) -> Result<()> {
    info!("[repository] clean start");

    let repo = Repository::init(&config.repo_dir)?;

    for (tag, list) in repo.data.iter() {
        clean_one(config, tag, list)?;
    }

    info!("[repository] clean finish");
    Ok(())
}

fn clean_one(config: &TaskConfig, tag: &str, list: &[Entry]) -> Result<()> {
    info!("clean: {tag}");

    let mut delete_count = 0_usize;

    if config.keep_count != 0 {
        let keep_count = config.keep_count as usize;
        if keep_count < list.len() {
            delete_count = delete_count.max(list.len() - keep_count);
        }
    }

    if config.keep_size != 0 {
        let mut total = list.iter().fold(0, |sum, e| sum + e.size);
        let mut count = 0_usize;
        for e in list.iter() {
            if total <= config.keep_size {
                break;
            }
            assert!(total >= e.size);
            total -= e.size;
            count += 1;
        }
        delete_count = delete_count.max(count);
    }

    let msg = if config.dry_run { "(dry run)" } else { "" };
    for (i, e) in list.iter().enumerate() {
        if i < delete_count {
            info!("DEL : {msg} {}", e.path.to_string_lossy());
            if !config.dry_run {
                std::fs::remove_file(&e.path)?;
            }
        } else {
            info!("KEEP: {}", e.path.to_string_lossy());
        }
    }

    Ok(())
}
