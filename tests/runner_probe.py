import contextlib
import hashlib
import io
import json
import os
import tempfile
from pathlib import Path

from training.runner import ExperimentRunner


def runner_fingerprint():
    outcomes = {}
    original_cwd = Path.cwd()
    with tempfile.TemporaryDirectory() as directory:
        os.chdir(directory)
        try:
            for environment in ("simple-target", "space-invaders"):
                for agent_type in ("neural", "dqn"):
                    for mode in ("random", "train", "evaluate"):
                        output = io.StringIO()
                        with contextlib.redirect_stdout(output):
                            runner = ExperimentRunner(
                                environment=environment,
                                agent_type=agent_type,
                                mode=mode,
                                episodes=2,
                                max_steps=12,
                                experiment_name="regression",
                                seed=42,
                            )
                            results = runner.run()
                        payload = (
                            json.dumps(results, sort_keys=True)
                            + runner.results_path.read_text()
                            + output.getvalue()
                        )
                        outcomes[f"{environment}/{agent_type}/{mode}"] = hashlib.sha256(
                            payload.encode()
                        ).hexdigest()
        finally:
            os.chdir(original_cwd)
    return outcomes
