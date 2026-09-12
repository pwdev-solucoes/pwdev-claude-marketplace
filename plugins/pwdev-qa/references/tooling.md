# QA tooling catalog

This is a recommendation catalog, not an installer. Match observed context against the
rules, preserve detection evidence, and keep unsupported or unprobed facts explicit.
Each supplied probe carries `state`, `result`, and `evidence`. `available` means the
tool probe and all purpose-specific required probes are positive. `missing` means the
tool probe explicitly reported the tool absent. `unverified` means a probe was absent,
not run, or a prerequisite was not established. Tool availability alone does not prove
that browsers, drivers, SDKs, devices, credentials, services, or authorization are
ready. Never turn an absent inventory key into fabricated negative evidence.

## Recommendation rules

| tool | surface | platform | tool probe | required probes | purpose | prerequisites | alternative | reason |
|---|---|---|---|---|---|---|---|---|
| playwright-cli | web | any | playwright-cli | playwright-cli,node,browser | Exploratory Web/UI navigation, observed-ref actions, snapshots, and screenshots in a task-owned session | Node.js 18+ compatibility: https://github.com/microsoft/playwright-cli (checked 2026-09-12); isolated qa-report session; browser access; screenshot review; version, cost, and license unverified | Manual browser exploration with timestamped notes and reviewed screenshots | Fast interactive investigation with concise observed page state; it does not replace a repeatable suite |
| Playwright Test | web | any | playwright-test | playwright-test,browsers | Repeatable suite execution across configured browsers and CI | Project dependency and browser binaries; CI compatibility: https://playwright.dev/docs/ci (checked 2026-09-12); version, cost, and license unverified | Existing repository Web/UI test runner | Deterministic assertions, retries, projects, and CI execution belong in the test suite |
| Appium UiAutomator2 | mobile | android | appium | appium,uiautomator2-driver,android-sdk,adb,android-device | Android native, hybrid, or Web UI automation through the UiAutomator2 driver | Android modes compatibility: https://appium.io/docs/en/latest/intro/drivers/ (checked 2026-09-12); Android SDK, ADB, device or emulator, and configured UiAutomator2 driver; version, cost, and license unverified | AndroidX Test or an authorized manual device run | Appium lists UiAutomator2 for Android native, hybrid, and Web modes |
| Appium XCUITest | mobile | ios | appium | appium,xcuitest-driver,macos,xcode,ios-device | iOS native, hybrid, or Web UI automation through the XCUITest driver | iOS technology compatibility: https://appium.io/docs/en/latest/intro/drivers/ (checked 2026-09-12); macOS, Xcode, device or simulator, and configured XCUITest driver; version, cost, and license unverified | XCUITest in the existing Apple project or an authorized manual device run | Appium maps its iOS driver to Apple XCUITest technology |

## Broader surface guide

Use repository-native tooling first. The examples below are candidates only: their
availability, versions, costs, licenses, credentials, and platform constraints remain
`unverified` until checked for the actual environment.

| surface | candidate purpose | example candidates | minimum context |
|---|---|---|---|
| Web/UI | browser behavior and visual interaction | existing browser suite; Playwright Test; playwright-cli for exploration | browsers, runtime, CI, data constraints |
| API | contract, authentication, authorization, errors, and idempotency | existing integration tests; curl; project HTTP client | schema, endpoint, credentials, safe target |
| mobile | Android or iOS behavior on compatible devices | Appium driver; platform-native test framework | target platform, host OS, SDK, device |
| data | integrity, transactions, and reconciliation | repository test client; read-only database client | engine, schema, safe dataset, permissions |
| accessibility | semantic and keyboard behavior plus assistive-technology review | existing accessibility checks; platform inspector; manual review | standard, browser/device, real component behavior |
| performance | agreed workload, profile, percentiles, and thresholds | existing benchmark runner; k6; JMeter | authorization, environment, limits, test data |
| security | authorized, reproducible security checks | existing SAST/DAST tooling; manual threat review | written scope, authorization, data handling |
| automation/CI | isolation, deterministic runs, flaky-test handling, artifacts, and gates | existing CI runner; Playwright Test for Web suites | CI provider, commands, secrets policy, artifact policy |
| observability | logs, metrics, traces, incidents, and preventive regression evidence | existing platform dashboards and query tools | authorized environment, time window, redaction policy |
| export | validate offline HTML and A4 PDF outputs | repository Python tests; pypdf; pdfplumber | Python runtime, pinned project dependencies, safe fixtures |

## Current-claim verification ledger

Only rows marked `verified` may support a current compatibility statement. No version,
cost, or license recommendation was verified for this task, so those facts must remain
`unverified` in recommendations.

| tool | claim | status | official source | checked at |
|---|---|---|---|---|
| playwright-cli | compatibility | verified | https://github.com/microsoft/playwright-cli | 2026-09-12 |
| Playwright Test | compatibility | verified | https://playwright.dev/docs/ci | 2026-09-12 |
| Appium UiAutomator2 | compatibility | verified | https://appium.io/docs/en/latest/intro/drivers/ | 2026-09-12 |
| Appium XCUITest | compatibility | verified | https://appium.io/docs/en/latest/intro/drivers/ | 2026-09-12 |
| playwright-cli | version | unverified | unverified | unverified |
| playwright-cli | cost | unverified | unverified | unverified |
| playwright-cli | license | unverified | unverified | unverified |
| Playwright Test | version | unverified | unverified | unverified |
| Playwright Test | cost | unverified | unverified | unverified |
| Playwright Test | license | unverified | unverified | unverified |
| Appium drivers | version | unverified | unverified | unverified |
| Appium drivers | cost | unverified | unverified | unverified |
| Appium drivers | license | unverified | unverified | unverified |

## Evidence boundaries

For exploratory `playwright-cli` work, create a dedicated `qa-report` session, obtain a
fresh snapshot before acting on refs, and close only that session. A snapshot is text,
not proof of pixels or semantics. A screenshot needs recorded visual sanitization
review before attachment. Do not attach traces or videos in v1. Never reuse a personal
browser profile or export its cookies/storage.

For every candidate, the final recommendation table still has exactly
`tool/purpose/availability/evidence/prerequisites/alternative/reason`. Record an absent
CLI as `missing` only after an explicit negative tool probe. With no probe, record
`unverified` and `probe <name> -> not provided`; never install or fabricate execution
evidence. Verified current claims carry their official URL and check date in the final
`prerequisites` cell; unverified version, cost, and license facts are labeled there too.
