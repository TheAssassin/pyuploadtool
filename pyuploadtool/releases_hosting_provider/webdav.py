import os
import string
from urllib.parse import quote

import requests

from . import ReleaseHostingProviderError
from .base import ReleasesHostingProviderBase
from .. import ReleaseMetadata, BuildType
from ..logging import make_logger


class WebDAV(ReleasesHostingProviderBase):
    logger = make_logger("webdav")

    def __init__(self, url: str, requests_session: requests.Session, release_name: str = None):
        # using dependency injection to allow for easier testing
        self.url = url
        self.requests_session = requests_session
        self.release_name = release_name

    @classmethod
    def from_environment(cls):
        try:
            url = cls.get_environment_variable("WEBDAV_URL")
            user = cls.get_environment_variable("WEBDAV_USER")
            password = cls.get_environment_variable("WEBDAV_PASSWORD")

            # optional features
            try:
                release_name = cls.get_environment_variable("WEBDAV_RELEASE_NAME")
            except KeyError:
                release_name = None

        except KeyError as e:
            raise ReleaseHostingProviderError(f"could not find required environment variable: {e.args[0]}")

        session = requests.Session()
        session.auth = (user, password)

        return WebDAV(url, session, release_name)

    def create_release(self, metadata: ReleaseMetadata, artifacts):
        def sanitize(s):
            out = []

            for i in str(s):
                if i in string.ascii_letters + string.digits + "_- ":
                    out.append(i)
                else:
                    out.append("_")

            return quote("".join(out))

        # credentials would be missing anyway in a pull request build
        if metadata.build_type == BuildType.PULL_REQUEST:
            self.logger.warning("not uploading to server as this is a pull request build")
            return

        # if the user specifies a release name via env vars, we prefer that one
        # note: we permit an empty string to allow for uploading to the specified URL's root directory
        if self.release_name is not None:
            self.logger.info(f'using user-specified release name "{self.release_name}"')
            target_directory = sanitize(self.release_name)

        elif metadata.pipeline_name and metadata.pipeline_run_number:
            target_directory = f"{sanitize(metadata.pipeline_name)}/{sanitize(metadata.pipeline_run_number)}"

        else:
            raise ReleaseHostingProviderError("cannot determine base URL")

        self.logger.info(f'target directory: "{target_directory}"')

        # avoid consecutive / in URLs, as some webservers don't like these
        while "//" in target_directory:
            target_directory = target_directory.replace("//", "/")

        base_url = f"{self.url}/{target_directory}"
        base_url = base_url.rstrip("/")

        for path in artifacts:
            self.logger.info(f'uploading artifact "{path}"')

            artifact_url = f"{base_url}/{quote(os.path.basename(path))}"
            with open(path, "rb") as f:
                response = self.requests_session.put(artifact_url, data=f)
                response.raise_for_status()

        if metadata.build_log_url:
            build_info_filename = "build-info.txt"
            self.logger.info(f"uploading build log URL to {build_info_filename}")
            build_info = f"Build log: {metadata.build_log_url}\n"
            build_info_url = f"{base_url}/{quote(build_info_filename)}"
            put_response = self.requests_session.put(build_info_url, data=build_info)
            put_response.raise_for_status()

    @property
    def name(self):
        return "WebDAV"
