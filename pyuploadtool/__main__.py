"""
Commandline interface.
"""

import sys


from pyuploadtool import (
    ReleaseMetadata,
    ReleasesHostingProviderFactory,
    update_metadata_with_user_specified_data,
    BuildSystemFactory,
)
from pyuploadtool.logging import make_logger, setup_logging

setup_logging()

logger = make_logger("cli")

# TODO: use some real CLI library
artifacts = sys.argv[1:]


def get_metadata():
    # create some metadata, which will be updated with the data from the build system
    logger.debug("creating empty metadata object")
    metadata = ReleaseMetadata()

    # the tool is supposed to run as part of some CI/CD workflow
    # therefore, we try to guess the build system from the environment
    # TODO: support specifying a build system explicitly
    logger.debug("detecting release metadata from build environment")
    build_system = BuildSystemFactory.from_environment()
    build_system.update_release_metadata(metadata)

    # TODO: support overwriting release metadata with environment variables
    # this should be done in some function or class which updates

    return metadata


def create_releases_hosting_provider():
    # try to guess the releases hosting provider from the environment, too
    logger.debug("creating release hosting provider instance from build environment")
    releases_hosting_provider = ReleasesHostingProviderFactory.from_environment()

    return releases_hosting_provider


logger.info("collecting release metadata")
metadata = get_metadata()
logger.info("build metadata: %s", metadata)

logger.info("updating metadata with user-specified values (if any)")
update_metadata_with_user_specified_data(metadata)

# TODO: support uploading to more than one provider
releases_hosting_provider = create_releases_hosting_provider()
logger.info("creating release to provider %s", releases_hosting_provider.name)
releases_hosting_provider.create_release(metadata, artifacts)

logger.info("done!")
