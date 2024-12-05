use anyhow::Result;
use chrono::{DateTime, Local, SecondsFormat};
use clap::{error::ErrorKind, Parser};
use fern::colors::{Color, ColoredLevelConfig};
use log::{error, info, LevelFilter};
use serde::{Deserialize, Serialize};
use task::TaskConfig;

mod fssys;
mod task;
mod version;

#[cfg(debug_assertions)]
const LOG_LEVEL_DEFAULT: LevelFilter = LevelFilter::Trace;
#[cfg(not(debug_assertions))]
const LOG_LEVEL_DEFAULT: LevelFilter = LevelFilter::Info;

/// Backup files maintenance daemon
#[derive(Debug, Parser, Serialize, Deserialize)]
#[command(author,
    long_version = version::version(),
    about, long_about = None)]
struct Args {
    #[arg(long, value_name = "LEVEL", default_value_t = LOG_LEVEL_DEFAULT)]
    log_level: LevelFilter,
    #[arg(long, value_name = "FILE", default_value_t = String::from("bkupsv.log"))]
    log_file: String,

    /// Enable all the tasks
    #[arg(long, short)]
    task_all: bool,
    /// Enable repository clean task
    #[arg(long)]
    task_repo: bool,
    /// Enable inbox > repository move task
    #[arg(long)]
    task_inbox: bool,
    /// Enable sync with cloud storage task
    #[arg(long)]
    task_sync: bool,

    /// Inbox directory path
    #[arg(long, value_name = "DIR", default_value_t = String::from("/tmp/inbox"))]
    inbox_dir: String,
    /// Repository directory path
    #[arg(long, value_name = "DIR", default_value_t = String::from("/tmp/repo"))]
    repo_dir: String,
    /// Cloud sync directory path
    #[arg(long, value_name = "DIR", default_value_t = String::from("/tmp/sync"))]
    sync_dir: String,

    /// repo-task: condition to keep archive files (0 to disable)
    #[arg(long, value_name = "COUNT", default_value_t = 0)]
    keep_count: u32,
    /// repo-task: condition to keep archive files (0 to disable)
    #[arg(long, value_name = "SIZE", default_value_t = String::from("0"))]
    keep_size: String,

    /// sync-task: check rclone update (apt system only)
    #[arg(long)]
    check_rclone_update: bool,
    /// sync-task: (local path if empty)
    #[arg(long, default_value_t = String::new())]
    remote: String,

    /// Dry-run
    #[arg(long, short = 'n')]
    dry_run: bool,
    /// Watch mode
    #[arg(long, short)]
    watch: bool,

    /// Read parameters from TOML file (other command line parameters will be ignored)
    #[arg(long, short, value_name = "FILE", default_value_t = String::new())]
    config_file: String,
    /// Generate a config file template and exit
    #[arg(long, short, value_name = "FILE", default_value_t = String::new())]
    gen_config: String,
}

/// Use system argv.
pub fn run() -> Result<()> {
    let args = help_version_filter(Args::try_parse())?;

    if let Some(args) = args {
        run_internal(args)
    } else {
        Ok(())
    }
}

/// Use &str list. (argv[0] is automatically added)
pub fn run_args(argv1: &[&str]) -> Result<()> {
    let argv0 = &[env!("CARGO_PKG_NAME")];
    let argv: std::iter::Chain<std::slice::Iter<'_, &str>, std::slice::Iter<'_, &str>> =
        argv0.iter().chain(argv1);
    let args = help_version_filter(Args::try_parse_from(argv))?;

    if let Some(args) = args {
        run_internal(args)
    } else {
        Ok(())
    }
}

/// Make clap Display* error Ok(None). (and print Display* error message)
///
/// Ok(Some(args)): parse ok
/// Ok(None): parse ok but should exit (print help/version)
/// Err: parse error
fn help_version_filter(
    parse_res: core::result::Result<Args, clap::error::Error>,
) -> core::result::Result<Option<Args>, clap::error::Error> {
    match parse_res {
        Ok(args) => Ok(Some(args)),
        Err(err) => {
            if matches!(
                err.kind(),
                ErrorKind::DisplayHelp
                    | ErrorKind::DisplayHelpOnMissingArgumentOrSubcommand
                    | ErrorKind::DisplayVersion
            ) {
                print!("{err:#}");
                Ok(None)
            } else {
                Err(err)
            }
        }
    }
}

/// Parse args and call main routines.
fn run_internal(mut args: Args) -> Result<()> {
    // write to a file and exit if --gen-config
    if !args.gen_config.is_empty() {
        let path = args.gen_config;
        args.config_file = String::new();
        args.gen_config = String::new();
        let toml = toml::to_string_pretty(&args)?;

        println!("Generate config file: {}", &path);
        std::fs::write(&path, toml)?;

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
    info!("version info:");
    for line in version::version_vec() {
        info!("{line}");
    }

    let toml = toml::to_string_pretty(&args)?;
    info!("arguments:\n{toml}");

    let remote = if !args.remote.is_empty() {
        format!("{}:", args.remote)
    } else {
        String::new()
    };
    let config = TaskConfig {
        dry_run: args.dry_run,

        enable_repo: args.task_all || args.task_repo,
        enable_inbox: args.task_all || args.task_inbox,
        enable_sync: args.task_all || args.task_sync,

        inbox_dir: args.inbox_dir.into(),
        repo_dir: args.repo_dir.into(),
        sync_dir: args.sync_dir.into(),

        keep_count: args.keep_count,
        keep_size: fssys::parse_size(&args.keep_size)?,

        check_rclone_update: args.check_rclone_update,
        remote,
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

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn run_help() -> Result<()> {
        run_args(&["-h"])?;
        run_args(&["--help"])?;

        Ok(())
    }

    #[test]
    fn run_version() -> Result<()> {
        run_args(&["-V"])?;
        run_args(&["--version"])?;

        Ok(())
    }

    #[test]
    fn test_gen_config() -> Result<()> {
        let dir = tempfile::tempdir()?;
        let path = dir.path().join("config.toml");

        run_args(&["--gen-config", &path.to_string_lossy()])?;

        let meta = std::fs::metadata(path)?;
        assert_ne!(meta.len(), 0);

        Ok(())
    }
}
