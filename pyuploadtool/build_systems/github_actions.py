import os

import github

from . import BuildSystemBase, BuildSystemError
from ..logger import make_logger
from ..metadata import ReleaseMetadata


class GitHubActions(BuildSystemBase):
    logger = make_logger("github_actions")

    def __init__(self, github_client, repository, run_id, event_name, ref):
        # dependency injection
        self.github_client: github.Github = github_client

        self.repository = repository
        self.run_id = run_id
        self.event_name = event_name
        self.ref = ref

    @classmethod
    def from_environment(cls):
        try:
            repository = os.environ["GITHUB_REPOSITORY"]
            token = os.environ["GITHUB_TOKEN"]
            run_id = os.environ["GITHUB_RUN_ID"]
            event_name = os.environ["GITHUB_EVENT_NAME"]
            ref = os.environ["GITHUB_REF"]
        except KeyError as e:
            raise BuildSystemError(f"Could not find environment variable ${e.args[0]}")

        github_client = github.Github(token)

        return GitHubActions(github_client, repository, run_id, event_name, ref)

    def update_release_metadata(self, metadata: ReleaseMetadata):
        # TODO: support custom names and tags
        # TODO: update existing release if there's one for the current commit already (travis ci workflow)

        # not using "latest", as this value is reserved by GitHub
        metadata.tag_name = "continuous"
        metadata.release_name = "Continuous build"
        metadata.build_log_url = f"https://github.com/{self.repository}/runs/{self.run_id}"
        metadata.unique_build_id = str(self.run_id)
        metadata.repository_slug = self.repository
