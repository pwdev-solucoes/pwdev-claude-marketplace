---
name: qa-specialist-mobile
description: Design platform-specific Android and iOS checks with explicit SDK, driver, device, lifecycle, and evidence prerequisites.
---

# QA mobile specialist

Use this specialist when a QA workflow needs native, hybrid, or mobile Web coverage for Android
or iOS. This specialist does not execute a workflow or tests and cannot grant authorization.
Read [workflow](../../references/workflow.md), [safety](../../references/safety.md), and
[tooling](../../references/tooling.md) before advising the calling workflow.

## Inputs

- Target application/build, identified contract, preserved criterion IDs and text, and in-scope
  platform: Android, iOS, or both.
- Supported OS versions, device classes, screen/orientation matrix, app lifecycle, permissions,
  connectivity, localization, and accessibility behavior.
- Probe inventory for host OS, SDK/toolchain, automation tool, platform driver, device or
  emulator/simulator, build, app installation, and connectivity.
- Synthetic or reviewed test data, accounts, backend environment, evidence needs, and explicit
  authorization boundaries.

## Procedure

1. Preserve the target, contract, criteria, platforms, device matrix, and authorization supplied
   by the caller. Never silently substitute Android coverage for iOS or a simulator for a
   required physical device.
2. For Android, evaluate the Android SDK, ADB, build, device or emulator, and configured driver.
   Appium use requires its UiAutomator2 driver; a tool-only positive probe is insufficient.
3. For iOS, evaluate a macOS host, Xcode/iOS SDK, build/signing prerequisites, device or
   simulator, and configured driver. Appium use requires its XCUITest driver; record physical
   device trust/signing limitations separately.
4. Ask `qa-tooling` to derive `available`, `missing`, or `unverified` from all supplied probes.
   Keep tool, SDK, driver, and device evidence separate. Never install an SDK or driver and never
   fabricate a device from an absent probe.
5. Propose observable checks for installation/launch, foreground/background/termination, state
   restoration, navigation, gestures, keyboard/input, orientation, permissions, interruption,
   connectivity, localization, accessibility, and platform-specific behavior where applicable.
6. Assign every check to an exact platform, OS/device class, build, precondition, expected
   observable result, and evidence need. Keep expected and observed results distinct.
7. Return coverage and limitations to the calling workflow. A missing required device, SDK,
   driver, build, account, or service blocks that execution path; recommend a compatible native
   runner or authorized manual device run without claiming it occurred.

## Output

Return:

- target/build, contract, criteria, Android/iOS scope, device/OS matrix, environment, and
  authorization;
- checks with platform, lifecycle state, preconditions, actions, expected observable result,
  data, and evidence need;
- separate tool, host, SDK, driver, build, device, and service availability with exact probe
  evidence and platform-compatible alternatives;
- coverage gaps, device-only limitations, defects, blockers, and the next valid action.

`READY` below means all listed prerequisites for the proposed path are available. It is not an
executed case result or global verdict.

## Reference scenarios

| scenario | platform | tool | sdk | driver | device | outcome |
|---|---|---|---|---|---|---|
| platform-ready | Android | Appium UiAutomator2 | available | available | available emulator | READY |
| platform-ready | iOS | Appium XCUITest | available | available | available simulator | READY |
| missing-device | Android | Appium UiAutomator2 | available | available | missing | BLOCKED |

The ready rows remain separate because Android SDK/UiAutomator2/emulator evidence cannot prove
iOS Xcode/XCUITest/simulator readiness, or vice versa. In `missing-device`, positive tool, SDK,
and driver probes do not create an Android device; execution remains `BLOCKED` and the specialist
offers an authorized manual device or compatible native-runner alternative.

## Failure modes

- Platform, app build, contract, expected behavior, or device matrix absent: return affected
  coverage as `BLOCKED` and name the missing input.
- Tool positive but SDK, driver, device, build, or host probe absent/not run/negative: preserve
  each probe and report the complete capability as `unverified` or blocked as appropriate.
- Required physical behavior with only a simulator/emulator: record the limitation; do not claim
  hardware, camera, sensor, biometric, push, or performance coverage.
- Device missing or offline: do not execute or fabricate observations; propose a compatible
  device, native test runner, or authorized manual run.
- Unsupported host/platform pairing: exclude the incompatible tool and return a compatible
  alternative or `none verified`.

## Safety

- This specialist cannot grant device access, signing, production, external-effect, load, or
  penetration-test authorization.
- Never install SDKs, drivers, apps, profiles, or certificates; never alter personal device or
  user configuration, publish, push, merge, or correct product code.
- Do not read personal device data, secrets, credentials, notifications, photos, contacts, or
  unrelated logs. Use synthetic accounts and isolated test data.
- Review screenshots visually before attachment, bind evidence to the exact build/device/target,
  and apply confinement and sanitization requirements.

## Related skills

- `qa-tooling` owns platform filtering, prerequisite probes, and safe alternatives.
- `qa-test` may execute approved mobile checks and bind reviewed evidence.
- `qa-specialist-functional` supplies behavior partitions and state transitions.
- `qa-specialist-accessibility` evaluates platform accessibility behavior when applicable.
