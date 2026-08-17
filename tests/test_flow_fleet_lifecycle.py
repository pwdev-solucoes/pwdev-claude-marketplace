import json
import hashlib
import os
import signal
import shutil
import socket
import subprocess
import tempfile
import time
import unittest
from pathlib import Path

from tests.flow_m5_fixtures import (
    create_approved_phase,
    init_repository,
    run_shell,
    write_executable,
)


ROOT = Path(__file__).resolve().parents[1]
FLEET_UP = ROOT / "plugins" / "pwdev-flow" / "scripts" / "fleet-up.sh"
FLEET_RUNNER = ROOT / "plugins" / "pwdev-flow" / "scripts" / "fleet-run.sh"
FLEET_TEARDOWN = ROOT / "plugins" / "pwdev-flow" / "scripts" / "fleet-teardown.sh"
SAFE_COMMANDS = (
    "awk",
    "basename",
    "cat",
    "chmod",
    "cmp",
    "cp",
    "cut",
    "date",
    "dirname",
    "find",
    "git",
    "grep",
    "head",
    "jq",
    "ln",
    "mkdir",
    "mktemp",
    "mv",
    "python3",
    "rm",
    "rmdir",
    "sed",
    "shasum",
    "sort",
    "stat",
    "tail",
    "tee",
    "tr",
    "wc",
)
INERT_COMMANDS = (
    "aws",
    "az",
    "codex",
    "curl",
    "gcloud",
    "gemini",
    "gh",
    "kiro-cli",
    "kubectl",
    "kimi",
    "nc",
    "ncat",
    "npm",
    "npx",
    "opencode",
    "pip",
    "pulumi",
    "scp",
    "sftp",
    "ssh",
    "terraform",
    "wget",
)


def git(repository: Path, *arguments: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        ["git", "-C", str(repository), *arguments],
        check=False,
        capture_output=True,
        text=True,
    )


def write_fleet_config(
    repository: Path,
    *,
    max_concurrent: int = 3,
    permission_mode: str = "danger-full-access",
    audit: bool = False,
) -> None:
    config = repository / ".planning" / "flow" / "config.json"
    config.parent.mkdir(parents=True, exist_ok=True)
    config.write_text(
        json.dumps(
            {
                "audit": audit,
                "fleet": {
                    "max_concurrent": max_concurrent,
                    "port_base_app": 3000,
                    "port_base_db": 5432,
                    "port_step": 10,
                    "permission_mode": permission_mode,
                    "auto_simplify": False,
                    "compose_file": "docker-compose.flow-fleet.yml",
                }
            }
        ),
        encoding="utf-8",
    )


def write_member(repository: Path, slug: str, index: int) -> Path:
    member = repository / ".planning" / "flow" / "fleet" / f"{slug}.json"
    member.parent.mkdir(parents=True, exist_ok=True)
    member.write_text(
        json.dumps(
            {
                "slug": slug,
                "branch": f"flow-fleet/{slug}",
                "worktree_path": str(repository.parent / f"repo-fleet-{slug}"),
                "app_port": 3000 + 10 * index,
                "db_port": 5432 + 10 * index,
                "port_index": index,
                "project_name": f"flow-fleet-{slug}",
                "tmux_window": f"pwdev-flow-fleet:{slug}",
                "compose_file": "docker-compose.flow-fleet.yml",
                "status": "ACTIVE",
                "initiating_root": str(repository.resolve()),
                "base_branch": git(repository, "symbolic-ref", "--quiet", "--short", "HEAD").stdout.strip(),
                "base_commit": git(repository, "rev-parse", "HEAD").stdout.strip(),
            }
        ),
        encoding="utf-8",
    )
    return member


