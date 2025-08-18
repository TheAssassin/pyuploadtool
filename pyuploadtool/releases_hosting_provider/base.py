import os
from typing import Iterable

from .. import ReleaseMetadata


class ReleasesHostingProviderBase:
    @property
    def name(self):
        raise NotImplementedError

    @staticmethod
    def get_environment_variable(name):
        """
        Small utility to fetch (populated) environment variables.

        In CI environments like GitHub actions, environment variables may be empty in, e.g., pull request builds, as
        the according secret is not available in these builds.

        Basically a wrapper for  os.environ[...], but it also raises a KeyError in case the value is empty.

        :param name: Name of the environment variable
        :raise KeyError: if value is empty or the variable is not set at all
        :return: value of environment variable
        """

        value = os.environ[name]

        if not value:
            raise ValueError(f'Environment variable has empty value set: "{name}"')

        return value

    @staticmethod
    def from_environment():
        """
        Create new instance from environment variables.
        Variables to be set vary from implementation to implementation.
        :return: new instance
        """
        raise NotImplementedError

    def create_release(self, metadata: ReleaseMetadata, artifacts: Iterable[str]):
        """
        Create new release on hosting provider from the provided metadata and upload provided artifacts there.
        :param metadata: metadata to create release from
        :param artifacts: files to be uploaded into the release
        """

        raise NotImplementedError
