import os

from . import ReleasesHostingProviderBase, GitHubReleases, ReleaseHostingProviderError
from ..logger import make_logger


class ReleasesHostingProviderFactory:
    logger = make_logger("releases-hosting-provider-factory")

    @classmethod
    def from_environment(cls) -> ReleasesHostingProviderBase:
        # TODO: support more than one provider at a time
        cls.logger.info("guessing releases hosting provider from environment variables")

        if "GITHUB_TOKEN" in os.environ:
            cls.logger.info("detected GitHub releases")
            return GitHubReleases.from_environment()

        raise ReleaseHostingProviderError("failed to guess build system from environment")
