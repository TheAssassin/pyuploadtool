from ..metadata import ReleaseMetadata


class BuildSystemBase:
    @staticmethod
    def from_environment():
        """
        Instantiate build system from provided environment variables.
        """

        raise NotImplementedError

    def update_release_metadata(self, metadata: ReleaseMetadata):
        """
        Update provided metadata with all data available in the build environment.
        :arg metadata: metadata object to be updated
        """

        raise NotImplementedError
