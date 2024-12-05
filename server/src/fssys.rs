// TODO: remove later
#![allow(dead_code)]

use anyhow::{bail, ensure, Context, Result};
use log::{info, warn};
use number_prefix::NumberPrefix;
use regex::Regex;
use std::{
    collections::BTreeMap,
    path::{Path, PathBuf},
    sync::LazyLock,
};

pub struct Repository {
    pub root_dir: PathBuf,
    /// tag => [Entry]
    pub data: BTreeMap<String, Vec<Entry>>,
}

#[derive(Eq, Ord, PartialEq, PartialOrd)]
pub struct Entry {
    /// sorted by dictionary order
    pub date: String,

    pub path: PathBuf,
    pub size: u64,
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

        let mut data = BTreeMap::new();

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

    /// scan dirname and return sorted archive entry list
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
            let Some((_name, tag, date)) = parts else {
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

        // date order
        result.sort();

        Ok(result)
    }
}

pub fn parse_size(s: &str) -> Result<u64> {
    let mut n: u64 = 0;
    let mut cur: Option<u64> = None;

    ensure!(!s.is_empty(), "parse size failed (empty string)");

    for c in s.chars() {
        match c {
            '0'..='9' => {
                let t = c as u64 - '0' as u64;
                let mut tmp = cur.unwrap_or(0);
                tmp = tmp.checked_mul(10).context("overflow")?;
                tmp = tmp.checked_add(t).context("overflow")?;
                cur = Some(tmp);
            }
            'k' | 'K' | 'm' | 'M' | 'g' | 'G' | 't' | 'T' => {
                let factor = match c {
                    'k' | 'K' => 1u64 << 10,
                    'm' | 'M' => 1u64 << 20,
                    'g' | 'G' => 1u64 << 30,
                    't' | 'T' => 1u64 << 40,
                    _ => panic!(),
                };
                let mut tmp = cur.context("parse size failed: {s}")?;
                tmp = tmp.checked_mul(factor).context("overflow")?;
                n = n.checked_add(tmp).context("overflow")?;
                cur = None;
            }
            _ => {
                bail!("parse size failed: {s}");
            }
        }
    }
    n = n.checked_add(cur.unwrap_or(0)).context("overflow")?;

    Ok(n)
}

pub fn auto_scale(size: u64) -> (f64, &'static str) {
    match NumberPrefix::binary(size as f64) {
        NumberPrefix::Standalone(n) => (n, ""),
        NumberPrefix::Prefixed(prefix, n) => (n, prefix.symbol()),
    }
}

/// Get (filename, tag, date) parts from file name.
///
/// If not UTF-8, parse will be failed.
///
/// e.g. "abc-20240101.zip" => ("abc", "20240101")
pub fn parse_file_name<P: AsRef<Path>>(path: P) -> Option<(String, String, String)> {
    const ARCHIVE_EXT: &[&str] = &["zip", "7z", "tar.gz", "tar.bz2", "tar.xz"];
    static ARCHIVE_RE: LazyLock<Regex> =
        LazyLock::new(|| Regex::new(r"^(.*?)[\-\_]?(\d{8,})$").unwrap());

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
        name.to_string(),
        caps.get(1).unwrap().as_str().to_string(),
        caps.get(2).unwrap().as_str().to_string(),
    ))
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_parse_size() -> Result<()> {
        assert_eq!(parse_size(&u64::MIN.to_string())?, u64::MIN);
        assert_eq!(parse_size("12345")?, 12345);
        assert_eq!(parse_size(&u64::MAX.to_string())?, u64::MAX);

        assert_eq!(parse_size("123k")?, 123u64 * 1024);
        assert_eq!(parse_size("123K")?, 123u64 * 1024);
        assert_eq!(parse_size("123m")?, 123u64 * 1024 * 1024);
        assert_eq!(parse_size("123M")?, 123u64 * 1024 * 1024);
        assert_eq!(parse_size("123g")?, 123u64 * 1024 * 1024 * 1024);
        assert_eq!(parse_size("123G")?, 123u64 * 1024 * 1024 * 1024);
        assert_eq!(parse_size("123t")?, 123u64 * 1024 * 1024 * 1024 * 1024);
        assert_eq!(parse_size("123T")?, 123u64 * 1024 * 1024 * 1024 * 1024);

        assert!(parse_size("").is_err());
        assert!(parse_size("k").is_err());
        assert!(parse_size("a").is_err());
        assert!(parse_size(&format!("{}k", u64::MAX)).is_err());

        Ok(())
    }

    #[test]
    fn test_parse_file_name() {
        assert_eq!(parse_file_name("/aaa/bbb/ccc/.hidden.zip"), None);
        assert_eq!(parse_file_name("/aaa/bbb/ccc/abc.txt"), None);
        assert_eq!(
            parse_file_name("/aaa/bbb/ccc/test-20240101.tar.gz"),
            Some((
                "test-20240101.tar.gz".into(),
                "test".into(),
                "20240101".into()
            ))
        );
    }
}
