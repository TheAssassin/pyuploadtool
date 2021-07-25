import os

from enum import Enum
from github import Github, UnknownObjectException

from . import ReleaseHostingProviderError
from .base import ReleasesHostingProviderBase
from .. import ReleaseMetadata, BuildType
from ..logging import make_logger


class GitHubReleaseTypes(Enum):
    STABLE = "stable"
    PRERELEASE = "prerelease"


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
        if metadata.build_type in [BuildType.SCHEDULED, BuildType.MANUAL, BuildType.PUSH]:
            if metadata.build_type == BuildType.PUSH:
                if metadata.branch != repo.default_branch:
                    self.logger.warning(
                        f'not creating release for branch "{metadata.branch}" as it is not the default branch '
                        f'"{repo.default_branch}"'
                    )
                    return

            else:
                if not metadata.branch:
                    metadata.branch = repo.default_branch

                elif metadata.branch == repo.default_branch:
                    pass

                else:
                    raise ReleaseHostingProviderError(
                        f'refusing to create continuous release for non-default branch "{metadata.branch}" '
                        f'(build type {metadata.build_type}, default branch "{repo.default_branch}")'
                    )

            self.logger.warning("push to default branch, creating continuous release")

            # not using "latest", as this value is reserved by GitHub
            metadata.tag = os.getenv("GITHUB_CONTINUOUS_RELEASE_TAG", "continuous")
            metadata.release_name = os.getenv("GITHUB_CONTINUOUS_RELEASE_NAME", "Continuous build")
            prerelease = (
                os.getenv("GITHUB_CONTINUOUS_RELEASE_TYPE", GitHubReleaseTypes.PRERELEASE.value)
                == GitHubReleaseTypes.PRERELEASE.value
            )

        elif metadata.build_type == BuildType.PULL_REQUEST:
            self.logger.warning("not creating release as this is a pull request build")
            return

        elif metadata.build_type == BuildType.TAG:
            self.logger.info("build of tag, creating regular release")

            if not metadata.release_name:
                metadata.release_name = f"Release {metadata.tag}"
                self.logger.info(f"automatically using tag name as release name: {metadata.release_name}")

        else:
            raise ReleaseHostingProviderError(f"unsupported build type: {metadata.build_type}")

        # recreate existing tag if it has the same name but is based on a different commit
        # this usually happens with continuous releases
        # deleting the tag is safe in this case
        for existing_tag in repo.get_tags():
            if existing_tag.name == metadata.tag and existing_tag.commit.sha != metadata.commit:
                self.logger.warning(f"recreating tag {metadata.tag} for commit {metadata.commit}")

                self.logger.debug(f"deleting tag {existing_tag.name}")
                existing_tag_ref = repo.get_git_ref(f"tags/{existing_tag.name}")
                existing_tag_ref.delete()

        try:
            release = repo.get_release(metadata.tag)
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
                self.logger.warning(f"deleting existing release for tag {metadata.tag}")
                release.delete_release()
                release = None

        if release is None:
            self.logger.info(f'drafting new release "{metadata.release_name}" for tag "{metadata.tag}"')
            release = repo.create_git_release(tag=metadata.tag, draft=True, **release_data)

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