class FleetLifecycleContractTest(unittest.TestCase):
    def fake_environment(
        self,
        root: Path,
        *,
        docker_exit: int = 0,
        docker_version_exit: int = 0,
        docker_block: bool = False,
        tmux_kill_exit: int = 0,
    ) -> dict[str, str]:
        fake_bin = root / "bin"
        fake_bin.mkdir()
        for command in SAFE_COMMANDS:
            executable = shutil.which(command)
            self.assertIsNotNone(executable, f"{command} is required for the fleet contract tests")
            write_executable(fake_bin / command, f'exec "{executable}" "$@"')
        for command in INERT_COMMANDS:
            write_executable(
                fake_bin / command,
                'printf "%s\\n" "$0" "$@" >> "$FLOW_FORBIDDEN_LOG"\nexit 97',
            )
        docker_log = root / "docker-arguments.txt"
        docker_pid = root / "docker-pid.txt"
        docker_release = root / "docker-release"
        tmux_log = root / "tmux-arguments.txt"
        tmux_state = root / "tmux-window-exists"
        tmux_state.write_text("present\n", encoding="utf-8")
        forbidden_log = root / "forbidden-command-arguments.txt"
        write_executable(
            fake_bin / "docker",
            'printf "%s\\n" "$@" >> "$FLOW_FAKE_DOCKER_LOG"\n'
            'if [ "${1:-}" = compose ] && [ "${2:-}" = version ]; then\n'
            '  exit "$FLOW_FAKE_DOCKER_VERSION_EXIT"\n'
            'fi\n'
            'if [ "${FLOW_FAKE_DOCKER_BLOCK:-0}" = 1 ]; then\n'
            '  printf "%s\\n" "$$" > "$FLOW_FAKE_DOCKER_PID"\n'
            '  while [ ! -f "$FLOW_FAKE_DOCKER_RELEASE" ]; do :; done\n'
            'fi\n'
            'exit "$FLOW_FAKE_DOCKER_EXIT"',
        )
        write_executable(
            fake_bin / "tmux",
            'printf "%s\\n" "$@" >> "$FLOW_FAKE_TMUX_LOG"\n'
            'case "${1:-}" in\n'
            '  has-session) [ -f "$FLOW_FAKE_TMUX_STATE" ] && exit 0; exit 1 ;;\n'
            '  list-windows) [ "$FLOW_FAKE_TMUX_INSPECT_EXIT" = 0 ] || exit "$FLOW_FAKE_TMUX_INSPECT_EXIT"; [ -f "$FLOW_FAKE_TMUX_STATE" ] && printf "%s\\n" "$FLOW_FAKE_TMUX_WINDOW_NAME"; exit 0 ;;\n'
            '  new-session|new-window) : > "$FLOW_FAKE_TMUX_STATE" ;;\n'
            '  kill-window) [ "$FLOW_FAKE_TMUX_KILL_EXIT" = 0 ] || exit "$FLOW_FAKE_TMUX_KILL_EXIT"; [ "$FLOW_FAKE_TMUX_KEEP_WINDOW" = 1 ] || rm -f "$FLOW_FAKE_TMUX_STATE" ;;\n'
            'esac',
        )
        home = root / "home"
        temporary = root / "tmp"
        home.mkdir()
        temporary.mkdir()
        return {
            "FLOW_CLEAN_ENV": "1",
            "HOME": str(home),
            "TMPDIR": str(temporary),
            "PATH": str(fake_bin),
            "GIT_CONFIG_GLOBAL": "/dev/null",
            "GIT_CONFIG_NOSYSTEM": "1",
            "GIT_TERMINAL_PROMPT": "0",
            "LANG": "C",
            "FLOW_FAKE_DOCKER_LOG": str(docker_log),
            "FLOW_FAKE_DOCKER_PID": str(docker_pid),
            "FLOW_FAKE_DOCKER_RELEASE": str(docker_release),
            "FLOW_FAKE_DOCKER_EXIT": str(docker_exit),
            "FLOW_FAKE_DOCKER_VERSION_EXIT": str(docker_version_exit),
            "FLOW_FAKE_DOCKER_BLOCK": "1" if docker_block else "0",
            "FLOW_FAKE_TMUX_LOG": str(tmux_log),
            "FLOW_FAKE_TMUX_STATE": str(tmux_state),
            "FLOW_FAKE_TMUX_KILL_EXIT": str(tmux_kill_exit),
            "FLOW_FAKE_TMUX_INSPECT_EXIT": "0",
            "FLOW_FAKE_TMUX_WINDOW_NAME": "demo",
            "FLOW_FAKE_TMUX_KEEP_WINDOW": "0",
            "FLOW_FORBIDDEN_LOG": str(forbidden_log),
        }

    def launch(self, repository: Path, slug: str, environment: dict[str, str]):
        return run_shell(FLEET_UP, repository, slug, env=environment)

    def active_member(self, repository: Path, slug: str) -> dict[str, object]:
        return json.loads(
            (repository / ".planning" / "flow" / "fleet" / f"{slug}.json").read_text(
                encoding="utf-8"
            )
        )

    def assert_no_forbidden_commands(self, environment: dict[str, str]) -> None:
        self.assertFalse(
            Path(environment["FLOW_FORBIDDEN_LOG"]).exists(),
            "lifecycle scripts must not invoke a prohibited provider or network command",
        )

    def write_terminal_status(
        self,
        worktree: Path,
        *,
        slug: str = "demo",
        stage: str = "verify",
        status_value: str = "DONE",
        message: str = "verified fixture",
        verdict: str = "APPROVED",
        updated_at: str = "2026-08-16T00:00:00Z",
        correction_cycles: object = 0,
    ) -> Path:
        status = worktree / ".planning" / "flow" / "fleet-status.json"
        status.parent.mkdir(parents=True, exist_ok=True)
        status.write_text(
            json.dumps(
                {
                    "slug": slug,
                    "stage": stage,
                    "status": status_value,
                    "message": message,
                    "verdict": verdict,
                    "updated_at": updated_at,
                    "correction_cycles": correction_cycles,
                }
            )
            + "\n",
            encoding="utf-8",
        )
        return status

    def create_active_member(
        self, root: Path, slug: str = "demo"
    ) -> tuple[Path, dict[str, str], dict[str, object]]:
        repository = init_repository(root / "repo")
        write_fleet_config(repository)
        canonical_repository = Path(git(repository, "rev-parse", "--show-toplevel").stdout.strip())
        worktree = canonical_repository.parent / "repo-fleet-demo"
        branch = f"flow-fleet/{slug}"
        self.assertEqual(git(repository, "worktree", "add", "-b", branch, str(worktree)).returncode, 0)
        (worktree / "docker-compose.flow-fleet.yml").write_text("services: {}\n", encoding="utf-8")
        (worktree / ".env.fleet").write_text("FLOW_ENV=development\n", encoding="utf-8")
        (worktree / ".planning" / "flow").mkdir(parents=True, exist_ok=True)
        exclude = Path(git(worktree, "rev-parse", "--git-path", "info/exclude").stdout.strip())
        exclude.parent.mkdir(parents=True, exist_ok=True)
        exclude.write_text(
            ".planning/flow/fleet-status.json\n.env.fleet\n",
            encoding="utf-8",
        )
        member_file = write_member(repository, slug, 0)
        member = json.loads(member_file.read_text(encoding="utf-8"))
        member["worktree_path"] = str(worktree)
        member_file.write_text(json.dumps(member), encoding="utf-8")
        pane_file = member_file.with_suffix(".pane.sh")
        pane_file.write_text("#!/usr/bin/env bash\nexit 0\n", encoding="utf-8")
        pane_file.chmod(0o700)
        environment = self.fake_environment(root)
        return repository, environment, member

    def test_launch_rejects_symlinked_central_parent_before_docker_or_tmux(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            repository = init_repository(root / "repo")
            create_approved_phase(repository, "demo", tracked=True)
            write_fleet_config(repository)
            outside = root / "outside-fleet"
            outside.mkdir()
            sentinel = outside / "sentinel.txt"
            sentinel.write_bytes(b"outside-bytes\n")
            (repository / ".planning" / "flow" / "fleet").symlink_to(
                outside, target_is_directory=True
            )
            environment = self.fake_environment(root)

            result = self.launch(repository, "demo", environment)

            self.assertEqual(result.returncode, 2, result.stderr)
            self.assertEqual(sentinel.read_bytes(), b"outside-bytes\n")
            self.assertEqual(sorted(path.name for path in outside.iterdir()), ["sentinel.txt"])
            self.assertFalse(Path(environment["FLOW_FAKE_DOCKER_LOG"]).exists())
            self.assertFalse(Path(environment["FLOW_FAKE_TMUX_LOG"]).exists())

    def test_launch_rejects_tracked_compose_symlink_before_external_write_or_runtime(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            repository = init_repository(root / "repo")
            create_approved_phase(repository, "demo", tracked=True)
            write_fleet_config(repository)
            sentinel = root / "outside-compose.yml"
            sentinel.write_bytes(b"outside-compose-bytes\n")
            (repository / "docker-compose.flow-fleet.yml").symlink_to(sentinel)
            self.assertEqual(
                git(repository, "add", "docker-compose.flow-fleet.yml").returncode, 0
            )
            self.assertEqual(git(repository, "commit", "-qm", "fixture: compose symlink").returncode, 0)
            environment = self.fake_environment(root)

            result = self.launch(repository, "demo", environment)

            self.assertEqual(result.returncode, 2, result.stderr)
            self.assertEqual(sentinel.read_bytes(), b"outside-compose-bytes\n")
            self.assertFalse(Path(environment["FLOW_FAKE_DOCKER_LOG"]).exists())
            self.assertFalse(Path(environment["FLOW_FAKE_TMUX_LOG"]).exists())

    def test_launch_requires_codex_and_named_branch_without_mutation(self) -> None:
        for prerequisite in ("codex", "named-branch"):
            with self.subTest(prerequisite=prerequisite), tempfile.TemporaryDirectory() as directory:
                root = Path(directory)
                repository = init_repository(root / "repo")
                create_approved_phase(repository, "demo", tracked=True)
                write_fleet_config(repository)
                environment = self.fake_environment(root)
                if prerequisite == "codex":
                    (Path(environment["PATH"]) / "codex").unlink()
                else:
                    self.assertEqual(git(repository, "checkout", "--detach", "-q").returncode, 0)
                status_before = git(repository, "status", "--short").stdout
                worktrees_before = git(repository, "worktree", "list", "--porcelain").stdout
                branches_before = git(repository, "branch", "--format=%(refname)").stdout

                result = self.launch(repository, "demo", environment)

                self.assertEqual(result.returncode, 2, result.stderr)
                self.assertEqual(git(repository, "status", "--short").stdout, status_before)
                self.assertEqual(git(repository, "worktree", "list", "--porcelain").stdout, worktrees_before)
                self.assertEqual(git(repository, "branch", "--format=%(refname)").stdout, branches_before)
                self.assertFalse(Path(environment["FLOW_FAKE_DOCKER_LOG"]).exists())
                self.assertFalse(Path(environment["FLOW_FAKE_TMUX_LOG"]).exists())

    def test_launch_requires_python3_before_any_mutation(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            repository = init_repository(root / "repo")
            create_approved_phase(repository, "demo", tracked=True)
            write_fleet_config(repository)
            environment = self.fake_environment(root)
            (Path(environment["PATH"]) / "python3").unlink()
            status_before = git(repository, "status", "--short").stdout
            worktrees_before = git(repository, "worktree", "list", "--porcelain").stdout
            branches_before = git(repository, "branch", "--format=%(refname)").stdout

            result = self.launch(repository, "demo", environment)

            self.assertEqual(result.returncode, 2, result.stderr)
            self.assertIn("required binary unavailable: python3", result.stderr)
            self.assertEqual(git(repository, "status", "--short").stdout, status_before)
            self.assertEqual(git(repository, "worktree", "list", "--porcelain").stdout, worktrees_before)
            self.assertEqual(git(repository, "branch", "--format=%(refname)").stdout, branches_before)
            self.assertFalse((repository / ".planning" / "flow" / "fleet" / "demo.json").exists())
            self.assertFalse(Path(environment["FLOW_FAKE_DOCKER_LOG"]).exists())
            self.assertFalse(Path(environment["FLOW_FAKE_TMUX_LOG"]).exists())

    def test_dry_and_live_launch_require_exact_config_types_and_compose_filename(self) -> None:
        for mode in ("dry", "live"):
            for mutation in ("string-false", "wrong-compose"):
                with self.subTest(mode=mode, mutation=mutation), tempfile.TemporaryDirectory() as directory:
                    root = Path(directory)
                    repository = init_repository(root / "repo")
                    create_approved_phase(repository, "demo", tracked=True)
                    write_fleet_config(repository)
                    config = repository / ".planning" / "flow" / "config.json"
                    payload = json.loads(config.read_text(encoding="utf-8"))
                    if mutation == "string-false":
                        payload["fleet"]["auto_simplify"] = "false"
                    else:
                        payload["fleet"]["compose_file"] = "other-compose.yml"
                    config.write_text(json.dumps(payload), encoding="utf-8")
                    environment = self.fake_environment(root)
                    if mode == "dry":
                        environment["DRY_RUN"] = "1"
                    worktrees_before = git(repository, "worktree", "list", "--porcelain").stdout
                    branches_before = git(repository, "branch", "--format=%(refname)").stdout

                    result = self.launch(repository, "demo", environment)

                    self.assertEqual(result.returncode, 2, result.stderr)
                    self.assertEqual(git(repository, "worktree", "list", "--porcelain").stdout, worktrees_before)
                    self.assertEqual(git(repository, "branch", "--format=%(refname)").stdout, branches_before)
                    self.assertFalse(Path(environment["FLOW_FAKE_DOCKER_LOG"]).exists())
                    self.assertFalse(Path(environment["FLOW_FAKE_TMUX_LOG"]).exists())

    def test_teardown_rejects_symlinked_operational_paths_before_side_effects(self) -> None:
        for target in ("central-parent", "compose-destination"):
            with self.subTest(target=target), tempfile.TemporaryDirectory() as directory:
                root = Path(directory)
                repository, environment, member = self.create_active_member(root)
                worktree = Path(str(member["worktree_path"]))
                sentinel = root / f"{target}-sentinel"
                sentinel.write_bytes(b"outside-bytes\n")
                if target == "central-parent":
                    fleet = repository / ".planning" / "flow" / "fleet"
                    outside = root / "outside-fleet"
                    fleet.rename(outside)
                    fleet.symlink_to(outside, target_is_directory=True)
                else:
                    compose = worktree / "docker-compose.flow-fleet.yml"
                    compose.unlink()
                    compose.symlink_to(sentinel)

                result = run_shell(FLEET_TEARDOWN, repository, "demo", env=environment)

                self.assertEqual(result.returncode, 2, result.stderr)
                self.assertEqual(sentinel.read_bytes(), b"outside-bytes\n")
                self.assertFalse(Path(environment["FLOW_FAKE_DOCKER_LOG"]).exists())
                self.assertFalse(Path(environment["FLOW_FAKE_TMUX_LOG"]).exists())

    def test_dry_run_prints_worktree_docker_tmux_and_flow_paths_without_mutation(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            repository = init_repository(root / "repo")
            create_approved_phase(repository, "demo", tracked=True)
            write_fleet_config(repository)
            environment = self.fake_environment(root)
            environment["DRY_RUN"] = "1"
            worktrees_before = git(repository, "worktree", "list", "--porcelain").stdout

            result = self.launch(repository, "demo", environment)

            self.assertEqual(result.returncode, 0, result.stderr)
            for fragment in (
                "git worktree add",
                "flow-fleet/demo",
                "docker compose",
                "pwdev-flow-fleet:demo",
                ".planning/flow/fleet/demo.json",
                ".planning/flow/fleet/demo.pane.sh",
            ):
                with self.subTest(fragment=fragment):
                    self.assertIn(fragment, result.stdout)
            canonical_worktree = Path(
                git(repository, "rev-parse", "--show-toplevel").stdout.strip()
            ).parent / "repo-fleet-demo"
            self.assertIn(
                f"exec {FLEET_RUNNER} demo {canonical_worktree} danger-full-access\\n",
                result.stdout,
            )
            self.assertNotEqual(
                git(repository, "show-ref", "--verify", "--quiet", "refs/heads/flow-fleet/demo").returncode,
                0,
            )
            self.assertEqual(git(repository, "worktree", "list", "--porcelain").stdout, worktrees_before)
            self.assertFalse((repository / ".planning" / "flow" / "fleet" / "demo.json").exists())
            self.assertFalse((repository / ".planning" / "flow" / "fleet" / "demo.pane.sh").exists())
            self.assertFalse((root / "docker-arguments.txt").exists())
            self.assertFalse((root / "tmux-arguments.txt").exists())
            self.assert_no_forbidden_commands(environment)

    def test_invalid_slug_and_non_dangerous_config_fail_before_mutation(self) -> None:
        for slug, permission_mode in (
            ("../escape", "danger-full-access"),
            ("Demo", "danger-full-access"),
            ("demo", "workspace-write"),
        ):
            with self.subTest(slug=slug, permission_mode=permission_mode), tempfile.TemporaryDirectory() as directory:
                root = Path(directory)
                repository = init_repository(root / "repo")
                create_approved_phase(
                    repository,
                    "../escape" if slug == "../escape" else ("Demo" if slug == "Demo" else "demo"),
                    tracked=True,
                )
                write_fleet_config(repository, permission_mode=permission_mode)
                environment = self.fake_environment(root)
                worktrees_before = git(repository, "worktree", "list", "--porcelain").stdout

                result = self.launch(repository, slug, environment)

                self.assertEqual(result.returncode, 2)
                if slug in {"../escape", "Demo"}:
                    self.assertIn("invalid slug", (result.stdout + result.stderr).lower())
                self.assertEqual(git(repository, "worktree", "list", "--porcelain").stdout, worktrees_before)
                self.assertFalse((root / "docker-arguments.txt").exists())
                self.assertFalse((root / "tmux-arguments.txt").exists())
                self.assert_no_forbidden_commands(environment)

    def test_capacity_and_existing_member_collisions_are_rejected(self) -> None:
        for existing_slug, max_concurrent in (("occupied", 1), ("demo", 3)):
            with self.subTest(existing_slug=existing_slug, max_concurrent=max_concurrent), tempfile.TemporaryDirectory() as directory:
                root = Path(directory)
                repository = init_repository(root / "repo")
                create_approved_phase(repository, "demo", tracked=True)
                write_fleet_config(repository, max_concurrent=max_concurrent)
                member = write_member(repository, existing_slug, 0)
                environment = self.fake_environment(root)
                member_before = member.read_text(encoding="utf-8")
                fleet_directory = repository / ".planning" / "flow" / "fleet"
                fleet_before = {
                    path.name: path.read_bytes() for path in sorted(fleet_directory.iterdir())
                }
                worktrees_before = git(repository, "worktree", "list", "--porcelain").stdout
                root_entries_before = sorted(path.name for path in root.iterdir())

                result = self.launch(repository, "demo", environment)

                self.assertEqual(result.returncode, 2)
                self.assertTrue(member.is_file())
                self.assertEqual(member.read_text(encoding="utf-8"), member_before)
                if existing_slug == "occupied":
                    self.assertFalse((fleet_directory / "demo.json").exists())
                self.assertEqual(
                    {path.name: path.read_bytes() for path in sorted(fleet_directory.iterdir())},
                    fleet_before,
                )
                self.assertEqual(git(repository, "worktree", "list", "--porcelain").stdout, worktrees_before)
                self.assertEqual(sorted(path.name for path in root.iterdir()), root_entries_before)
                self.assertNotEqual(
                    git(repository, "show-ref", "--verify", "--quiet", "refs/heads/flow-fleet/demo").returncode,
                    0,
                )
                self.assertFalse((root / "docker-arguments.txt").exists())
                self.assertFalse((root / "tmux-arguments.txt").exists())
                self.assert_no_forbidden_commands(environment)

    def test_existing_regular_or_dangling_symlink_pane_fails_preflight_unchanged(self) -> None:
        for collision_kind in ("regular", "dangling-symlink"):
            with self.subTest(collision_kind=collision_kind), tempfile.TemporaryDirectory() as directory:
                root = Path(directory)
                repository = init_repository(root / "repo")
                create_approved_phase(repository, "demo", tracked=True)
                write_fleet_config(repository)
                pane_file = repository / ".planning" / "flow" / "fleet" / "demo.pane.sh"
                pane_file.parent.mkdir(parents=True)
                if collision_kind == "regular":
                    pane_file.write_bytes(b"existing pane bytes\n")
                    preserved = pane_file.read_bytes()
                else:
                    pane_file.symlink_to("missing-pane-target")
                    preserved = os.readlink(pane_file)
                environment = self.fake_environment(root)
                worktrees_before = git(repository, "worktree", "list", "--porcelain").stdout

                result = self.launch(repository, "demo", environment)

                self.assertEqual(result.returncode, 2)
                self.assertIn("fleet pane already exists", result.stderr)
                if collision_kind == "regular":
                    self.assertEqual(pane_file.read_bytes(), preserved)
                else:
                    self.assertTrue(pane_file.is_symlink())
                    self.assertEqual(os.readlink(pane_file), preserved)
                self.assertEqual(git(repository, "worktree", "list", "--porcelain").stdout, worktrees_before)
                self.assertNotEqual(
                    git(repository, "show-ref", "--verify", "--quiet", "refs/heads/flow-fleet/demo").returncode,
                    0,
                )
                self.assertFalse((repository / ".planning" / "flow" / "fleet" / "demo.json").exists())
                self.assertFalse(Path(environment["FLOW_FAKE_DOCKER_LOG"]).exists())
                self.assertFalse(Path(environment["FLOW_FAKE_TMUX_LOG"]).exists())
                self.assert_no_forbidden_commands(environment)

    def test_occupied_port_is_rejected_before_worktree_creation(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            repository = init_repository(root / "repo")
            create_approved_phase(repository, "demo", tracked=True)
            write_fleet_config(repository)
            environment = self.fake_environment(root)
            worktrees_before = git(repository, "worktree", "list", "--porcelain").stdout
            root_entries_before = sorted(path.name for path in root.iterdir())
            try:
                with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as listener:
                    listener.bind(("127.0.0.1", 3000))
                    listener.listen()
                    result = self.launch(repository, "demo", environment)
            except PermissionError as error:
                self.skipTest(f"sandbox disallows the local port fixture: {error}")

            self.assertEqual(result.returncode, 2)
            self.assertNotEqual(git(repository, "show-ref", "--verify", "--quiet", "refs/heads/flow-fleet/demo").returncode, 0)
            self.assertEqual(git(repository, "worktree", "list", "--porcelain").stdout, worktrees_before)
            self.assertEqual(sorted(path.name for path in root.iterdir()), root_entries_before)
            self.assertFalse((repository / ".planning" / "flow" / "fleet" / "demo.json").exists())
            self.assertFalse((root / "docker-arguments.txt").exists())
            self.assertFalse((root / "tmux-arguments.txt").exists())
            self.assert_no_forbidden_commands(environment)

    def test_launch_allocates_first_free_slot_and_writes_bookkeeping(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            repository = init_repository(root / "repo")
            create_approved_phase(repository, "demo", tracked=True)
            write_fleet_config(repository)
            write_member(repository, "occupied", 0)
            environment = self.fake_environment(root)

            result = self.launch(repository, "demo", environment)

            self.assertEqual(result.returncode, 0, result.stderr)
            member = self.active_member(repository, "demo")
            self.assertEqual(member["port_index"], 1)
            self.assertEqual(member["app_port"], 3010)
            self.assertEqual(member["db_port"], 5442)
            self.assertEqual(member["branch"], "flow-fleet/demo")
            self.assertTrue(Path(str(member["worktree_path"])).is_dir())
            environment_file = Path(str(member["worktree_path"])) / ".env.fleet"
            self.assertTrue(environment_file.is_file())
            self.assertEqual(environment_file.stat().st_mode & 0o777, 0o600)
            self.assertTrue((root / "docker-arguments.txt").is_file())
            self.assertTrue((root / "tmux-arguments.txt").is_file())
            pane_file = repository / ".planning" / "flow" / "fleet" / "demo.pane.sh"
            self.assertTrue(pane_file.is_file())
            self.assertEqual(pane_file.stat().st_mode & 0o777, 0o700)
            self.assertFalse((Path(str(member["worktree_path"])) / ".flow-fleet-pane.sh").exists())
            self.assertIn(
                str(pane_file),
                (root / "tmux-arguments.txt").read_text(encoding="utf-8"),
            )
            self.assert_no_forbidden_commands(environment)

    def test_fleet_launch_and_teardown_emit_only_verified_sanitized_audit_events(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            repository = init_repository(root / "repo")
            create_approved_phase(repository, "demo", tracked=True)
            write_fleet_config(repository, audit=True)
            environment = self.fake_environment(root)

            launch = self.launch(repository, "demo", environment)

            self.assertEqual(launch.returncode, 0, launch.stderr)
            audit_file = repository / ".planning" / "flow" / "audit" / "events.jsonl"
            events = [json.loads(line) for line in audit_file.read_text(encoding="utf-8").splitlines()]
            self.assertEqual([event["action"] for event in events], ["fleet_launched"])
            serialized = json.dumps(events)
            member = self.active_member(repository, "demo")
            for prohibited in (str(member["worktree_path"]), "danger-full-access", "prompt", "model"):
                self.assertNotIn(prohibited, serialized)

            teardown = run_shell(FLEET_TEARDOWN, repository, "demo", env=environment)

            self.assertEqual(teardown.returncode, 0, teardown.stderr)
            events = [json.loads(line) for line in audit_file.read_text(encoding="utf-8").splitlines()]
            self.assertEqual(
                [event["action"] for event in events],
                ["fleet_launched", "fleet_teardown"],
            )

    def test_launch_failure_has_no_success_audit_and_audit_failure_preserves_launch(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            repository = init_repository(root / "repo")
            create_approved_phase(repository, "demo", tracked=True)
            write_fleet_config(repository, audit=True)
            environment = self.fake_environment(root, docker_exit=9)

            failed = self.launch(repository, "demo", environment)

            self.assertNotEqual(failed.returncode, 0)
            self.assertFalse(
                (repository / ".planning" / "flow" / "audit" / "events.jsonl").exists()
            )

        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            repository = init_repository(root / "repo")
            create_approved_phase(repository, "demo", tracked=True)
            write_fleet_config(repository, audit=True)
            environment = self.fake_environment(root)
            write_executable(Path(environment["PATH"]) / "python3", "exit 23")

            result = self.launch(repository, "demo", environment)

            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertIn("warning: fleet_launched audit record failed", result.stderr)
            self.assertNotIn(str(repository), result.stderr)

    def test_generated_pane_wrapper_executes_runner_with_exact_fleet_vector(self) -> None:
        with tempfile.TemporaryDirectory(prefix="flow fleet pane ") as directory:
            root = Path(directory)
            repository = init_repository(root / "repo")
            create_approved_phase(repository, "demo", tracked=True)
            write_fleet_config(repository)
            fixture_plugin = root / "fixture-plugin"
            fixture_scripts = fixture_plugin / "scripts"
            fixture_templates = fixture_plugin / "templates"
            fixture_scripts.mkdir(parents=True)
            fixture_templates.mkdir(parents=True)
            copied_up = fixture_scripts / "fleet-up.sh"
            shutil.copy2(FLEET_UP, copied_up)
            shutil.copy2(
                ROOT / "plugins/pwdev-flow/templates/docker-compose.flow-fleet.yml",
                fixture_templates / "docker-compose.flow-fleet.yml",
            )
            runner_arguments = root / "runner-arguments.txt"
            write_executable(
                fixture_scripts / "fleet-run.sh",
                '[ -f "$FLOW_EXPECTED_MEMBER" ] || { printf "member missing at pane start\\n" >&2; exit 55; }\n'
                'grep -q \'"status": "ACTIVE"\' "$FLOW_EXPECTED_MEMBER" || { printf "member not ACTIVE at pane start\\n" >&2; exit 56; }\n'
                'printf "%s\\n" "$@" > "$FLOW_FAKE_RUNNER_ARGS"',
            )
            write_executable(fixture_scripts / "fleet-dashboard.sh", "exit 0")
            environment = self.fake_environment(root)
            environment["FLOW_FAKE_RUNNER_ARGS"] = str(runner_arguments)
            expected_member = repository / ".planning/flow/fleet/demo.json"
            environment["FLOW_EXPECTED_MEMBER"] = str(expected_member)
            write_executable(
                Path(environment["PATH"]) / "tmux",
                'printf "%s\\n" "$@" >> "$FLOW_FAKE_TMUX_LOG"\n'
                'case "${1:-}" in\n'
                '  has-session) exit 1 ;;\n'
                '  new-session) exit 0 ;;\n'
                '  new-window) last=""; for argument in "$@"; do last=$argument; done; PATH=/bin:/usr/bin /bin/bash -c "$last" ;;\n'
                'esac',
            )

            launch = run_shell(copied_up, repository, "demo", env=environment)

            self.assertEqual(launch.returncode, 0, launch.stderr)
            member = self.active_member(repository, "demo")
            worktree = Path(str(member["worktree_path"]))
            wrapper = repository / ".planning" / "flow" / "fleet" / "demo.pane.sh"
            self.assertTrue(wrapper.is_file())
            self.assertFalse((worktree / ".flow-fleet-pane.sh").exists())
            tmux_arguments = Path(environment["FLOW_FAKE_TMUX_LOG"]).read_text(encoding="utf-8")
            self.assertIn(str(wrapper.resolve()).replace(" ", "\\ "), tmux_arguments)
            self.assertEqual(
                runner_arguments.read_text(encoding="utf-8").splitlines(),
                ["demo", str(worktree), "danger-full-access"],
            )

    def test_tmux_session_failure_preserves_central_pane_and_recovery_state(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            repository = init_repository(root / "repo")
            create_approved_phase(repository, "demo", tracked=True)
            write_fleet_config(repository)
            environment = self.fake_environment(root)
            write_executable(
                Path(environment["PATH"]) / "tmux",
                'case "${1:-}" in has-session) exit 1 ;; new-session) exit 41 ;; esac',
            )

            launch = self.launch(repository, "demo", environment)

            self.assertNotEqual(launch.returncode, 0)
            member = self.active_member(repository, "demo")
            self.assertEqual(member["status"], "NEEDS_HUMAN")
            self.assertTrue(member["tmux_attempted"])
            pane_file = repository / ".planning" / "flow" / "fleet" / "demo.pane.sh"
            self.assertTrue(pane_file.is_file())
            self.assertEqual(pane_file.stat().st_mode & 0o777, 0o700)
            self.assertFalse((Path(str(member["worktree_path"])) / ".flow-fleet-pane.sh").exists())

    def test_directory_or_symlink_to_directory_race_cannot_capture_pane_publication(self) -> None:
        for collision_kind in ("directory", "symlink-to-directory"):
            with self.subTest(collision_kind=collision_kind), tempfile.TemporaryDirectory() as directory:
                root = Path(directory)
                repository = init_repository(root / "repo")
                create_approved_phase(repository, "demo", tracked=True)
                write_fleet_config(repository)
                environment = self.fake_environment(root)
                pane_file = repository / ".planning" / "flow" / "fleet" / "demo.pane.sh"
                target_directory = root / "race-pane-container"
                real_chmod = shutil.which("chmod")
                real_mkdir = shutil.which("mkdir")
                real_ln = shutil.which("ln")
                self.assertIsNotNone(real_chmod)
                self.assertIsNotNone(real_mkdir)
                self.assertIsNotNone(real_ln)
                race_setup = (
                    f'"{real_mkdir}" "$FLOW_RACE_PANE"\n'
                    if collision_kind == "directory"
                    else f'"{real_mkdir}" "$FLOW_RACE_TARGET"\n'
                    f'"{real_ln}" -s "$FLOW_RACE_TARGET" "$FLOW_RACE_PANE"\n'
                )
                write_executable(
                    Path(environment["PATH"]) / "chmod",
                    'if [ "${1:-}" = 700 ]; then\n'
                    '  case "${2:-}" in */.demo.pane.sh.*)\n'
                    + race_setup
                    + '  ;; esac\n'
                    'fi\n'
                    f'exec "{real_chmod}" "$@"',
                )
                environment["FLOW_RACE_PANE"] = str(pane_file)
                environment["FLOW_RACE_TARGET"] = str(target_directory)

                result = self.launch(repository, "demo", environment)

                self.assertNotEqual(result.returncode, 0)
                self.assertIn("recovery", result.stderr.lower())
                if collision_kind == "directory":
                    self.assertTrue(pane_file.is_dir())
                    container = pane_file
                else:
                    self.assertTrue(pane_file.is_symlink())
                    self.assertEqual(os.readlink(pane_file), str(target_directory))
                    container = target_directory
                self.assertEqual(list(container.iterdir()), [])
                member = self.active_member(repository, "demo")
                self.assertEqual(member["status"], "NEEDS_HUMAN")
                self.assertTrue(member["worktree_created"])
                self.assertTrue(member["docker_attempted"])
                self.assertFalse(member["tmux_attempted"])
                self.assertFalse(list(pane_file.parent.glob(".demo.pane.sh.*")))
                self.assertTrue(Path(environment["FLOW_FAKE_DOCKER_LOG"]).exists())
                self.assertFalse(Path(environment["FLOW_FAKE_TMUX_LOG"]).exists())

    def test_first_sigterm_wins_at_reservation_restore_and_cleans_incomplete_pane(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            repository = init_repository(root / "repo")
            create_approved_phase(repository, "demo", tracked=True)
            write_fleet_config(repository)
            environment = self.fake_environment(root)
            pane_file = repository / ".planning" / "flow" / "fleet" / "demo.pane.sh"
            reservation_reached = root / "reservation-reached"
            later_signal_sent = root / "later-signal-sent"
            bash_environment = root / "signal-after-reservation.sh"
            bash_environment.write_text(
                "set -T\n"
                "flow_signal_after_reservation() {\n"
                "  if [[ ${BASH_COMMAND:-} == 'PANE_INCOMPLETE_OWNED=true' "
                "&& -f $FLOW_EXPECTED_PANE && ! -f $FLOW_RESERVATION_REACHED ]]; then\n"
                "    printf 'reached\\n' > \"$FLOW_RESERVATION_REACHED\"\n"
                "    kill -TERM \"$$\"\n"
                "  elif [[ ${BASH_COMMAND:-} == 'pending=$PENDING_RECOVERY_SIGNAL' "
                "&& -f $FLOW_RESERVATION_REACHED && ! -f $FLOW_LATER_SIGNAL_SENT ]]; then\n"
                "    printf 'sent\\n' > \"$FLOW_LATER_SIGNAL_SENT\"\n"
                "    kill -HUP \"$$\"\n"
                "  fi\n"
                "}\n"
                "trap flow_signal_after_reservation DEBUG\n",
                encoding="utf-8",
            )
            environment["BASH_ENV"] = str(bash_environment)
            environment["FLOW_EXPECTED_PANE"] = str(pane_file)
            environment["FLOW_RESERVATION_REACHED"] = str(reservation_reached)
            environment["FLOW_LATER_SIGNAL_SENT"] = str(later_signal_sent)

            result = self.launch(repository, "demo", environment)

            self.assertEqual(result.returncode, 143, result.stderr)
            self.assertTrue(reservation_reached.is_file(), "launch never reached exact-path reservation")
            self.assertTrue(later_signal_sent.is_file(), "later HUP was not injected at deferral end")
            self.assertIn("termination", result.stderr.lower())
            self.assertNotIn("hangup", result.stderr.lower())
            member = self.active_member(repository, "demo")
            self.assertEqual(member["status"], "NEEDS_HUMAN")
            self.assertTrue(member["worktree_created"])
            self.assertTrue(member["docker_attempted"])
            self.assertFalse(member["tmux_attempted"])
            self.assertFalse(pane_file.exists())
            self.assertFalse(list(pane_file.parent.glob(".demo.pane.sh.*")))
            self.assertTrue(Path(environment["FLOW_FAKE_DOCKER_LOG"]).exists())
            self.assertFalse(Path(environment["FLOW_FAKE_TMUX_LOG"]).exists())
            self.assert_no_forbidden_commands(environment)

    def test_first_sigterm_wins_at_validation_restore_and_preserves_complete_pane(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            repository = init_repository(root / "repo")
            create_approved_phase(repository, "demo", tracked=True)
            write_fleet_config(repository)
            environment = self.fake_environment(root)
            pane_file = repository / ".planning" / "flow" / "fleet" / "demo.pane.sh"
            validation_reached = root / "validation-reached"
            validation_release = root / "validation-release"
            later_signal_sent = root / "later-signal-sent"
            bash_environment = root / "signal-at-validation-restore.sh"
            bash_environment.write_text(
                "set -T\n"
                "flow_signal_at_validation_restore() {\n"
                "  if [[ ${BASH_COMMAND:-} == 'pending=$PENDING_RECOVERY_SIGNAL' "
                "&& -f $FLOW_VALIDATION_REACHED && ! -f $FLOW_LATER_SIGNAL_SENT ]]; then\n"
                "    printf 'sent\\n' > \"$FLOW_LATER_SIGNAL_SENT\"\n"
                "    kill -INT \"$$\"\n"
                "  fi\n"
                "}\n"
                "trap flow_signal_at_validation_restore DEBUG\n",
                encoding="utf-8",
            )
            real_cmp = shutil.which("cmp")
            self.assertIsNotNone(real_cmp)
            write_executable(
                Path(environment["PATH"]) / "cmp",
                'case "${3:-}" in */demo.pane.sh)\n'
                '  printf "%s\\n" "$$" > "$FLOW_VALIDATION_REACHED"\n'
                '  while [ ! -f "$FLOW_VALIDATION_RELEASE" ]; do :; done\n'
                '  ;;\n'
                'esac\n'
                f'exec "{real_cmp}" "$@"',
            )
            environment["FLOW_VALIDATION_REACHED"] = str(validation_reached)
            environment["FLOW_VALIDATION_RELEASE"] = str(validation_release)
            environment["FLOW_LATER_SIGNAL_SENT"] = str(later_signal_sent)
            environment["BASH_ENV"] = str(bash_environment)
            process = subprocess.Popen(
                ["/bin/bash", str(FLEET_UP), "demo"],
                cwd=repository,
                env={"LC_ALL": "C", **environment},
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
            )
            try:
                deadline = time.monotonic() + 5
                while not validation_reached.exists() and time.monotonic() < deadline:
                    time.sleep(0.02)
                self.assertTrue(validation_reached.is_file(), "launch never reached final pane validation")
                process.send_signal(signal.SIGTERM)
                validation_release.write_text("release\n", encoding="utf-8")
                _stdout, stderr = process.communicate(timeout=5)
            finally:
                if process.poll() is None:
                    validation_release.write_text("release\n", encoding="utf-8")
                    process.terminate()
                    process.communicate(timeout=5)

            self.assertEqual(process.returncode, 143, stderr)
            self.assertTrue(later_signal_sent.is_file(), "later INT was not injected at deferral end")
            self.assertIn("termination", stderr.lower())
            self.assertNotIn("interrupt", stderr.lower())
            member = self.active_member(repository, "demo")
            self.assertEqual(member["status"], "NEEDS_HUMAN")
            self.assertTrue(member["worktree_created"])
            self.assertTrue(member["docker_attempted"])
            self.assertFalse(member["tmux_attempted"])
            self.assertTrue(pane_file.is_file())
            self.assertEqual(pane_file.stat().st_mode & 0o777, 0o700)
            canonical_repository = Path(
                git(repository, "rev-parse", "--show-toplevel").stdout.strip()
            )
            self.assertEqual(
                pane_file.read_text(encoding="utf-8"),
                f"#!/usr/bin/env bash\nexec {FLEET_RUNNER} demo "
                f"{canonical_repository.parent / 'repo-fleet-demo'} danger-full-access\n",
            )
            self.assertFalse(list(pane_file.parent.glob(".demo.pane.sh.*")))
            self.assertTrue(Path(environment["FLOW_FAKE_DOCKER_LOG"]).exists())
            self.assertFalse(Path(environment["FLOW_FAKE_TMUX_LOG"]).exists())
            self.assert_no_forbidden_commands(environment)

    def test_untracked_approved_contracts_are_adopted_only_in_worktree(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            repository = init_repository(root / "repo")
            create_approved_phase(repository, "demo", tracked=False)
            write_fleet_config(repository)
            environment = self.fake_environment(root)
            status_before = git(repository, "status", "--short").stdout
            head_before = git(repository, "rev-parse", "HEAD").stdout.strip()

            result = self.launch(repository, "demo", environment)

            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertEqual(git(repository, "status", "--short").stdout, status_before)
            worktree = Path(str(self.active_member(repository, "demo")["worktree_path"]))
            self.assertNotEqual(git(worktree, "rev-parse", "HEAD").stdout.strip(), head_before)
            for filename in ("spec.md", "decisions.md"):
                relative = f".planning/flow/phases/demo/{filename}"
                with self.subTest(contract=filename):
                    self.assertTrue((worktree / relative).is_file())
                    self.assertEqual(git(worktree, "cat-file", "-e", f"HEAD:{relative}").returncode, 0)
            self.assert_no_forbidden_commands(environment)

    def test_stale_head_contracts_are_replaced_by_exact_approved_bytes_and_bound(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            repository = init_repository(root / "repo")
            create_approved_phase(repository, "demo", tracked=True)
            phase = repository / ".planning" / "flow" / "phases" / "demo"
            (phase / "spec.md").write_text("# Stale\n\n- Status: DRAFT\n", encoding="utf-8")
            (phase / "decisions.md").write_text(
                "# Stale\n\n- Status: REJECTED\n", encoding="utf-8"
            )
            self.assertEqual(git(repository, "add", str(phase)).returncode, 0)
            self.assertEqual(git(repository, "commit", "-qm", "fixture: stale contracts").returncode, 0)
            create_approved_phase(repository, "demo", tracked=False)
            approved = {
                name: (phase / name).read_bytes() for name in ("spec.md", "decisions.md")
            }
            write_fleet_config(repository)
            environment = self.fake_environment(root)

            result = self.launch(repository, "demo", environment)

            self.assertEqual(result.returncode, 0, result.stderr)
            member = self.active_member(repository, "demo")
            worktree = Path(str(member["worktree_path"]))
            for name, expected in approved.items():
                self.assertEqual((worktree / ".planning" / "flow" / "phases" / "demo" / name).read_bytes(), expected)
                self.assertEqual(member[f"{name.removesuffix('.md')}_sha256"], hashlib.sha256(expected).hexdigest())
            self.assert_no_forbidden_commands(environment)

    def test_dry_run_binds_contract_hashes_base_branch_and_safe_publications(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            repository = init_repository(root / "repo")
            create_approved_phase(repository, "demo", tracked=True)
            phase = repository / ".planning" / "flow" / "phases" / "demo"
            (phase / "spec.md").write_text("# Stale\n\n- Status: DRAFT\n", encoding="utf-8")
            self.assertEqual(git(repository, "add", str(phase / "spec.md")).returncode, 0)
            self.assertEqual(git(repository, "commit", "-qm", "fixture: stale dry contract").returncode, 0)
            create_approved_phase(repository, "demo", tracked=False)
            write_fleet_config(repository)
            environment = self.fake_environment(root)
            environment["DRY_RUN"] = "1"
            spec_hash = hashlib.sha256((phase / "spec.md").read_bytes()).hexdigest()
            decisions_hash = hashlib.sha256((phase / "decisions.md").read_bytes()).hexdigest()
            base_branch = git(repository, "symbolic-ref", "--quiet", "--short", "HEAD").stdout.strip()
            base_commit = git(repository, "rev-parse", "HEAD").stdout.strip()

            result = self.launch(repository, "demo", environment)

            self.assertEqual(result.returncode, 0, result.stderr)
            for literal in (
                spec_hash,
                decisions_hash,
                base_branch,
                base_commit,
                "spec_sha256",
                "decisions_sha256",
                "initiating_root",
                "base_branch",
                "base_commit",
                ".gitignore.XXXXXX",
                ".docker-compose.flow-fleet.yml.XXXXXX",
                ".env.fleet.XXXXXX",
            ):
                self.assertIn(literal, result.stdout)
            self.assertIn(str(phase / "spec.md"), result.stdout)
            self.assertEqual(git(repository, "status", "--short").stdout.count("spec.md"), 1)

    def test_partial_docker_failure_persists_needs_human_resources(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            repository = init_repository(root / "repo")
            create_approved_phase(repository, "demo", tracked=True)
            write_fleet_config(repository)
            environment = self.fake_environment(root, docker_exit=9)

            result = self.launch(repository, "demo", environment)

            self.assertNotEqual(result.returncode, 0)
            member_file = repository / ".planning" / "flow" / "fleet" / "demo.json"
            self.assertTrue(member_file.is_file(), "post-worktree Docker failure must persist bookkeeping")
            member = json.loads(member_file.read_text(encoding="utf-8"))
            self.assertEqual(member["status"], "NEEDS_HUMAN")
            self.assertTrue(member["worktree_created"])
            self.assertTrue(member["docker_attempted"])
            self.assertFalse(member["tmux_attempted"])
            self.assert_no_forbidden_commands(environment)

    def test_teardown_recovers_pre_pane_partial_launch(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            repository = init_repository(root / "repo")
            create_approved_phase(repository, "demo", tracked=True)
            write_fleet_config(repository)
            environment = self.fake_environment(root, docker_exit=9)

            launch = self.launch(repository, "demo", environment)

            self.assertNotEqual(launch.returncode, 0)
            pane_file = repository / ".planning" / "flow" / "fleet" / "demo.pane.sh"
            self.assertFalse(pane_file.exists())
            environment["FLOW_FAKE_DOCKER_EXIT"] = "0"

            teardown = run_shell(FLEET_TEARDOWN, repository, "demo", env=environment)

            self.assertEqual(teardown.returncode, 0, teardown.stderr)
            self.assertFalse((repository / ".planning" / "flow" / "fleet" / "demo.json").exists())
            self.assertFalse(pane_file.exists())

    def test_teardown_without_merge_preserves_branch_and_worktree(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            repository, environment, member = self.create_active_member(Path(directory))
            worktree = Path(str(member["worktree_path"]))
            (worktree / "fleet-only.txt").write_text("branch only\n", encoding="utf-8")
            self.assertEqual(git(worktree, "add", "fleet-only.txt").returncode, 0)
            self.assertEqual(git(worktree, "commit", "-qm", "fixture: fleet only").returncode, 0)

            result = run_shell(FLEET_TEARDOWN, repository, "demo", env=environment)

            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertTrue(worktree.is_dir())
            self.assertEqual(git(repository, "show-ref", "--verify", "--quiet", "refs/heads/flow-fleet/demo").returncode, 0)
            self.assertFalse((repository / "fleet-only.txt").exists())
            self.assertFalse((repository / ".planning" / "flow" / "fleet" / "demo.json").exists())
            self.assertFalse((repository / ".planning" / "flow" / "fleet" / "demo.pane.sh").exists())
            self.assertIn("down", (Path(environment["FLOW_FAKE_DOCKER_LOG"])).read_text(encoding="utf-8"))
            self.assertIn("kill-window", (Path(environment["FLOW_FAKE_TMUX_LOG"])).read_text(encoding="utf-8"))
            self.assert_no_forbidden_commands(environment)

    def test_teardown_refuses_merge_when_status_is_not_done(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            repository, environment, member = self.create_active_member(Path(directory))
            worktree = Path(str(member["worktree_path"]))
            status = worktree / ".planning" / "flow" / "fleet-status.json"
            status.parent.mkdir(parents=True, exist_ok=True)
            status.write_text('{"status": "NEEDS_HUMAN"}\n', encoding="utf-8")
            head_before = git(repository, "rev-parse", "HEAD").stdout

            result = run_shell(FLEET_TEARDOWN, repository, "demo", "--merge", env=environment)

            self.assertNotEqual(result.returncode, 0)
            output = (result.stdout + result.stderr).lower()
            self.assertIn("refus", output)
            self.assertIn("needs_human", output)
            self.assertEqual(git(repository, "rev-parse", "HEAD").stdout, head_before)
            self.assertTrue(worktree.is_dir())
            self.assertTrue((repository / ".planning" / "flow" / "fleet" / "demo.json").exists())
            self.assertTrue((repository / ".planning" / "flow" / "fleet" / "demo.pane.sh").exists())
            self.assertFalse(Path(environment["FLOW_FAKE_DOCKER_LOG"]).exists())
            self.assertFalse(Path(environment["FLOW_FAKE_TMUX_LOG"]).exists())
            self.assert_no_forbidden_commands(environment)

    def test_merge_rejects_every_invalid_terminal_status_before_runtime_side_effects(self) -> None:
        invalid_payloads = (
            {"slug": "other"},
            {"stage": "review"},
            {"verdict": "REJECTED"},
            {"message": ""},
            {"updated_at": ""},
            {"correction_cycles": -1},
            {"correction_cycles": 3},
            {"correction_cycles": 1.5},
            {"status_value": "ACTIVE"},
        )
        for overrides in invalid_payloads:
            with self.subTest(overrides=overrides), tempfile.TemporaryDirectory() as directory:
                root = Path(directory)
                repository, environment, member = self.create_active_member(root)
                worktree = Path(str(member["worktree_path"]))
                self.write_terminal_status(worktree, **overrides)

                result = run_shell(FLEET_TEARDOWN, repository, "demo", "--merge", env=environment)

                self.assertNotEqual(result.returncode, 0)
                self.assertFalse(Path(environment["FLOW_FAKE_DOCKER_LOG"]).exists())
                self.assertFalse(Path(environment["FLOW_FAKE_TMUX_LOG"]).exists())
                self.assertTrue(worktree.is_dir())
                self.assertTrue(
                    (repository / ".planning" / "flow" / "fleet" / "demo.json").is_file()
                )

        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            repository, environment, member = self.create_active_member(root)
            worktree = Path(str(member["worktree_path"]))
            status = self.write_terminal_status(worktree)
            payload = json.loads(status.read_text(encoding="utf-8"))
            payload.pop("message")
            status.write_text(json.dumps(payload) + "\n", encoding="utf-8")

            result = run_shell(FLEET_TEARDOWN, repository, "demo", "--merge", env=environment)

            self.assertNotEqual(result.returncode, 0)
            self.assertFalse(Path(environment["FLOW_FAKE_DOCKER_LOG"]).exists())
            self.assertFalse(Path(environment["FLOW_FAKE_TMUX_LOG"]).exists())

    def test_merge_refuses_base_branch_drift_before_stopping_resources(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            repository, environment, member = self.create_active_member(root)
            worktree = Path(str(member["worktree_path"]))
            self.write_terminal_status(worktree)
            self.assertEqual(git(repository, "switch", "-q", "-c", "other").returncode, 0)
            head_before = git(repository, "rev-parse", "HEAD").stdout

            result = run_shell(FLEET_TEARDOWN, repository, "demo", "--merge", env=environment)

            self.assertEqual(result.returncode, 2, result.stderr)
            self.assertIn("base branch", result.stderr)
            self.assertEqual(git(repository, "rev-parse", "HEAD").stdout, head_before)
            self.assertTrue(worktree.is_dir())
            self.assertFalse(Path(environment["FLOW_FAKE_DOCKER_LOG"]).exists())
            self.assertFalse(Path(environment["FLOW_FAKE_TMUX_LOG"]).exists())

    def test_done_member_merges_and_removes_worktree(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            repository, environment, member = self.create_active_member(Path(directory))
            worktree = Path(str(member["worktree_path"]))
            status = self.write_terminal_status(worktree)
            (worktree / "result.txt").write_text("done\n", encoding="utf-8")
            self.assertEqual(git(worktree, "add", "result.txt").returncode, 0)
            self.assertEqual(git(worktree, "commit", "-qm", "fixture: result").returncode, 0)

            result = run_shell(FLEET_TEARDOWN, repository, "demo", "--merge", env=environment)

            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertEqual((repository / "result.txt").read_text(encoding="utf-8"), "done\n")
            self.assertFalse(worktree.exists())
            self.assertFalse((repository / ".planning" / "flow" / "fleet" / "demo.json").exists())
            self.assertFalse((repository / ".planning" / "flow" / "fleet" / "demo.pane.sh").exists())
            self.assert_no_forbidden_commands(environment)

    def test_merge_conflict_aborts_and_preserves_recoverable_state(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            repository, environment, member = self.create_active_member(Path(directory))
            worktree = Path(str(member["worktree_path"]))
            status = self.write_terminal_status(worktree)
            (worktree / "README.md").write_text("# Worktree change\n", encoding="utf-8")
            self.assertEqual(git(worktree, "add", "README.md").returncode, 0)
            self.assertEqual(git(worktree, "commit", "-qm", "fixture: worktree conflict").returncode, 0)
            (repository / "README.md").write_text("# Main change\n", encoding="utf-8")
            self.assertEqual(git(repository, "add", "README.md").returncode, 0)
            self.assertEqual(git(repository, "commit", "-qm", "fixture: main conflict").returncode, 0)
            head_before = git(repository, "rev-parse", "HEAD").stdout
            readme_before = (repository / "README.md").read_text(encoding="utf-8")

            result = run_shell(FLEET_TEARDOWN, repository, "demo", "--merge", env=environment)

            self.assertNotEqual(result.returncode, 0)
            self.assertIn("conflict", (result.stdout + result.stderr).lower())
            self.assertFalse((repository / ".git" / "MERGE_HEAD").exists())
            self.assertEqual(git(repository, "rev-parse", "HEAD").stdout, head_before)
            self.assertEqual((repository / "README.md").read_text(encoding="utf-8"), readme_before)
            self.assertTrue(worktree.is_dir())
            self.assertEqual(git(repository, "show-ref", "--verify", "--quiet", "refs/heads/flow-fleet/demo").returncode, 0)
            self.assertTrue((repository / ".planning" / "flow" / "fleet" / "demo.json").exists())
            self.assertTrue((repository / ".planning" / "flow" / "fleet" / "demo.pane.sh").exists())
            self.assertTrue(Path(environment["FLOW_FAKE_DOCKER_LOG"]).is_file())
            self.assertTrue(Path(environment["FLOW_FAKE_TMUX_LOG"]).is_file())
            self.assert_no_forbidden_commands(environment)

    def test_dry_run_renders_db_only_plan_and_full_fleet_bookkeeping(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            repository = init_repository(root / "repo")
            create_approved_phase(repository, "demo", tracked=False)
            write_fleet_config(repository)
            environment = self.fake_environment(root)
            environment["DRY_RUN"] = "1"

            result = self.launch(repository, "demo", environment)

            self.assertEqual(result.returncode, 0, result.stderr)
            for fragment in (
                "port_index=0",
                "app_port=3000",
                "db_port=5432",
                "docker compose version",
                "up -d db",
                "mkdir -p",
                "git -C",
                "chmod 600",
                "fleet-dashboard.sh",
                "fleet-run.sh",
                "--arg status ACTIVE",
            ):
                with self.subTest(fragment=fragment):
                    self.assertIn(fragment, result.stdout)
            self.assertFalse(Path(environment["FLOW_FAKE_DOCKER_LOG"]).exists())
            self.assertFalse(Path(environment["FLOW_FAKE_TMUX_LOG"]).exists())

    def test_dry_run_publishes_exact_contracts_and_renders_exact_provision_flow(self) -> None:
        for tracked_contracts in (("spec.md",), ()):
            with self.subTest(tracked_contracts=tracked_contracts), tempfile.TemporaryDirectory(
                prefix="flow fleet parity "
            ) as directory:
                root = Path(directory)
                repository = init_repository(root / "repo")
                repository = Path(git(repository, "rev-parse", "--show-toplevel").stdout.strip())
                create_approved_phase(repository, "demo", tracked=False)
                for contract in tracked_contracts:
                    self.assertEqual(
                        git(repository, "add", f".planning/flow/phases/demo/{contract}").returncode,
                        0,
                    )
                if tracked_contracts:
                    self.assertEqual(
                        git(repository, "commit", "-qm", "fixture: tracked contracts").returncode,
                        0,
                    )
                write_fleet_config(repository)
                environment = self.fake_environment(root)
                environment["DRY_RUN"] = "1"
                worktree = repository.parent / "repo-fleet-demo"
                phase = worktree / ".planning" / "flow" / "phases" / "demo"
                fleet_directory = repository / ".planning" / "flow" / "fleet"
                member = fleet_directory / "demo.json"
                quoted_worktree = str(worktree).replace(" ", "\\ ")
                quoted_phase = str(phase).replace(" ", "\\ ")
                quoted_repository = str(repository).replace(" ", "\\ ")
                quoted_fleet_directory = str(fleet_directory).replace(" ", "\\ ")
                quoted_member = str(member).replace(" ", "\\ ")
                worktrees_before = git(repository, "worktree", "list", "--porcelain").stdout
                status_before = git(repository, "status", "--short").stdout

                result = self.launch(repository, "demo", environment)

                self.assertEqual(result.returncode, 0, result.stderr)
                lines = result.stdout.splitlines()
                worktree_add = f"git worktree add {quoted_worktree} -b flow-fleet/demo"
                self.assertIn(worktree_add, lines)
                created_at = "STATE_CREATED_AT=$(date -u +%Y-%m-%dT%H:%M:%SZ)"
                self.assertEqual(lines.index(created_at), lines.index(worktree_add) + 1)
                mkdir_command = f"mkdir -p {quoted_phase}"
                self.assertEqual(lines.count(mkdir_command), 1)
                contract_publications = [
                    line for line in lines if "contract_temporary=$(mktemp" in line
                ]
                self.assertEqual(len(contract_publications), 2)
                for contract in ("spec.md", "decisions.md"):
                    source = str(repository / ".planning" / "flow" / "phases" / "demo" / contract).replace(
                        " ", "\\ "
                    )
                    destination = f"{quoted_phase}/{contract}"
                    publication = next(line for line in contract_publications if source in line)
                    self.assertIn(f"cmp -s {source} {destination}", publication)
                    self.assertIn(f"cp {source} \"$contract_temporary\"", publication)
                    self.assertIn(f'mv "$contract_temporary" {destination}', publication)
                adoption_guard = (
                    f"if [[ -n $(git -C {quoted_worktree} status --porcelain -- "
                    ".planning/flow/phases/demo) ]]; then "
                    f"git -C {quoted_worktree} add .planning/flow/phases/demo/spec.md "
                    ".planning/flow/phases/demo/decisions.md; "
                    f"git -C {quoted_worktree} commit -m chore\\(flow-fleet\\):\\ adopt\\ approved\\ demo\\ contracts; fi"
                )
                self.assertEqual(lines.count(adoption_guard), 1)
                last_copy = max(lines.index(line) for line in contract_publications)
                self.assertLess(last_copy, lines.index(adoption_guard))

                env_line = next(line for line in lines if "env_temporary=$(mktemp" in line)
                self.assertIn(f"{quoted_worktree}/.env.fleet.XXXXXX", env_line)
                self.assertIn('; (umask 077; printf ', env_line)
                self.assertIn('> "$env_temporary"); chmod 600 "$env_temporary"', env_line)
                self.assertIn(f'mv "$env_temporary" {quoted_worktree}/.env.fleet', env_line)
                compose = (
                    f"(cd {quoted_worktree} && docker compose -p flow-fleet-demo --env-file .env.fleet "
                    "-f docker-compose.flow-fleet.yml up -d db)"
                )
                self.assertIn(compose, lines)
                dashboard = next(line for line in lines if "tmux new-session" in line)
                self.assertIn("tmux has-session -t pwdev-flow-fleet 2>/dev/null", dashboard)
                self.assertIn("-n dashboard bash\\ ", dashboard)
                pane = next(line for line in lines if "tmux new-window" in line)
                pane_path = fleet_directory / "demo.pane.sh"
                quoted_pane_write_path = str(pane_path).replace(" ", "\\ ")
                quoted_pane_path = str(pane_path).replace(" ", "\\\\\\ ")
                self.assertIn(f"-n demo bash\\ {quoted_pane_path}", pane)
                self.assertNotIn(".flow-fleet-pane.sh", result.stdout)
                pane_signal_model = next(
                    line for line in lines if line.startswith("pane_pending_signal=")
                )
                for fragment in (
                    "pane_handle_signal HUP",
                    "pane_handle_signal INT",
                    "pane_handle_signal TERM",
                    'if [[ "$pane_signals_deferred" == true ]]',
                    'elif [[ -n "$pane_pending_signal" ]]',
                    "pane_recover_signal 129",
                    "pane_recover_signal 130",
                    "pane_recover_signal 143",
                    "pending=$pane_pending_signal",
                ):
                    with self.subTest(signal_fragment=fragment):
                        self.assertIn(fragment, pane_signal_model)
                pane_write = next(line for line in lines if "pane_temporary=$(mktemp" in line)
                self.assertIn(f"/.demo.pane.sh.XXXXXX", pane_write)
                self.assertIn('chmod 700 "$pane_temporary"', pane_write)
                self.assertIn(
                    f'(set -o noclobber; : > {quoted_pane_write_path}) 2>/dev/null',
                    pane_write,
                )
                self.assertIn('pane_incomplete_owned=true', pane_write)
                self.assertEqual(pane_write.count("pane_defer_signals"), 2)
                self.assertEqual(pane_write.count("pane_restore_signals"), 3)
                self.assertIn(f'cat "$pane_temporary" > {quoted_pane_write_path}', pane_write)
                self.assertIn(f'chmod 700 {quoted_pane_write_path}', pane_write)
                self.assertIn(f'cmp -s "$pane_temporary" {quoted_pane_write_path}', pane_write)
                self.assertIn('rm "$pane_temporary"', pane_write)

                recovery_state_line = next(
                    line for line in lines if line.startswith("pane_write_recovery_state()")
                )
                for fragment in (
                    "--arg status NEEDS_HUMAN",
                    '--arg created_at "$STATE_CREATED_AT" --arg updated_at "$pane_now"',
                    "--argjson worktree_created true --argjson docker_attempted true "
                    "--argjson tmux_attempted false",
                    f'mv "$pane_state_temporary" {quoted_member}',
                ):
                    with self.subTest(recovery_fragment=fragment):
                        self.assertIn(fragment, recovery_state_line)
                state_line = next(
                    line for line in lines
                    if "jq -n --arg slug demo" in line and "--arg status ACTIVE" in line
                )
                for fragment in (
                    f"NOW=$(date -u +%Y-%m-%dT%H:%M:%SZ); mkdir -p {quoted_fleet_directory}; "
                    f"temporary=$(mktemp {quoted_fleet_directory}/.demo.json.XXXXXX) || exit 1; ",
                    "if ! jq -n --arg slug demo --arg branch flow-fleet/demo",
                    f"--arg worktree {quoted_worktree}",
                    "--arg project flow-fleet-demo --arg window pwdev-flow-fleet:demo",
                    "--arg compose docker-compose.flow-fleet.yml",
                    "--arg spec_sha256",
                    "--arg decisions_sha256",
                    f"--arg initiating_root {quoted_repository}",
                    "--arg base_branch",
                    "--arg base_commit",
                    "--arg status ACTIVE",
                    '--arg created_at "$STATE_CREATED_AT" --arg updated_at "$NOW"',
                    "--argjson app_port 3000 --argjson db_port 5432 --argjson index 0",
                    "--argjson worktree_created true --argjson docker_attempted true --argjson tmux_attempted true",
                    f'> "$temporary"; then rm -f "$temporary"; exit 1; fi; mv "$temporary" {quoted_member}',
                ):
                    with self.subTest(fragment=fragment):
                        self.assertIn(fragment, state_line)
                self.assertLess(lines.index(recovery_state_line), lines.index(pane_signal_model))
                self.assertLess(lines.index(pane_signal_model), lines.index(pane_write))
                self.assertLess(lines.index(pane_write), lines.index(state_line))
                self.assertLess(lines.index(state_line), lines.index(pane))
                self.assertNotIn("<", result.stdout)
                self.assertEqual(git(repository, "status", "--short").stdout, status_before)
                self.assertEqual(git(repository, "worktree", "list", "--porcelain").stdout, worktrees_before)
                self.assertFalse(worktree.exists())
                self.assertFalse(member.exists())
                self.assertFalse(pane_path.exists())
                self.assertFalse(Path(environment["FLOW_FAKE_DOCKER_LOG"]).exists())
                self.assertFalse(Path(environment["FLOW_FAKE_TMUX_LOG"]).exists())

    def test_rendered_dry_run_recovers_pending_signal_before_active_or_tmux(self) -> None:
        with tempfile.TemporaryDirectory(prefix="flow fleet rendered recovery ") as directory:
            root = Path(directory)
            repository = init_repository(root / "repo")
            create_approved_phase(repository, "demo", tracked=True)
            write_fleet_config(repository)
            environment = self.fake_environment(root)
            environment["DRY_RUN"] = "1"
            status_before = git(repository, "status", "--short").stdout
            worktrees_before = git(repository, "worktree", "list", "--porcelain").stdout

            rendered = self.launch(repository, "demo", environment)

            self.assertEqual(rendered.returncode, 0, rendered.stderr)
            self.assertEqual(git(repository, "status", "--short").stdout, status_before)
            self.assertEqual(git(repository, "worktree", "list", "--porcelain").stdout, worktrees_before)
            self.assertFalse(Path(environment["FLOW_FAKE_DOCKER_LOG"]).exists())
            self.assertFalse(Path(environment["FLOW_FAKE_TMUX_LOG"]).exists())

            pane_file = repository / ".planning" / "flow" / "fleet" / "demo.pane.sh"
            member_file = pane_file.parent / "demo.json"
            reservation_reached = root / "rendered-reservation-reached"
            later_signal_sent = root / "rendered-later-signal-sent"
            bash_environment = root / "signal-rendered-plan.sh"
            bash_environment.write_text(
                "set -T\n"
                "flow_signal_rendered_plan() {\n"
                "  if [[ ${BASH_COMMAND:-} == 'pane_incomplete_owned=true' "
                "&& -f $FLOW_EXPECTED_PANE && ! -f $FLOW_RESERVATION_REACHED ]]; then\n"
                "    printf 'reached\\n' > \"$FLOW_RESERVATION_REACHED\"\n"
                "    kill -TERM \"$$\"\n"
                "  elif [[ ${BASH_COMMAND:-} == 'pending=$pane_pending_signal' "
                "&& -f $FLOW_RESERVATION_REACHED && ! -f $FLOW_LATER_SIGNAL_SENT ]]; then\n"
                "    printf 'sent\\n' > \"$FLOW_LATER_SIGNAL_SENT\"\n"
                "    kill -HUP \"$$\"\n"
                "  fi\n"
                "}\n"
                "trap flow_signal_rendered_plan DEBUG\n",
                encoding="utf-8",
            )
            plan = root / "rendered-plan.sh"
            plan.write_text("#!/usr/bin/env bash\nset -Eeuo pipefail\n" + rendered.stdout, encoding="utf-8")
            plan.chmod(0o700)
            execution_environment = dict(environment)
            execution_environment.pop("DRY_RUN")
            execution_environment["BASH_ENV"] = str(bash_environment)
            execution_environment["FLOW_EXPECTED_PANE"] = str(pane_file)
            execution_environment["FLOW_RESERVATION_REACHED"] = str(reservation_reached)
            execution_environment["FLOW_LATER_SIGNAL_SENT"] = str(later_signal_sent)

            executed = run_shell(plan, repository, env=execution_environment)

            self.assertEqual(executed.returncode, 143, executed.stderr)
            self.assertTrue(reservation_reached.is_file(), "rendered plan never reserved its pane")
            self.assertTrue(later_signal_sent.is_file(), "rendered plan never injected later HUP")
            self.assertIn("termination", executed.stderr.lower())
            self.assertNotIn("hangup", executed.stderr.lower())
            member = json.loads(member_file.read_text(encoding="utf-8"))
            self.assertEqual(member["status"], "NEEDS_HUMAN")
            self.assertTrue(member["worktree_created"])
            self.assertTrue(member["docker_attempted"])
            self.assertFalse(member["tmux_attempted"])
            self.assertEqual(member["slug"], "demo")
            self.assertEqual(member["branch"], "flow-fleet/demo")
            canonical_repository = Path(
                git(repository, "rev-parse", "--show-toplevel").stdout.strip()
            )
            self.assertEqual(
                member["worktree_path"], str(canonical_repository.parent / "repo-fleet-demo")
            )
            self.assertEqual(member["app_port"], 3000)
            self.assertEqual(member["db_port"], 5432)
            self.assertEqual(member["port_index"], 0)
            self.assertEqual(member["project_name"], "flow-fleet-demo")
            self.assertEqual(member["tmux_window"], "pwdev-flow-fleet:demo")
            self.assertEqual(member["compose_file"], "docker-compose.flow-fleet.yml")
            self.assertRegex(str(member["created_at"]), r"^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}Z$")
            self.assertRegex(str(member["updated_at"]), r"^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}Z$")
            self.assertFalse(pane_file.exists())
            self.assertFalse(list(pane_file.parent.glob(".demo.pane.sh.*")))
            self.assertFalse(list(pane_file.parent.glob(".demo.json.*")))
            self.assertTrue(Path(environment["FLOW_FAKE_DOCKER_LOG"]).exists())
            self.assertFalse(Path(environment["FLOW_FAKE_TMUX_LOG"]).exists())
            self.assert_no_forbidden_commands(environment)

    def test_teardown_dry_run_rejects_each_merge_gate_before_rendering_mutations(self) -> None:
        for gate, status_value, dirty_path, diagnostic in (
            ("status", "NEEDS_HUMAN", None, "member status NEEDS_HUMAN is not DONE"),
            ("tracked", "DONE", "README.md", "tracked uncommitted files"),
            ("untracked", "DONE", "user notes.txt", "non-fleet untracked data exists"),
        ):
            with self.subTest(gate=gate), tempfile.TemporaryDirectory(
                prefix="flow fleet gate parity "
            ) as directory:
                repository, environment, member = self.create_active_member(Path(directory))
                repository = Path(git(repository, "rev-parse", "--show-toplevel").stdout.strip())
                worktree = Path(str(member["worktree_path"]))
                status = worktree / ".planning" / "flow" / "fleet-status.json"
                status.parent.mkdir(parents=True, exist_ok=True)
                if status_value == "DONE":
                    status = self.write_terminal_status(worktree)
                else:
                    status.write_text(json.dumps({"status": status_value}) + "\n", encoding="utf-8")
                if dirty_path == "README.md":
                    (worktree / dirty_path).write_text("# tracked dirty fixture\n", encoding="utf-8")
                elif dirty_path is not None:
                    (worktree / dirty_path).write_text("preserve this fixture\n", encoding="utf-8")
                environment["DRY_RUN"] = "1"
                quoted_worktree = str(worktree).replace(" ", "\\ ")
                quoted_status = str(status).replace(" ", "\\ ")
                member_file = repository / ".planning" / "flow" / "fleet" / "demo.json"
                member_before = member_file.read_bytes()
                status_before = status.read_bytes()
                head_before = git(repository, "rev-parse", "HEAD").stdout
                worktrees_before = git(repository, "worktree", "list", "--porcelain").stdout
                worktree_status_before = git(worktree, "status", "--short").stdout

                result = run_shell(FLEET_TEARDOWN, repository, "demo", "--merge", env=environment)

                self.assertNotEqual(result.returncode, 0)
                self.assertIn(diagnostic, result.stderr)
                self.assertIn(
                    f"STATUS=$(jq -er .status {quoted_status} 2>/dev/null || printf MISSING)",
                    result.stdout,
                )
                self.assertIn(
                    f"if ! git -C {quoted_worktree} diff --quiet || ! git -C {quoted_worktree} "
                    "diff --cached --quiet; then",
                    result.stdout,
                )
                self.assertIn(
                    f"done < <(git -C {quoted_worktree} status --porcelain --untracked-files=all)",
                    result.stdout,
                )
                for mutation in (
                    "docker compose",
                    "tmux kill-window",
                    "git merge --no-ff",
                    "STATUS_BACKUP=$(mktemp",
                    "git worktree remove",
                    "mkdir -p",
                    "cp ",
                    "rm ",
                ):
                    with self.subTest(gate=gate, mutation=mutation):
                        self.assertNotIn(mutation, result.stdout)
                self.assertEqual(git(repository, "rev-parse", "HEAD").stdout, head_before)
                self.assertEqual(git(repository, "worktree", "list", "--porcelain").stdout, worktrees_before)
                self.assertEqual(git(worktree, "status", "--short").stdout, worktree_status_before)
                self.assertEqual(member_file.read_bytes(), member_before)
                self.assertEqual(status.read_bytes(), status_before)
                self.assertFalse(Path(environment["FLOW_FAKE_DOCKER_LOG"]).exists())
                self.assertFalse(Path(environment["FLOW_FAKE_TMUX_LOG"]).exists())
                self.assert_no_forbidden_commands(environment)

    def test_teardown_dry_run_renders_exact_fail_closed_done_merge_and_recovery_flow(self) -> None:
        with tempfile.TemporaryDirectory(prefix="flow fleet parity ") as directory:
            repository, environment, member = self.create_active_member(Path(directory))
            repository = Path(git(repository, "rev-parse", "--show-toplevel").stdout.strip())
            worktree = Path(str(member["worktree_path"]))
            status = worktree / ".planning/flow/fleet-status.json"
            member_file = repository / ".planning/flow/fleet/demo.json"
            pane_file = repository / ".planning/flow/fleet/demo.pane.sh"
            fleet_directory = repository / ".planning/flow/fleet"
            quoted_worktree = str(worktree).replace(" ", "\\ ")
            quoted_status = str(status).replace(" ", "\\ ")
            quoted_fleet_directory = str(fleet_directory).replace(" ", "\\ ")
            quoted_member_file = str(member_file).replace(" ", "\\ ")
            quoted_pane_file = str(pane_file).replace(" ", "\\ ")
            status = self.write_terminal_status(worktree)
            environment["DRY_RUN"] = "1"
            head_before = git(repository, "rev-parse", "HEAD").stdout
            status_before = git(worktree, "status", "--short").stdout

            result = run_shell(FLEET_TEARDOWN, repository, "demo", "--merge", env=environment)

            self.assertEqual(result.returncode, 0, result.stderr)
            plan = result.stdout
            for fragment in (
                "tmux_windows=$(tmux list-windows -t pwdev-flow-fleet -F '#{window_name}' 2>/dev/null) || return 2",
                'while IFS= read -r tmux_name; do [[ $tmux_name == demo ]] && return 0; done <<<"$tmux_windows"',
                "tmux kill-window -t pwdev-flow-fleet:demo",
                "tmux window remains after shutdown",
                "unable to verify tmux window absence",
                "unable to inspect tmux window state",
                f"STATUS=$(jq -er .status {quoted_status} 2>/dev/null || printf MISSING)",
                '[[ $STATUS == DONE ]] || { printf \'fleet-teardown: refusing merge: member status %s is not DONE\\n\' "$STATUS" >&2; exit 1; }',
                f"if ! git -C {quoted_worktree} diff --quiet || ! git -C {quoted_worktree} diff --cached --quiet; then",
                f"done < <(git -C {quoted_worktree} status --porcelain --untracked-files=all)",
                "has_nonfleet_untracked",
                "refusing merge: non-fleet untracked data exists",
            ):
                with self.subTest(fragment=fragment):
                    self.assertIn(fragment, plan)
            self.assertNotIn("grep -Fvx", plan)
            for placeholder in ("<timestamp", "<cleanup", "<restore", "on remove failure", "on remove success"):
                self.assertNotIn(placeholder, plan)
            merge_failure_flow = "\n".join(
                (
                    "if ! git merge --no-ff flow-fleet/demo; then",
                    "  if git rev-parse -q --verify MERGE_HEAD >/dev/null 2>&1; then",
                    "    if git merge --abort; then",
                    "      printf 'fleet-teardown: merge conflict aborted; recovery state preserved\\n' >&2",
                    "    else",
                    "      printf 'fleet-teardown: merge failed and abort failed; manual recovery required\\n' >&2",
                    "    fi",
                    "  else",
                    "    printf 'fleet-teardown: merge failed before a merge state was created; recovery state preserved\\n' >&2",
                    "  fi",
                    "  exit 1",
                    "fi",
                )
            )
            backup_pattern = f"{quoted_fleet_directory}/.demo.status.XXXXXX"
            backup_flow = "\n".join(
                (
                    f"STATUS_BACKUP=$(mktemp {backup_pattern}) || {{ printf 'fleet-teardown: could not preserve recovery status\n' >&2; exit 2; }}",
                    f"cp {quoted_status} \"$STATUS_BACKUP\" || {{ printf 'fleet-teardown: could not preserve recovery status\n' >&2; exit 2; }}",
                    f"rm -f {quoted_worktree}/docker-compose.flow-fleet.yml {quoted_status}",
                    f"if ! git worktree remove {quoted_worktree}; then",
                    f"  mkdir -p {quoted_worktree}/.planning/flow",
                    f"  if cp \"$STATUS_BACKUP\" {quoted_status}; then",
                    '    rm -f "$STATUS_BACKUP"',
                    "    printf 'fleet-teardown: worktree removal failed; recovery status was restored\\n' >&2",
                    "    exit 2",
                    "  fi",
                    "  printf 'fleet-teardown: worktree removal failed; status restore failed; backup preserved at %s\\n' \"$STATUS_BACKUP\" >&2",
                    "  exit 2",
                    "fi",
                    'rm -f "$STATUS_BACKUP"',
                    f"rm -f {quoted_pane_file}; rm {quoted_member_file}",
                )
            )
            self.assertIn(merge_failure_flow, plan)
            self.assertIn(backup_flow, plan)
            self.assertEqual(plan.count(f"mktemp {backup_pattern}"), 1)
            self.assertEqual(plan.count(f'cp {quoted_status} "$STATUS_BACKUP"'), 1)
            self.assertEqual(plan.count(f'cp "$STATUS_BACKUP" {quoted_status}'), 1)
            self.assertEqual(plan.count('rm -f "$STATUS_BACKUP"'), 2)
            self.assertEqual(git(repository, "rev-parse", "HEAD").stdout, head_before)
            self.assertEqual(git(worktree, "status", "--short").stdout, status_before)
            self.assertTrue(status.exists())
            self.assertTrue(member_file.exists())
            self.assertTrue(pane_file.exists())
            self.assertFalse(Path(environment["FLOW_FAKE_DOCKER_LOG"]).exists())
            self.assertFalse(Path(environment["FLOW_FAKE_TMUX_LOG"]).exists())

    def test_missing_compose_v2_fails_before_worktree_creation(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            repository = init_repository(root / "repo")
            create_approved_phase(repository, "demo", tracked=True)
            write_fleet_config(repository)
            environment = self.fake_environment(root, docker_version_exit=19)
            before = git(repository, "worktree", "list", "--porcelain").stdout

            result = self.launch(repository, "demo", environment)

            self.assertEqual(result.returncode, 2)
            self.assertIn("compose", (result.stdout + result.stderr).lower())
            self.assertEqual(git(repository, "worktree", "list", "--porcelain").stdout, before)
            self.assertFalse((repository / ".planning" / "flow" / "fleet" / "demo.json").exists())
            self.assertIn("version", Path(environment["FLOW_FAKE_DOCKER_LOG"]).read_text(encoding="utf-8"))

    def test_malformed_or_overlapping_member_reservations_fail_closed(self) -> None:
        for member_data in (
            {"port_index": "bad", "app_port": 3000, "db_port": 5432},
            {"port_index": 1, "app_port": 3000, "db_port": 5442},
            {"port_index": 0, "app_port": 3000, "db_port": 3000},
        ):
            with self.subTest(member_data=member_data), tempfile.TemporaryDirectory() as directory:
                root = Path(directory)
                repository = init_repository(root / "repo")
                create_approved_phase(repository, "demo", tracked=True)
                write_fleet_config(repository)
                member = write_member(repository, "occupied", 0)
                existing = json.loads(member.read_text(encoding="utf-8"))
                existing.update(member_data)
                member.write_text(json.dumps(existing), encoding="utf-8")
                environment = self.fake_environment(root)

                result = self.launch(repository, "demo", environment)

                self.assertEqual(result.returncode, 2)
                self.assertIn("member", (result.stdout + result.stderr).lower())
                self.assertFalse((repository.parent / "repo-fleet-demo").exists())
                self.assertFalse(Path(environment["FLOW_FAKE_DOCKER_LOG"]).exists())

    def test_teardown_rejects_tampered_member_targets_before_side_effects(self) -> None:
        for key, value in (
            ("worktree_path", "/tmp/not-a-fleet-worktree"),
            ("project_name", "unrelated-project"),
            ("compose_file", "../../unrelated-compose.yml"),
        ):
            with self.subTest(key=key), tempfile.TemporaryDirectory() as directory:
                repository, environment, member = self.create_active_member(Path(directory))
                member_file = repository / ".planning" / "flow" / "fleet" / "demo.json"
                tampered = json.loads(member_file.read_text(encoding="utf-8"))
                tampered[key] = value
                member_file.write_text(json.dumps(tampered), encoding="utf-8")

                result = run_shell(FLEET_TEARDOWN, repository, "demo", env=environment)

                self.assertEqual(result.returncode, 2)
                self.assertTrue(member_file.exists())
                self.assertTrue(Path(str(member["worktree_path"])).is_dir())
                self.assertFalse(Path(environment["FLOW_FAKE_DOCKER_LOG"]).exists())
                self.assertFalse(Path(environment["FLOW_FAKE_TMUX_LOG"]).exists())

    def test_teardown_rejects_missing_or_symlinked_central_pane_before_side_effects(self) -> None:
        for pane_kind in ("missing", "symlink"):
            with self.subTest(pane_kind=pane_kind), tempfile.TemporaryDirectory() as directory:
                repository, environment, member = self.create_active_member(Path(directory))
                pane_file = repository / ".planning" / "flow" / "fleet" / "demo.pane.sh"
                pane_file.unlink()
                if pane_kind == "symlink":
                    pane_file.symlink_to(repository / "README.md")

                result = run_shell(FLEET_TEARDOWN, repository, "demo", env=environment)

                self.assertEqual(result.returncode, 2)
                self.assertIn("pane", (result.stdout + result.stderr).lower())
                self.assertTrue((repository / ".planning" / "flow" / "fleet" / "demo.json").exists())
                self.assertTrue(Path(str(member["worktree_path"])).exists())
                self.assertFalse(Path(environment["FLOW_FAKE_DOCKER_LOG"]).exists())
                self.assertFalse(Path(environment["FLOW_FAKE_TMUX_LOG"]).exists())

    def test_teardown_keeps_bookkeeping_when_tmux_kill_fails(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            repository, environment, _member = self.create_active_member(Path(directory))
            environment["FLOW_FAKE_TMUX_KILL_EXIT"] = "23"

            result = run_shell(FLEET_TEARDOWN, repository, "demo", env=environment)

            self.assertNotEqual(result.returncode, 0)
            self.assertTrue((repository / ".planning" / "flow" / "fleet" / "demo.json").exists())
            self.assertTrue((repository / ".planning" / "flow" / "fleet" / "demo.pane.sh").exists())
            self.assertIn("kill-window", Path(environment["FLOW_FAKE_TMUX_LOG"]).read_text(encoding="utf-8"))

    def test_teardown_keeps_bookkeeping_when_tmux_post_kill_is_indeterminate_or_present(self) -> None:
        for key, value in (("FLOW_FAKE_TMUX_INSPECT_EXIT", "31"), ("FLOW_FAKE_TMUX_KEEP_WINDOW", "1")):
            with self.subTest(key=key), tempfile.TemporaryDirectory() as directory:
                repository, environment, _member = self.create_active_member(Path(directory))
                environment[key] = value

                result = run_shell(FLEET_TEARDOWN, repository, "demo", env=environment)

                self.assertNotEqual(result.returncode, 0)
                self.assertTrue((repository / ".planning" / "flow" / "fleet" / "demo.json").exists())
                self.assertTrue((repository / ".planning" / "flow" / "fleet" / "demo.pane.sh").exists())
                self.assertIn("list-windows", Path(environment["FLOW_FAKE_TMUX_LOG"]).read_text(encoding="utf-8"))

    def test_worktree_remove_and_status_restore_failure_preserves_backup(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            repository, environment, member = self.create_active_member(Path(directory))
            worktree = Path(str(member["worktree_path"]))
            status = worktree / ".planning" / "flow" / "fleet-status.json"
            status.parent.mkdir(parents=True, exist_ok=True)
            status = self.write_terminal_status(worktree)
            (worktree / "result.txt").write_text("done\n", encoding="utf-8")
            self.assertEqual(git(worktree, "add", "result.txt").returncode, 0)
            self.assertEqual(git(worktree, "commit", "-qm", "fixture: result").returncode, 0)
            fake_bin = Path(environment["PATH"])
            write_executable(
                fake_bin / "git",
                'if [ "${1:-}" = worktree ] && [ "${2:-}" = remove ]; then exit 41; fi\n'
                f'exec "{shutil.which("git")}" "$@"',
            )
            write_executable(
                fake_bin / "cp",
                'case "${1:-}" in */.demo.status.*) case "${2:-}" in */fleet-status.json) exit 42 ;; esac ;; esac\n'
                f'exec "{shutil.which("cp")}" "$@"',
            )

            result = run_shell(FLEET_TEARDOWN, repository, "demo", "--merge", env=environment)

            self.assertNotEqual(result.returncode, 0)
            self.assertIn("restore failed", (result.stdout + result.stderr).lower())
            self.assertTrue((repository / ".planning" / "flow" / "fleet" / "demo.json").exists())
            self.assertTrue((repository / ".planning" / "flow" / "fleet" / "demo.pane.sh").exists())
            self.assertTrue(list((repository / ".planning" / "flow" / "fleet").glob(".demo.status.*")))

    def test_done_member_with_user_untracked_file_is_not_merged_or_cleaned(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            repository, environment, member = self.create_active_member(Path(directory))
            worktree = Path(str(member["worktree_path"]))
            status = worktree / ".planning" / "flow" / "fleet-status.json"
            status.parent.mkdir(parents=True, exist_ok=True)
            status = self.write_terminal_status(worktree)
            (worktree / "result.txt").write_text("done\n", encoding="utf-8")
            self.assertEqual(git(worktree, "add", "result.txt").returncode, 0)
            self.assertEqual(git(worktree, "commit", "-qm", "fixture: result").returncode, 0)
            (worktree / "user-untracked.txt").write_text("preserve me\n", encoding="utf-8")

            result = run_shell(FLEET_TEARDOWN, repository, "demo", "--merge", env=environment)

            self.assertNotEqual(result.returncode, 0)
            self.assertIn("untracked", (result.stdout + result.stderr).lower())
            self.assertTrue(status.exists())
            self.assertTrue((repository / ".planning" / "flow" / "fleet" / "demo.json").exists())
            self.assertTrue((repository / ".planning" / "flow" / "fleet" / "demo.pane.sh").exists())
            self.assertFalse((repository / "result.txt").exists())
            self.assertTrue((worktree / "user-untracked.txt").exists())

    def test_sigterm_after_worktree_creation_writes_atomic_recovery_state(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            repository = init_repository(root / "repo")
            create_approved_phase(repository, "demo", tracked=True)
            write_fleet_config(repository)
            environment = self.fake_environment(root, docker_block=True)
            process_environment = {"LC_ALL": "C", **environment}
            process = subprocess.Popen(
                ["/bin/bash", str(FLEET_UP), "demo"],
                cwd=repository,
                env=process_environment,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
            )
            member_file = repository / ".planning" / "flow" / "fleet" / "demo.json"
            deadline = time.monotonic() + 5
            while not Path(environment["FLOW_FAKE_DOCKER_PID"]).exists() and time.monotonic() < deadline:
                time.sleep(0.02)
            self.assertTrue(Path(environment["FLOW_FAKE_DOCKER_PID"]).exists(), "fake Docker did not start")
            process.send_signal(signal.SIGTERM)
            Path(environment["FLOW_FAKE_DOCKER_RELEASE"]).write_text("release\n", encoding="utf-8")
            _stdout, stderr = process.communicate(timeout=5)

            self.assertNotEqual(process.returncode, 0)
            self.assertIn("recovery", stderr.lower())
            member = json.loads(member_file.read_text(encoding="utf-8"))
            self.assertEqual(member["status"], "NEEDS_HUMAN")
            self.assertTrue(member["worktree_created"])
            self.assertTrue(member["docker_attempted"])
            self.assertFalse(list(member_file.parent.glob(".demo.json.*")))


if __name__ == "__main__":
    unittest.main()
