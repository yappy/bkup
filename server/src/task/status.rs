use std::{ffi::CString, mem::MaybeUninit, os::unix::ffi::OsStrExt, path::Path};

use anyhow::Result;
use log::info;

use crate::fssys;

use super::TaskConfig;

pub fn run(config: &TaskConfig) -> Result<()> {
    info!("[status] start");

    let inbox_dir = std::path::absolute(&config.inbox_dir)?;
    let repo_dir = std::path::absolute(&config.repo_dir)?;
    let sync_dir = std::path::absolute(&config.sync_dir)?;

    status_inbox(&inbox_dir)?;
    status_repo(&repo_dir)?;
    status_sync(&sync_dir)?;

    info!("[status] finish");
    Ok(())
}

fn status_inbox(path: &Path) -> Result<()> {
    info!("inbox: {}", path.to_string_lossy());
    report_disk_usage(path)?;

    Ok(())
}

fn status_repo(path: &Path) -> Result<()> {
    info!("repo: {}", path.to_string_lossy());
    report_disk_usage(path)?;

    Ok(())
}

fn status_sync(path: &Path) -> Result<()> {
    info!("sync: {}", path.to_string_lossy());
    report_disk_usage(path)?;

    Ok(())
}

fn report_disk_usage(path: &Path) -> Result<()> {
    let stat = statvfs(path)?;

    let total = stat.f_blocks * stat.f_frsize;
    let avail = stat.f_bavail * stat.f_frsize;
    let avail_rate = avail as f64 / total as f64;
    let total = fssys::auto_scale(total);
    let avail = fssys::auto_scale(avail);

    info!(
        "{:4.1} {}B / {:4.1} {}B ({:.1}%) free",
        avail.0,
        avail.1,
        total.0,
        total.1,
        avail_rate * 100.0
    );

    Ok(())
}

/// <https://stackoverflow.com/questions/54823541/what-do-f-bsize-and-f-frsize-in-struct-statvfs-stand-for>
fn statvfs(path: impl AsRef<Path>) -> Result<libc::statvfs> {
    let path = path.as_ref();

    let c_path = CString::new(path.as_os_str().as_bytes()).unwrap();
    let mut c_statvfs = MaybeUninit::<libc::statvfs>::uninit();
    let statvfs = unsafe {
        let ret = libc::statvfs(c_path.as_ptr(), c_statvfs.as_mut_ptr());
        if ret == 0 {
            Ok(c_statvfs.assume_init())
        } else {
            Err(std::io::Error::last_os_error())
        }
    };

    Ok(statvfs?)
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_statvfs() -> Result<()> {
        let statvfs = statvfs(".")?;
        assert_ne!(statvfs.f_bfree, 0);
        assert_ne!(statvfs.f_bsize, 0);
        assert_ne!(statvfs.f_frsize, 0);
        // true in almost cases
        assert_eq!(statvfs.f_bsize, statvfs.f_frsize);

        Ok(())
    }

    #[test]
    fn test_statvfs_enoent() {
        let res = statvfs("/invalid/dir/path");
        assert!(res.is_err());
        if let Err(err) = res {
            let err: std::io::Error = err.downcast().unwrap();
            assert_eq!(err.kind(), std::io::ErrorKind::NotFound);
        }
    }
}
