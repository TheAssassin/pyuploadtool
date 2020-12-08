import os

from . import GitHubActions, BuildSystemError, BuildSystemBase
from ..logger import make_logger


class BuildSystemFactory:
    logger = make_logger("build-system-factory")

    @classmethod
    def from_environment(cls) -> BuildSystemBase:
        cls.logger.info("guessing build system from environment variables")

        if "GITHUB_ACTIONS" in os.environ:
            cls.logger.info("detected GitHub actions environment")
            return GitHubActions.from_environment()

        raise BuildSystemError("failed to guess build system from environment")
