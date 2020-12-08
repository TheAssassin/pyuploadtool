from typing import Iterable

from .. import ReleaseMetadata


class ReleasesHostingProviderBase:
    @property
    def name(self):
        raise NotImplementedError

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
