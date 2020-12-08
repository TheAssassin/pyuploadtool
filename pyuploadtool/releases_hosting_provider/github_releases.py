import os

from github import Github, UnknownObjectException

from . import ReleaseHostingProviderError
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
            raise ReleaseHostingProviderError(f"could not find required environment variable: {e.args[0]}")

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
            if existing_tag.name == metadata.tag_name and existing_tag.commit.sha != metadata.commit:
                self.logger.warning(f"recreating tag {metadata.tag_name} for commit {metadata.commit}")

                self.logger.debug(f"deleting tag {existing_tag.name}")
                existing_tag_ref = repo.get_git_ref(f"tags/{existing_tag.name}")
                existing_tag_ref.delete()

        try:
            release = repo.get_release(metadata.tag_name)
        except UnknownObjectException:
            release = None

        message = f"Build log: {metadata.build_log_url}"

        if metadata.release_description is not None:
            message = f"{metadata.release_description}\n\n{message}"

        # for some annoying reason, you have to specify all the metadata both when drafting _and_ creating the release
        release_data = dict(
            name=metadata.release_name,
            message=message,
            prerelease=prerelease,
            target_commitish=metadata.commit,
        )

        # in case we have multiple jobs build and upload in parallel, the release may already have been created by
        # one job
        # therefore, we want to make sure we only (re)create the release if it is not based on the commit we're
        # processing right now
        if release is not None:
            if release.target_commitish == metadata.commit:
                self.logger.info(
                    f'found an existing release called "{metadata.release_name}" for commit "{metadata.commit}"'
                )
            else:
                self.logger.warning(f"deleting existing release for tag {metadata.tag_name}")
                release.delete_release()
                release = None

        if release is None:
            self.logger.info(f'drafting new release "{metadata.release_name}" for tag "{metadata.tag_name}"')
            release = repo.create_git_release(tag=metadata.tag_name, draft=True, **release_data)

        for path in artifacts:
            self.logger.info(f'uploading artifact "{path}"')

            # in case there's an existing artifact with the same filename, we need to delete the old file first
            for asset in release.get_assets():
                if asset.name == os.path.basename(path):
                    self.logger.info(f'deleting existing asset {asset.id} with name "{asset.name}"')
                    asset.delete_asset()

            release.upload_asset(path)

        self.logger.info("publishing release")
        # for some annoying reason, you have to re-provide all options
        release.update_release(draft=False, **release_data)

    @property
    def name(self):
        return "GitHub Releases"
