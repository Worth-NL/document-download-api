# NotifyNL: upstream (alphagov) tests that don't hold for NL are listed in superseded_tests_nl.toml instead of being
# skipped inline, so upstream test files stay identical to alphagov's. This repo has no such tests yet, so there is no
# manifest and the plugin changes nothing about a test run. It's loaded for --nl-verify, which CI runs to fail on any
# inline [NOTIFYNL] skip: add a superseded_tests_nl.toml entry with an NL twin instead. See notifynl-utils'
# notifications_utils/testing_nl/superseded_tests.py for the options
# (--nl-verify, --nl-show-superseded, --nl-run-superseded).
pytest_plugins = ["notifications_utils.testing_nl.superseded_tests"]
