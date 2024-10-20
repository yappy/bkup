use anyhow::Result;
use chrono::{DateTime, Local, SecondsFormat};
use clap::Parser;
use fern::colors::{Color, ColoredLevelConfig};
use log::{error, info, LevelFilter};
use serde::{Deserialize, Serialize};
use task::TaskConfig;

mod fssys;
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

    /// repo: condition to keep archive files (0 to disable)
    #[arg(long, default_value_t = 0)]
    keep_count: u32,
    /// repo: condition to keep archive files (0 to disable)
    #[arg(long, default_value_t = String::from("0"))]
    keep_size: String,

    /// Watch mode
    #[arg(long, short)]
    watch: bool,
    /// Dry-run
    #[arg(long, short = 'n')]
    dry_run: bool,

    /// Read parameters from TOML file (other command line parameters will be ignored)
    #[arg(long, short, default_value_t = String::new())]
    config_file: String,
    /// Generate a config file template and exit
    #[arg(long, short)]
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
        let toml = toml::to_string_pretty(&args)?;
        std::fs::write(GEN_CONFIG_PATH, toml)?;
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

    let toml = toml::to_string_pretty(&args)?;
    info!("arguments:\n{toml}");

    let config = TaskConfig {
        dry_run: args.dry_run,

        enable_inbox: true,
        enable_repo: true,
        enable_sync: true,

        inbox_dir: args.inbox_dir.into(),
        repo_dir: args.repo_dir.into(),
        sync_dir: args.sync_dir.into(),

        keep_count: args.keep_count,
        keep_size: fssys::parse_size(&args.keep_size)?,
    };
    let cont = || -> Result<()> {
        if args.watch {
            task::watch(&config)
        } else {
            task::run(&config)
        }
    };

    // catch Error and error!() to logger
    let result = cont();
    if let Err(ref err) = result {
        error!("{err:#}");
    } else {
        info!("exit successfully")
    }

    // return the result as is
    result
}

fn create_fern(color: bool) -> fern::Dispatch {
    let colors = if color {
        Some(
            ColoredLevelConfig::new()
                .info(Color::Green)
                .debug(Color::Magenta)
                .trace(Color::BrightBlue),
        )
    } else {
        None
    };

    fern::Dispatch::new().format(move |out, message, record| {
        let time: DateTime<Local> = Local::now();
        let level = record.level();
        let level = colors.map_or(level.to_string(), |colors| colors.color(level).to_string());
        out.finish(format_args!(
            "{} [{:5}] {}",
            time.to_rfc3339_opts(SecondsFormat::Secs, false),
            level,
            message
        ))
    })
}

fn setup_logger(log_level: LevelFilter, log_file: Option<&str>) -> Result<()> {
    let fern = fern::Dispatch::new();

    // log level
    let fern = fern.level(log_level);

    // output
    let fern = fern.chain(create_fern(true).chain(std::io::stdout()));
    let fern = if let Some(log_file) = log_file {
        fern.chain(create_fern(false).chain(fern::log_file(log_file)?))
    } else {
        fern
    };

    fern.apply()?;
    Ok(())
}

/// Fern setup for test.
///
/// println! with color.
/// Required:
/// cargo test -- --nocapture
#[cfg(test)]
fn setup_test_logger() {
    // std::io::stdout() prints logs even if --nocapture is not passed...
    // let fern = create_fern(true).chain(std::io::stdout());

    let fern = create_fern(true).chain(fern::Output::call(|record| {
        println!("{}", record.args());
    }));

    // ignore error due to duplicated setup
    // (test functions will be executed parallelly)
    let _ = fern.apply();
}
