use anyhow::{ensure, Context, Result};
use const_format::formatcp;
use log::{error, info, warn};
use std::{mem, process::Command};
use tempfile::TempDir;

use super::TaskConfig;

const RCLONE_CMD: &str = "rclone";
const RCLONE_HINT: &str = "[HINT] Download rclone and install: https://rclone.org/downloads/";

pub fn run(config: &TaskConfig) -> Result<()> {
    info!("[sync] start");

    check_rclone(config.check_rclone_update)?;

    info!("[sync] end");

    Ok(())
}

fn execute(command: &mut Command) -> Result<(String, String)> {
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

    let stdout = String::from_utf8_lossy(&output.stdout);
    let stderr = String::from_utf8_lossy(&output.stderr);
    if !stdout.is_empty() {
        info!("stdout\n{}", stdout);
    }
    if !stderr.is_empty() {
        info!("stderr\n{}", stderr);
    }

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
    ensure!(
        output.status.success(),
        "{program} exited with error status"
    );

    Ok((stdout.to_string(), stderr.to_string()))
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
    const DEB_FILE: &str = "rclone-current-linux-amd64.deb";
    const URL: &str = formatcp!("https://downloads.rclone.org/{}", DEB_FILE);

    let dir = TempDir::new()?;
    let dir_path = dir.path();
    let file_path = dir_path.join(DEB_FILE);
    info!("Download: {URL}");
    info!("To: {}", dir_path.to_string_lossy());

    execute(Command::new("wget").args(["-q", "-P", dir_path.to_str().unwrap(), URL]))?;
    let (stdout, _) = execute(Command::new("dpkg-deb").args(["-W", file_path.to_str().unwrap()]))?;

    let mut it = stdout.split_whitespace();
    let _pkg_name = it.next().context("dpkg-deb version parse error")?;
    let pkg_ver = it.next().context("dpkg-deb version parse error")?;
    let pkg_ver = format!("v{pkg_ver}");

    if ver != pkg_ver {
        warn!("Newer package is found: {pkg_ver} (current: {ver})");
        warn!("Install command: apt install {}", file_path.to_string_lossy());
        // Don't remove dir
        mem::forget(dir);
    } else {
        info!("No update: {pkg_ver}");
    }

    Ok(())
}
