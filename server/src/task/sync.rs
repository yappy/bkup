use anyhow::{ensure, Context, Result};
use std::{path::Path, process::Command};

const RCLONE_CMD: &str = "rclone";
const RCLONE_ERROR_HELP: &str = "Cannot execute rclone
[HINT] Download rclone and install:
https://rclone.org/downloads/";

pub fn run(_dry_run: bool, _repo_dir: &Path, _sync_dir: &Path) -> Result<()> {
    check_rclone()?;

    Ok(())
}

fn check_rclone() -> Result<()> {
    let output = Command::new(RCLONE_CMD)
        .arg("version")
        .output()
        .context(RCLONE_ERROR_HELP)?;
    let stdout = String::from_utf8_lossy(&output.stdout);
    let stderr = String::from_utf8_lossy(&output.stderr);
    if !stdout.is_empty() {
        println!("{}", stdout);
    }
    if !stderr.is_empty() {
        println!("{}", stderr);
    }

    ensure!(output.status.success(), "rclone exited with error status");

    Ok(())
}
