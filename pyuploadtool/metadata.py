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
        build_log_url: str = None,
        unique_build_id: str = None,
        repository_slug: str = None,
    ):
        # name of the tag to be created
        self.tag_name = tag_name

        # name of the release to be created (might be the same as tag_name)
        self.release_name = release_name

        # URL to build log
        self.build_log_url = build_log_url

        # an ID unique to the running build (e.g., build/run number)
        # example use case: allow release hosting provider implementations to handle duplicate build runs properly
        self.unique_build_id = unique_build_id

        # repository slug
        # this is required by releases hosting platforms such as GitHub releases
        self.repository_slug = repository_slug

    def __repr__(self):
        args = ", ".join(
            (f'{i}="{getattr(self, i)}"' for i in ("tag_name", "release_name", "build_log_url", "repository_slug"))
        )

        return f"<{self.__class__.__name__}({args})>"
