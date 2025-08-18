import os
from typing import List

from . import ReleasesHostingProviderBase, GitHubReleases, WebDAV
from ..logging import make_logger


class ReleasesHostingProviderFactory:
    logger = make_logger("releases-hosting-provider-factory")

    @classmethod
    def from_environment(cls) -> List[ReleasesHostingProviderBase]:
        providers = []

        cls.logger.info("guessing releases hosting provider from environment variables")

        if os.getenv("WEBDAV_URL", None):
            cls.logger.info("detected WebDAV")
            providers.append(WebDAV.from_environment())

        if os.getenv("GITHUB_TOKEN", None):
            cls.logger.info("detected GitHub releases")
            providers.append(GitHubReleases.from_environment())

        return providers
