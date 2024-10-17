use anyhow::Result;
use chrono::{DateTime, Local, SecondsFormat};
use clap::Parser;
use fern::{
    colors::{Color, ColoredLevelConfig},
    FormatCallback,
};
use log::{error, info, LevelFilter, Record};
use serde::{Deserialize, Serialize};
use task::TaskConfig;

mod task;

#[cfg(debug_assertions)]
const LOG_LEVEL_DEFAULT: LevelFilter = LevelFilter::Trace;
#[cfg(not(debug_assertions))]
const LOG_LEVEL_DEFAULT: LevelFilter = LevelFilter::Info;
const GEN_CONFIG_PATH: &str = "config.toml";

/// Backup files maintenance daemon
#[derive(Debug, Parser, Serialize, Deserialize)]
#[command(author, version, about, long_about = None)]
struct Args {
    #[arg(long, default_value_t = LOG_LEVEL_DEFAULT)]
    log_level: LevelFilter,
    #[arg(long, default_value_t = String::from("bkupsv.log"))]
    log_file: String,

    /// Inbox directory path
    #[arg(long, default_value_t = String::from("/tmp/inbox"))]
    inbox_dir: String,
    /// Repository directory path
    #[arg(long, default_value_t = String::from("/tmp/repo"))]
    repo_dir: String,
    /// Cloud sync directory path
    #[arg(long, default_value_t = String::from("/tmp/sync"))]
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

    // setup logger
    let log_file = if !args.log_file.is_empty() {
        Some(args.log_file.as_str())
    } else {
        None
    };
    setup_logger(args.log_level, log_file)?;
    info!("log setup OK");
    if let Some(log_file) = log_file {
        info!("log file: {log_file}");
    } else {
        info!("log file: disabled");
    };

    // catch Error and error!() to logger
    let cont = || -> Result<()> {
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
    };

    let result = cont();
    if let Err(ref err) = result {
        error!("{err:#}");
    } else {
        info!("exit successfully")
    }

    // return the result as is
    result
}

fn setup_logger(log_level: LevelFilter, log_file: Option<&str>) -> Result<()> {
    let colors = ColoredLevelConfig::new()
        .info(Color::Green)
        .debug(Color::Magenta)
        .trace(Color::BrightBlue);

    let fern = fern::Dispatch::new();

    // log level
    let fern = fern.level(log_level);

    // output
    let fern = fern.chain(
        fern::Dispatch::new()
            .format(move |out, message, record| {
                let time: DateTime<Local> = Local::now();
                out.finish(format_args!(
                    "{} [{:5}] {}",
                    time.to_rfc3339_opts(SecondsFormat::Secs, false),
                    colors.color(record.level()),
                    message
                ))
            })
            .chain(std::io::stdout()),
    );
    let fern = if let Some(log_file) = log_file {
        fern.chain(
            fern::Dispatch::new()
                .format(move |out: FormatCallback, message, record: &Record| {
                    let time: DateTime<Local> = Local::now();
                    out.finish(format_args!(
                        "{} [{:5}] {}",
                        time.to_rfc3339_opts(SecondsFormat::Secs, false),
                        record.level(),
                        message
                    ))
                })
                .chain(fern::log_file(log_file)?),
        )
    } else {
        fern
    };

    fern.apply()?;
    Ok(())
}
