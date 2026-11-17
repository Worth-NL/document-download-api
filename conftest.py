# NotifyNL: upstream (alphagov) tests that don't hold for NL are listed in superseded_tests_nl.toml instead of being
# skipped inline, so upstream test files stay identical to alphagov's. CI runs --nl-verify, which fails on a stale
# manifest entry, a missing NL replacement or any inline [NOTIFYNL] skip. See notifynl-utils'
# notifications_utils/testing_nl/superseded_tests.py for the options
# (--nl-verify, --nl-show-superseded, --nl-run-superseded).
pytest_plugins = ["notifications_utils.testing_nl.superseded_tests"]
