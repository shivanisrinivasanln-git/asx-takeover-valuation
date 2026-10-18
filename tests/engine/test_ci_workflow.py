"""The CI workflow deploys to GitHub Pages only from a green main branch (task P7-01).

The deploy job needs the checks job, so a failing check stops it, and it runs only for a push to
main, so another branch or a pull request never deploys. The uploaded site is the one the checks
built. Every action is pinned to a commit and every downloaded tool to its checksum.
"""

import re
from pathlib import Path
from typing import Any

import pytest
import yaml

ROOT = Path(__file__).resolve().parents[2]
WORKFLOW = ROOT / ".github" / "workflows" / "ci.yml"
MAIN_PUSH_ONLY = "github.event_name == 'push' && github.ref == 'refs/heads/main'"
FULL_SHA = re.compile(r"^[0-9a-f]{40}$")


@pytest.fixture(scope="module")
def workflow() -> dict[str, Any]:
    loaded: dict[str, Any] = yaml.safe_load(WORKFLOW.read_text(encoding="utf-8"))
    return loaded


def steps(workflow: dict[str, Any], job: str) -> list[dict[str, Any]]:
    found: list[dict[str, Any]] = workflow["jobs"][job]["steps"]
    return found


def step_named(workflow: dict[str, Any], job: str, name: str) -> dict[str, Any]:
    return next(step for step in steps(workflow, job) if step.get("name") == name)


def test_the_deploy_job_waits_for_the_checks_and_runs_only_for_a_push_to_main(
    workflow: dict[str, Any],
) -> None:
    deploy = workflow["jobs"]["deploy"]
    assert deploy["needs"] == "checks"
    assert deploy["if"] == MAIN_PUSH_ONLY
    assert deploy["environment"]["name"] == "github-pages"


def test_only_the_deploy_job_may_write_to_pages(workflow: dict[str, Any]) -> None:
    assert workflow["permissions"] == {"contents": "read"}
    assert workflow["jobs"]["deploy"]["permissions"] == {"pages": "write", "id-token": "write"}
    assert "permissions" not in workflow["jobs"]["checks"]


def test_the_uploaded_site_is_the_one_the_checks_built(workflow: dict[str, Any]) -> None:
    names = [step.get("name") for step in steps(workflow, "checks")]
    upload = step_named(workflow, "checks", "Upload the site for Pages")
    assert names.index("Full check") < names.index("Upload the site for Pages")
    assert names.index("Lighthouse budgets on every page") < names.index(
        "Upload the site for Pages"
    )
    assert upload["if"] == MAIN_PUSH_ONLY
    assert upload["with"]["path"] == "build/site"


def test_every_action_is_pinned_to_a_full_commit(workflow: dict[str, Any]) -> None:
    uses = [
        step["uses"] for job in workflow["jobs"] for step in steps(workflow, job) if "uses" in step
    ]
    assert len(uses) >= 4
    for use in uses:
        assert FULL_SHA.match(use.split("@")[1]), use


@pytest.mark.parametrize(
    ("name", "version"),
    [("Install Typst 0.15.1", "v0.15.1"), ("Install Node 24.21.0", "v24.21.0")],
)
def test_each_downloaded_tool_is_pinned_and_checked(
    workflow: dict[str, Any], name: str, version: str
) -> None:
    step = step_named(workflow, "checks", name)
    url = next(value for key, value in step["env"].items() if key.endswith("_URL"))
    checksum = next(value for key, value in step["env"].items() if key.endswith("_SHA256"))
    assert f"/{version}/" in url
    assert re.fullmatch(r"[0-9a-f]{64}", checksum)
    assert "sha256sum --check --strict" in step["run"]
