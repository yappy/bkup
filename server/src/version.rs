use std::sync::LazyLock;

#[rustfmt::skip] const GIT_BRANCH:    &str = env!("BUILD_GIT_BRANCH");
#[allow(dead_code)]
#[rustfmt::skip] const GIT_HASH:      &str = env!("BUILD_GIT_HASH");
#[rustfmt::skip] const GIT_DESCRIBE:  &str = env!("BUILD_GIT_DESCRIBE");
#[rustfmt::skip] const GIT_DATE:      &str = env!("BUILD_GIT_DATE");
#[rustfmt::skip] const BUILD_DEBUG:   &str = env!("BUILD_CARGO_DEBUG");
#[allow(dead_code)]
#[rustfmt::skip] const BUILD_TARGET:  &str = env!("BUILD_CARGO_TARGET");

pub fn build_profile() -> &'static str {
    if BUILD_DEBUG == "true" {
        "debug"
    } else {
        "release"
    }
}

#[rustfmt::skip]
pub fn version() -> &'static str {
    static VERSION_INFO: LazyLock<String> = LazyLock::new(|| {
        let cv = env!("CARGO_PKG_VERSION");
        let prof = build_profile();

        format!("{cv}
{GIT_BRANCH} {GIT_DESCRIBE} {GIT_DATE}
Build: {prof}"
        )
    });

    &VERSION_INFO
}
