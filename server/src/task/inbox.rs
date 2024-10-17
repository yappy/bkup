use anyhow::{Context, Result};
use log::{info, warn};
use regex::Regex;
use std::{path::Path, sync::LazyLock};

const ARCHIVE_EXT: &[&str] = &["zip", "7z", "tar.gz", "tar.bz2", "tar.xz"];
static ARCHIVE_RE: LazyLock<Regex> =
    LazyLock::new(|| Regex::new(r"^(.*?)[\-\_]?(\d{8,})$").unwrap());

pub fn run(_dry_run: bool, inbox_dir: &Path, _repo_dir: &Path) -> Result<()> {
    let inbox_dir = std::path::absolute(inbox_dir)?;

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
            warn!("warning: {err:#}");
            continue;
        }
        let sub = sub?;

        let path = sub.path();
        let parts = parse_file_name(&path);
        let Some((tag, date)) = parts else {
            warn!("ignore: {}", path.to_string_lossy());
            continue;
        };
        info!("find: {}, tag={tag}, date={date}", path.to_string_lossy());
    }

    info!("scan end");

    Ok(())
}

fn parse_file_name<P: AsRef<Path>>(path: P) -> Option<(String, String)> {
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
