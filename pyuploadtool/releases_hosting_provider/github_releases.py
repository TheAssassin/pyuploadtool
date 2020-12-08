import os

from github import Github, UnknownObjectException

from .base import ReleasesHostingProviderBase
from .. import ReleaseMetadata
from ..exceptions import PyUploadtoolError
from ..logger import make_logger


class GitHubReleases(ReleasesHostingProviderBase):
    logger = make_logger("github-releases")

    def __init__(self, github_client: Github):
        # using dependency injection to allow for easier testing
        self.github_client = github_client

    @staticmethod
    def from_environment():
        try:
            github_client = Github(os.environ["GITHUB_TOKEN"])
        except KeyError as e:
            raise PyUploadtoolError(f"could not find required environment variable: {e.args[0]}")

        return GitHubReleases(github_client)

    def create_release(self, metadata: ReleaseMetadata, artifacts):
        repo = self.github_client.get_repo(metadata.repository_slug)

        try:
            old_release = repo.get_release(metadata.tag_name)
        except UnknownObjectException:
            old_release = None

        if old_release is not None:
            self.logger.warning(f"deleting existing release for tag {metadata.tag_name}")
            old_release.delete_release()

        message = f"Build log: {metadata.build_log_url}"

        self.logger.info(f'drafting new release "{metadata.release_name}" for tag "{metadata.tag_name}"')
        draft = repo.create_git_release(tag=metadata.tag_name, name=metadata.release_name, message=message, draft=True)

        for path in artifacts:
            self.logger.info(f'uploading artifact "{path}"')
            draft.upload_asset(path)

        self.logger.info("publishing release")
        # for some annoying reason, you have to re-provide name and message
        draft.update_release(name=metadata.release_name, message=message, draft=False)

    @property
    def name(self):
        return "GitHub Releases"
