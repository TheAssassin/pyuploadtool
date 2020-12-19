import os
import re

from . import BuildSystemBase, BuildSystemError
from .. import BuildType
from ..logging import make_logger
from ..metadata import ReleaseMetadata


class GitHubActions(BuildSystemBase):
    logger = make_logger("github_actions")

    def __init__(self, repository, run_id, event_name, ref, sha, workflow, run_number):
        # dependency injection
        self.repository = repository
        self.run_id = run_id
        self.event_name = event_name
        self.ref = ref
        self.commit = sha
        self.workflow = workflow
        self.run_number = run_number

    @classmethod
    def from_environment(cls):
        try:
            repository = os.environ["GITHUB_REPOSITORY"]
            run_id = int(os.environ["GITHUB_RUN_ID"])
            event_name = os.environ["GITHUB_EVENT_NAME"]
            ref = os.environ["GITHUB_REF"]
            sha = os.environ["GITHUB_SHA"]
            workflow = os.environ["GITHUB_WORKFLOW"]
            run_number = int(os.environ["GITHUB_RUN_NUMBER"])

        except KeyError as e:
            raise BuildSystemError(f"Could not find environment variable ${e.args[0]}")

        return GitHubActions(repository, run_id, event_name, ref, sha, workflow, run_number)

    def update_release_metadata(self, metadata: ReleaseMetadata):
        # extract tag name, if possible (for release builds)
        branch_match = re.match(r"(?:refs/)?tags/(.+)", self.ref)
        if branch_match:
            metadata.tag = branch_match.group(1)

        branch_match = re.match(r"(?:refs/)?heads/(.+)", self.ref)
        if branch_match:
            metadata.branch = branch_match.group(1)

        metadata.build_log_url = f"https://github.com/{self.repository}/actions/runs/{self.run_id}"
        metadata.unique_build_id = str(self.run_id)
        metadata.repository_slug = self.repository
        metadata.commit = self.commit
        metadata.pipeline_name = self.workflow
        metadata.pipeline_run_number = self.run_number

        event_name = self.event_name.lower()

        # the create event can occur whenever a tag or branch is created
        if event_name == "pull_request":
            metadata.build_type = BuildType.PULL_REQUEST
        elif event_name == "push":
            if metadata.tag:
                metadata.build_type = BuildType.TAG
            else:
                metadata.build_type = BuildType.PUSH

        elif event_name == "schedule":
            metadata.build_type = BuildType.SCHEDULED

        elif event_name in ["workflow_dispatch", "repository_dispatch"]:
            metadata.build_type = BuildType.MANUAL

        else:
            raise BuildSystemError("Could not detect build type or build type is unsupported")
