use anyhow::Result;
use clap::Parser;
use serde::{Deserialize, Serialize};
use task::TaskConfig;

mod task;

const GEN_CONFIG_PATH: &str = "config.toml";

/// Backup files maintenance daemon
#[derive(Debug, Parser, Serialize, Deserialize)]
#[command(author, version, about, long_about = None, arg_required_else_help = true)]
struct Args {
    /// Inbox directory path
    #[arg(long, default_value_t = String::new())]
    inbox_dir: String,
    /// Repository directory path
    #[arg(long, default_value_t = String::new())]
    repo_dir: String,
    /// Cloud sync directory path
    #[arg(long, default_value_t = String::new())]
    sync_dir: String,
    /// Watch mode
    #[arg(long, short)]
    watch: bool,
    /// Dry-run
    #[arg(long, short = 'n')]
    dry_run: bool,

    /// Read parameters from TOML file (other command line parameters will be ignored)
    #[arg(long, default_value_t = String::new())]
    config_file: String,
    /// Generate a config file template and exit
    #[arg(long)]
    gen_config: bool,
}

/// Parse args and call main routines.
pub fn run() -> Result<()> {
    let mut args = Args::try_parse()?;

    // write to a file and exit if --gen-config
    if args.gen_config {
        println!("Generate config file: {GEN_CONFIG_PATH}");
        args.config_file = "".to_string();
        args.gen_config = false;
        let src = toml::to_string_pretty(&args)?;
        std::fs::write(GEN_CONFIG_PATH, src)?;
        return Ok(());
    }

    // replace args with toml if --config-file
    if !args.config_file.is_empty() {
        let src = std::fs::read_to_string(args.config_file)?;
        args = toml::from_str(&src)?;
    }

    let config = TaskConfig {
        dry_run: args.dry_run,

        enable_inbox: true,
        enable_sync: true,

        inbox_dir: args.inbox_dir.into(),
        repo_dir: args.repo_dir.into(),
        sync_dir: args.sync_dir.into(),
    };

    if args.watch {
        task::watch(&config)
    } else {
        task::run(&config)
    }
}
