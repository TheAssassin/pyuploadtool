import os

from github import Github, UnknownObjectException

from .base import ReleasesHostingProviderBase
from .. import ReleaseMetadata
from ..exceptions import PyUploadtoolError
from ..logging import make_logger


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

        prerelease = False

        # fallback values (for continuous release setup)
        if not metadata.tag_name:
            self.logger.warning("tag name not set, assuming this is a continuous release setup")

            # not using "latest", as this value is reserved by GitHub
            metadata.tag_name = "continuous"
            metadata.release_name = "Continuous build"
            prerelease = True

        # recreate existing tag if it has the same name but is based on a different commit
        # this usually happens with continuous releases
        # deleting the tag is safe in this case
        for existing_tag in repo.get_tags():
            if existing_tag.name == metadata.tag_name and existing_tag.commit != metadata.commit:
                self.logger.warning(f"recreating tag {metadata.tag_name} for commit {metadata.commit}")

                self.logger.debug(f"deleting tag {existing_tag.name}")
                existing_tag_ref = repo.get_git_ref(f"tags/{existing_tag.name}")
                existing_tag_ref.delete()

        try:
            old_release = repo.get_release(metadata.tag_name)
        except UnknownObjectException:
            old_release = None

        if old_release is not None:
            self.logger.warning(f"deleting existing release for tag {metadata.tag_name}")
            old_release.delete_release()

        message = f"Build log: {metadata.build_log_url}"

        self.logger.info(f'drafting new release "{metadata.release_name}" for tag "{metadata.tag_name}"')

        # for some annoying reason, you have to specify all the metadata both when drafting _and_ creating the release
        release_data = dict(
            name=metadata.release_name,
            message=message,
            prerelease=prerelease,
            target_commitish=metadata.commit,
        )

        draft = repo.create_git_release(tag=metadata.tag_name, draft=True, **release_data)

        for path in artifacts:
            self.logger.info(f'uploading artifact "{path}"')
            draft.upload_asset(path)

        self.logger.info("publishing release")
        # for some annoying reason, you have to re-provide all options
        draft.update_release(draft=False, **release_data)

    @property
    def name(self):
        return "GitHub Releases"
