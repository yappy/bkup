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

pub fn version_vec() -> &'static [String] {
    static VERSION_INFO: LazyLock<Vec<String>> = LazyLock::new(|| {
        vec![
            env!("CARGO_PKG_VERSION").to_string(),
            format!("{GIT_BRANCH} {GIT_DESCRIBE} {GIT_DATE}"),
            format!("Build: {}", build_profile()),
        ]
    });

    &VERSION_INFO
}

#[rustfmt::skip]
pub fn version() -> &'static str {
    static VERSION_INFO: LazyLock<String> = LazyLock::new(|| {
        version_vec().join("\n")
    });

    &VERSION_INFO
}
