use anyhow::{bail, Result};
use log::{debug, info, warn};
use notify::{
    event::{AccessKind, AccessMode, ModifyKind},
    Event, EventKind, Watcher,
};
use std::{path::Path, thread, time::Duration};

fn filter_event(res: notify::Result<Event>) -> bool {
    match res {
        Ok(ev) => match ev.kind {
            EventKind::Access(AccessKind::Close(mode)) => {
                if matches!(mode, AccessMode::Write) {
                    // access - close_write
                    return true;
                }
            }
            EventKind::Modify(ModifyKind::Name(_mode)) => {
                // modify - rename
                return true;
            }
            _ => {}
        },
        Err(err) => {
            warn!("{err:#}");
        }
    }

    false
}

pub fn watch<P: AsRef<Path>, F: Fn() -> Result<()>>(path: P, func: F) -> Result<()> {
    if !path.as_ref().is_dir() {
        bail!("\"{}\" is not a directory", path.as_ref().to_string_lossy());
    }

    let (tx, rx) = std::sync::mpsc::channel();

    let mut watcher = notify::recommended_watcher(move |res| {
        // this handler will be called on another thread
        debug!("{:?}", res);
        tx.send(res).unwrap();
    })?;

    watcher.watch(path.as_ref(), notify::RecursiveMode::NonRecursive)?;
    info!("watching: {}", path.as_ref().to_string_lossy());

    loop {
        let mut need = false;

        // wait and recv
        let res1 = rx.recv().unwrap();
        need |= filter_event(res1);
        // wait for 100 ms to gather events
        thread::sleep(Duration::from_millis(100));
        // consume all the available events without blocking
        for res2 in rx.try_iter() {
            need |= filter_event(res2);
        }

        if need {
            info!("Do something!");
            // TODO continue even if error?
            func()?;
        }
    }

    //watcher.unwatch(path.as_ref())?;

    //Ok(())
}
