use anyhow::{bail, ensure, Context, Result};
use log::{error, info, warn};
use serde::{Deserialize, Serialize};
use std::{
    mem,
    process::{Command, Output},
};
use tempfile::TempDir;

use super::TaskConfig;
use crate::fssys;

const RCLONE_CMD: &str = "rclone";
const RCLONE_HINT: &str = "[HINT] Download rclone and install: https://rclone.org/downloads/";

/// rclone about --json remote:
#[derive(Debug, Clone, Copy, Serialize, Deserialize)]
struct StorageUsage {
    total: u64,
    used: u64,
    free: u64,
}

/// rclone about --json remote:
#[derive(Debug, Clone, Serialize, Deserialize, Hash)]
#[serde(rename_all = "PascalCase")]
struct FileEntry {
    path: String,
    name: String,
    size: u64,
    // MimeType
    // ModTime
    is_dir: bool,
    #[serde(rename = "ID")]
    id: String,
}

pub fn run(config: &TaskConfig) -> Result<()> {
    info!("[sync] start");

    check_rclone(config.check_rclone_update)?;
    if !config.remote.is_empty() {
        get_storage_usage(&config.remote)?;
        let files = ls(&config.remote)?;
        let dirc = files.iter().filter(|f| f.is_dir).count();
        let filec = files.len() - dirc;
        info!("Dirs: {dirc}, Files: {filec}");
    } else {
        warn!("--remote is not specified");
    }

    info!("[sync] end");

    Ok(())
}

/// Return (stdout, stderr) if succeeded.
/// Return error if exit status is not 0.
fn execute(command: &mut Command) -> Result<(String, String)> {
    let program = command.get_program().to_string_lossy().to_string();
    let output = execute_internal(command)?;

    match output.status.code() {
        Some(code) => {
            if output.status.success() {
                info!("{program} exited with status: {code}");
            } else {
                error!("{program} exited with status: {code}");
            }
        }
        None => error!("{program} terminated by signal"),
    }

    let stdout = String::from_utf8_lossy(&output.stdout);
    let stderr = String::from_utf8_lossy(&output.stderr);

    if !output.status.success() {
        if !stdout.is_empty() {
            info!("stdout\n{}", stdout);
        }
        if !stderr.is_empty() {
            info!("stderr\n{}", stderr);
        }
        bail!("{program} exited with error status");
    }

    Ok((stdout.to_string(), stderr.to_string()))
}

fn execute_internal(command: &mut Command) -> Result<Output> {
    let program = command.get_program().to_string_lossy().to_string();

    let mut cmdline = String::new();
    cmdline.push_str(&program);
    for arg in command.get_args() {
        cmdline.push(' ');
        cmdline.push_str(&arg.to_string_lossy());
    }

    info!("EXEC: {cmdline}");
    let output = command
        .output()
        .with_context(|| format!("Cannot execute {program}"))?;

    Ok(output)
}

fn check_rclone(check_update: bool) -> Result<()> {
    info!("rclone command check start");
    info!("{RCLONE_HINT}");

    let (stdout, _) = execute(Command::new(RCLONE_CMD).arg("version"))?;

    let mut it = stdout.split_whitespace();
    let name = it.next().context("rclone version parse error")?;
    let ver = it.next().context("rclone version parse error")?;
    info!("rclone command check OK ({name} {ver})");

    if check_update {
        check_rclone_update(ver)?;
    }

    Ok(())
}

fn check_rclone_update(ver: &str) -> Result<()> {
    let os = match std::env::consts::OS {
        "linux" => "linux",
        _ => bail!("This check is Linux only"),
    };
    let arch = match std::env::consts::ARCH {
        "x86_64" => "amd64",
        "x86" => "386",
        "aarch64" => "arm64",
        "arm" => "arm-v7",
        _ => bail!(""),
    };

    let deb_file = format!("rclone-current-{os}-{arch}.deb");
    let url = format!("https://downloads.rclone.org/{}", deb_file);

    let dir = TempDir::new()?;
    let dir_path = dir.path();
    let file_path = dir_path.join(deb_file);
    info!("Download: {url}");
    info!("To: {}", dir_path.to_string_lossy());

    execute(Command::new("wget").args(["-q", "-P", dir_path.to_str().unwrap(), &url]))?;
    let (stdout, _) = execute(Command::new("dpkg-deb").args(["-W", file_path.to_str().unwrap()]))?;

    let mut it = stdout.split_whitespace();
    let _pkg_name = it.next().context("dpkg-deb version parse error")?;
    let pkg_ver = it.next().context("dpkg-deb version parse error")?;
    let pkg_ver = format!("v{pkg_ver}");

    if ver != pkg_ver {
        warn!("Newer package is found: {pkg_ver} (current: {ver})");
        warn!(
            "Install command: apt install {}",
            file_path.to_string_lossy()
        );
        // Don't remove dir
        mem::forget(dir);
    } else {
        info!("No update: {pkg_ver}");
    }

    Ok(())
}

fn get_storage_usage(remote: &str) -> Result<()> {
    ensure!(!remote.is_empty(), "--remote required");

    let (stdout, _) = execute(Command::new("rclone").args(["about", "--json", remote]))?;
    let stat: StorageUsage = serde_json::from_str(&stdout)?;

    let total = fssys::auto_scale(stat.total);
    let free = fssys::auto_scale(stat.free);
    let free_rate = stat.free as f64 / stat.total as f64;

    info!(
        "{:4.1} {}B / {:4.1} {}B ({:.1}%) free",
        free.0,
        free.1,
        total.0,
        total.1,
        free_rate * 100.0
    );

    Ok(())
}

fn ls(remote: &str) -> Result<Vec<FileEntry>> {
    ensure!(!remote.is_empty(), "--remote required");

    let (stdout, _) = execute(Command::new("rclone").args([
        "lsjson",
        "-R",
        "--fast-list",
        "--no-mimetype",
        "--no-modtime",
        remote,
    ]))?;
    let result = serde_json::from_str(&stdout)?;

    Ok(result)
}
