import os
from typing import List

from . import ReleasesHostingProviderBase, GitHubReleases, WebDAV
from ..logging import make_logger


class ReleasesHostingProviderFactory:
    logger = make_logger("releases-hosting-provider-factory")

    @classmethod
    def from_environment(cls) -> List[ReleasesHostingProviderBase]:
        providers = []

        # TODO: support more than one provider at a time
        cls.logger.info("guessing releases hosting provider from environment variables")

        if "WEBDAV_URL" in os.environ:
            cls.logger.info("detected WebDAV")
            providers.append(WebDAV.from_environment())

        if "GITHUB_TOKEN" in os.environ:
            cls.logger.info("detected GitHub releases")
            providers.append(GitHubReleases.from_environment())

        return providers
