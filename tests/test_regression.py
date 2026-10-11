"""Behavior and integration contracts preserved by the refactor."""

import ast
import importlib
import json
import os
import subprocess
import sys
import unittest
from pathlib import Path

os.environ.setdefault("PYGAME_HIDE_SUPPORT_PROMPT", "1")

from tests.behavior_probe import fingerprint
from tests.runner_probe import runner_fingerprint
from training.config import ExperimentConfig

ROOT = Path(__file__).resolve().parents[1]
FIXTURES = Path(__file__).parent / "fixtures"


class RegressionTests(unittest.TestCase):
    def test_original_environment_and_learning_behavior(self):
        expected = json.loads((FIXTURES / "behavior.json").read_text())
        actual = fingerprint()
        for scenario, digest in expected.items():
            with self.subTest(scenario=scenario):
                self.assertEqual(digest, actual[scenario])

    def test_original_boundaries_and_rendering(self):
        from tests.render_probe import rendering_fingerprint

        expected = json.loads((FIXTURES / "rendering.json").read_text())
        self.assertEqual(expected, rendering_fingerprint())

    def test_original_experiment_outputs(self):
        expected = json.loads((FIXTURES / "runner.json").read_text())
        actual = runner_fingerprint()
        for scenario, digest in expected.items():
            with self.subTest(scenario=scenario):
                self.assertEqual(digest, actual[scenario])

    def test_all_canonical_modules_import(self):
        for folder in ("application", "agents", "game_env", "training"):
            for path in (ROOT / folder).rglob("*.py"):
                module_name = ".".join(path.relative_to(ROOT).with_suffix("").parts)
                with self.subTest(module=module_name):
                    importlib.import_module(module_name)

    def test_obsolete_modules_are_absent(self):
        obsolete = (
            "game_env.agent",
            "game_env.hud",
            "game_env.settings",
            "game_env.controllers.action",
            "game_env.building",
            "game_env.city",
            "game_env.pixel_art",
            "game_env.stats",
            "game_env.wave_manager",
            "training.n_step_buffer",
            "training.replay_buffer",
            "agents.training_history",
            "game_env.entities.enemy",
        )
        for module_name in obsolete:
            with self.subTest(module=module_name):
                self.assertFalse((ROOT / module_name.replace(".", "/")).exists())
                self.assertFalse(
                    (ROOT / (module_name.replace(".", "/") + ".py")).exists()
                )
        for folder in (
            "application",
            "agents",
            "game_env",
            "training",
            "experiments",
            "tests",
        ):
            for path in (ROOT / folder).rglob("*.py"):
                for node in ast.walk(ast.parse(path.read_text())):
                    imports = []
                    if isinstance(node, ast.ImportFrom):
                        imports.append(node.module or "")
                    elif isinstance(node, ast.Import):
                        imports.extend(alias.name for alias in node.names)
                    for name in imports:
                        with self.subTest(path=path, module=name):
                            self.assertFalse(
                                any(
                                    name == old or name.startswith(old + ".")
                                    for old in obsolete
                                )
                            )

    def test_configuration_rejects_original_invalid_inputs(self):
        cases = [
            ({"mode": "invalid"}, "Unknown mode: invalid"),
            ({"environment": "invalid"}, "Unknown environment: invalid"),
            ({"agent_type": "invalid"}, "Unknown agent type: invalid"),
            ({"episodes": 0}, "episodes must be >= 1"),
            ({"max_steps": 0}, "max_steps must be >= 1"),
            ({"n_steps": 0}, "n_steps must be >= 1"),
            ({"max_stagnation_steps": 0}, "max_stagnation_steps must be >= 1"),
            ({"debug_last_steps": 0}, "debug_last_steps must be >= 1"),
        ]
        for options, message in cases:
            with self.subTest(options=options):
                with self.assertRaises(ValueError) as error:
                    ExperimentConfig(**options)
                self.assertEqual(message, str(error.exception))
        self.assertIsNone(
            ExperimentConfig(max_stagnation_steps=None).max_stagnation_steps
        )

    def test_layers_do_not_depend_on_experiment_orchestration(self):
        for folder in (
            "agents",
            "game_env/core",
            "game_env/contracts",
            "game_env/observations",
        ):
            for path in (ROOT / folder).rglob("*.py"):
                tree = ast.parse(path.read_text())
                for node in ast.walk(tree):
                    if isinstance(node, ast.ImportFrom):
                        with self.subTest(path=path, module=node.module):
                            self.assertFalse((node.module or "").startswith("training"))

    def test_simple_target_and_agents_do_not_load_pygame(self):
        command = (
            "import sys; from game_env.core.simple_target import SimpleTargetEnv; "
            "from agents.dqn_agent import DQNAgent; "
            "assert 'pygame' not in sys.modules"
        )
        subprocess.run(
            [sys.executable, "-c", command], cwd=ROOT, check=True, capture_output=True
        )


if __name__ == "__main__":
    unittest.main()
