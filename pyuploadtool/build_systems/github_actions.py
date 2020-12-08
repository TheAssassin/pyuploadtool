import os
import re

import github

from . import BuildSystemBase, BuildSystemError
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
            run_id = os.environ["GITHUB_RUN_ID"]
            event_name = os.environ["GITHUB_EVENT_NAME"]
            ref = os.environ["GITHUB_REF"]
            sha = os.environ["GITHUB_SHA"]
            workflow = os.environ["GITHUB_WORKFLOW"]
            run_number = os.environ["GITHUB_RUN_NUMBER"]

        except KeyError as e:
            raise BuildSystemError(f"Could not find environment variable ${e.args[0]}")

        return GitHubActions(repository, run_id, event_name, ref, sha, workflow, run_number)

    def update_release_metadata(self, metadata: ReleaseMetadata):
        # extract tag name, if possible (for release builds)
        tag_match = re.match(r"(?:refs/)?tags/(.+)", self.ref)
        if tag_match:
            metadata.tag_name = tag_match.group(1)
            metadata.release_name = f"Release {metadata.tag_name}"

        metadata.build_log_url = f"https://github.com/{self.repository}/runs/{self.run_id}"
        metadata.unique_build_id = str(self.run_id)
        metadata.repository_slug = self.repository
        metadata.commit = self.commit
        metadata.pipeline_name = self.workflow
        metadata.pipeline_run_number = self.run_number
