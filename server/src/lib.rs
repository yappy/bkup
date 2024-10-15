use anyhow::Result;
use clap::Parser;
use serde::{Deserialize, Serialize};

mod task;

const GEN_CONFIG_PATH: &str = "config.toml";

/// Backup files maintenance daemon
#[derive(Debug, Parser, Serialize, Deserialize)]
#[command(author, version, about, long_about = None, arg_required_else_help = true)]
struct Args {
    /// Inbox directory path
    #[arg(short, long, default_value_t = String::new())]
    inbox_dir: String,
    #[arg(long)]
    watch: bool,

    /// Read parameters from TOML file (other command line parameters will be ignored)
    #[arg(long, default_value_t = String::new())]
    config_file: String,
    /// Generate a config file template and exit
    #[arg(long)]
    gen_config: bool,
}

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

    println!("{:?}", args);
    task::watch(&args.inbox_dir)?;

    Ok(())
}
