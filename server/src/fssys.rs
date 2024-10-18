// TODO: remove later
#![allow(dead_code)]

use anyhow::{Context, Result};
use log::{info, warn};
use regex::Regex;
use std::{
    collections::HashMap,
    path::{Path, PathBuf},
    sync::LazyLock,
};

pub struct Repository {
    root_dir: PathBuf,
    /// tag => [Entry]
    data: HashMap<String, Vec<Entry>>,
}

struct Entry {
    /// sorted by this
    date: String,
    path: PathBuf,
    size: u64,
}

impl Repository {
    pub fn init<P: AsRef<Path>>(root_dir: P) -> Result<Self> {
        let root_dir = std::path::absolute(root_dir)?;

        Self::scan_root(root_dir.as_ref())
    }

    fn scan_root(root_dir: &Path) -> Result<Self> {
        info!("scan start: {}", root_dir.to_string_lossy());

        let rd = root_dir
            .read_dir()
            .with_context(|| format!("cannot read directory: {}", root_dir.to_string_lossy()))?;

        let mut data = HashMap::new();

        for sub in rd {
            if let Err(err) = sub {
                warn!("{err:#}");
                continue;
            }
            let sub = sub.unwrap();
            let ftype = sub.file_type().with_context(|| {
                format!("failed to get file type: {}", sub.path().to_string_lossy())
            });
            if let Err(err) = ftype {
                warn!("{err:#}");
                continue;
            }
            // directory only
            if !ftype.unwrap().is_dir() {
                warn!("not a directory: {}", sub.path().to_string_lossy());
                continue;
            }

            let name = sub.file_name();
            let name = if let Some(name) = name.to_str() {
                name
            } else {
                warn!("invalid name: {}", sub.file_name().to_string_lossy());
                continue;
            };

            let path = sub.path();
            let list = Self::scan_sub(&path, name);
            if let Err(err) = list {
                warn!("{err:#}");
                continue;
            }
            let old = data.insert(name.to_string(), list.unwrap());
            assert!(old.is_none());

            info!("scan end: {}", root_dir.to_string_lossy());
        }

        let root_dir = root_dir.into();
        Ok(Self { root_dir, data })
    }

    fn scan_sub(dir: &Path, dirname: &str) -> Result<Vec<Entry>> {
        info!("scan start: {}", dir.to_string_lossy());

        let mut result = Vec::new();

        let rd = dir
            .read_dir()
            .with_context(|| format!("cannot read directory: {}", dir.to_string_lossy()))?;

        for sub in rd {
            if let Err(err) = sub {
                warn!("{err:#}");
                continue;
            }
            let sub = sub.unwrap();
            let path = sub.path();

            let ftype = sub
                .file_type()
                .with_context(|| format!("failed to get file type: {}", path.to_string_lossy()));
            if let Err(err) = ftype {
                warn!("{err:#}");
                continue;
            }
            // file only
            if !ftype.unwrap().is_file() {
                warn!("not a file: {}", path.to_string_lossy());
                continue;
            }

            let parts = parse_file_name(&path);
            // cannot parse
            let Some((tag, date)) = parts else {
                warn!("ignore: {}", path.to_string_lossy());
                continue;
            };
            // tag mismatch with dirname
            if tag != dirname {
                warn!("ignore: {}", path.to_string_lossy());
                continue;
            }

            let size = if let Ok(meta) = std::fs::metadata(&path) {
                meta.len()
            } else {
                warn!("failed to get file size: {}", path.to_string_lossy());
                continue;
            };

            info!("find: {}, tag={tag}, date={date}", path.to_string_lossy());
            result.push(Entry { date, path, size });
        }

        info!("scan end");

        Ok(result)
    }
}

const ARCHIVE_EXT: &[&str] = &["zip", "7z", "tar.gz", "tar.bz2", "tar.xz"];
static ARCHIVE_RE: LazyLock<Regex> =
    LazyLock::new(|| Regex::new(r"^(.*?)[\-\_]?(\d{8,})$").unwrap());

pub fn parse_file_name<P: AsRef<Path>>(path: P) -> Option<(String, String)> {
    // get filename as utf-8
    // return None if failed
    let name = path.as_ref().file_name()?.to_str()?;
    // split at the first "."
    let (body, ext) = name.split_once('.')?;

    // ignore hidden file
    if body.is_empty() {
        return None;
    }
    // check the ext
    if !ARCHIVE_EXT.iter().any(|&e| e == ext) {
        return None;
    }
    // RE match
    let caps = ARCHIVE_RE.captures(body)?;
    Some((
        caps.get(1).unwrap().as_str().to_string(),
        caps.get(2).unwrap().as_str().to_string(),
    ))
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_parse_file_name() {
        assert_eq!(parse_file_name("/aaa/bbb/ccc/.hidden.zip"), None);
        assert_eq!(parse_file_name("/aaa/bbb/ccc/abc.txt"), None);
        assert_eq!(
            parse_file_name("/aaa/bbb/ccc/test-20240101.tar.gz"),
            Some(("test".into(), "20240101".into()))
        );
    }
}
