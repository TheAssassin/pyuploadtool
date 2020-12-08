import os


class ReleaseMetadata:
    """
    Data object holding all metadata about a release that can be gathered from, e.g., a build system's environment.

    All the data is optional. Release hosting providers have to either handle missing values, or raise an exception if
    mandatory data is missing.

    Release metadata instances are created by the user and then handed to, e.g., build systems, to fill in data.
    """

    def __init__(
        self,
        tag_name: str = None,
        release_name: str = None,
        release_description: str = None,
        build_log_url: str = None,
        unique_build_id: str = None,
        repository_slug: str = None,
        commit: str = None,
        pipeline_name: str = None,
        pipeline_run_number: str = None,
    ):
        # name of the tag to be created
        self.tag_name = tag_name

        # name of the release to be created (might be the same as tag_name)
        self.release_name = release_name

        # optional release description
        # will be prepended to the auto-generated description for release hosting platforms that support descriptions
        self.release_description = release_description

        # URL to build log
        self.build_log_url = build_log_url

        # an ID unique to the running build (e.g., build/run number)
        # example use case: allow release hosting provider implementations to handle duplicate build runs properly
        self.unique_build_id = unique_build_id

        # repository slug
        # this is required by releases hosting platforms such as GitHub releases
        self.repository_slug = repository_slug

        # Git commit hash
        self.commit = commit

        # build pipeline metadata
        # used to determine the release directory name in hosting providers such as WebDAV
        self.pipeline_name = pipeline_name
        # the run number shall be monotonically increasing, and start at 0 or 1
        self.pipeline_run_number = pipeline_run_number

    def __repr__(self):
        args = ", ".join(
            (
                f'{i}="{getattr(self, i)}"'
                for i in (
                    "tag_name",
                    "release_name",
                    "build_log_url",
                    "repository_slug",
                    "commit",
                    "pipeline_name",
                    "pipeline_run_number",
                )
            )
        )

        return f"<{self.__class__.__name__}({args})>"


def update_metadata_with_user_specified_data(metadata: ReleaseMetadata):
    """
    Update metadata with values from environment variables users may specify. This can be used to overwrite
    auto-detected values or provide additional data the auto detection can't determine itself.

    :param metadata: metadata to update
    """

    # probonopd/uploadtool compatibility
    try:
        metadata.description = os.environ["UPLOADTOOL_BODY"]
    except KeyError:
        pass
