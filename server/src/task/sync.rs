use anyhow::{ensure, Context, Result};
use log::info;
use std::process::Command;

use super::TaskConfig;

const RCLONE_CMD: &str = "rclone";
const RCLONE_HINT: &str = "[HINT] Download rclone and install: https://rclone.org/downloads/";

pub fn run(_config: &TaskConfig) -> Result<()> {
    check_rclone()?;

    Ok(())
}

fn check_rclone() -> Result<()> {
    info!("rclone command check start");

    let output = Command::new(RCLONE_CMD)
        .arg("version")
        .output()
        .with_context(|| format!("Cannot execute rclone\n{RCLONE_HINT}"))?;
    info!("{RCLONE_HINT}");
    let stdout = String::from_utf8_lossy(&output.stdout);
    let stderr = String::from_utf8_lossy(&output.stderr);
    if !stdout.is_empty() {
        info!("stdout\n{}", stdout);
    }
    if !stderr.is_empty() {
        info!("stderr\n{}", stderr);
    }

    ensure!(output.status.success(), "rclone exited with error status");
    info!("rclone command check OK");

    Ok(())
}
