import os
from urllib.parse import urljoin, quote

import requests

from . import ReleaseHostingProviderError
from .base import ReleasesHostingProviderBase
from .. import ReleaseMetadata
from ..logging import make_logger


class WebDAV(ReleasesHostingProviderBase):
    logger = make_logger("webdav")

    def __init__(self, url: str, requests_session: requests.Session, release_name: str = None):
        # using dependency injection to allow for easier testing
        self.url = url
        self.requests_session = requests_session
        self.release_name = release_name

    @staticmethod
    def from_environment():
        try:
            url = os.environ["WEBDAV_URL"]
            user = os.environ["WEBDAV_USER"]
            password = os.environ["WEBDAV_PASSWORD"]

            # optional features
            try:
                release_name = os.environ["WEBDAV_RELEASE_NAME"]
            except KeyError:
                release_name = None

        except KeyError as e:
            raise ReleaseHostingProviderError(f"could not find required environment variable: {e.args[0]}")

        session = requests.Session()
        session.auth = (user, password)

        return WebDAV(url, session, release_name)

    def create_release(self, metadata: ReleaseMetadata, artifacts):
        # if the user specifies a release name via env vars, we prefer that one
        if self.release_name:
            self.logger.info(f'using user-specified release name "{self.release_name}"')
            base_url = self.url
            base_url += "/"
            base_url = urljoin(base_url, quote(self.release_name))
            base_url += "/"

        elif metadata.pipeline_name and metadata.pipeline_run_number:
            self.logger.info(f'target directory: "{metadata.pipeline_name}/{metadata.pipeline_run_number}"')
            base_url = self.url
            base_url += "/"
            base_url = urljoin(base_url, quote(metadata.pipeline_name))
            base_url += "/"
            base_url = urljoin(base_url, quote(str(metadata.pipeline_run_number)))
            base_url += "/"

        else:
            raise ReleaseHostingProviderError("cannot determine release name")

        for path in artifacts:
            self.logger.info(f'uploading artifact "{path}"')

            artifact_url = urljoin(base_url, quote(os.path.basename(path)))
            with open(path, "rb") as f:
                response = self.requests_session.put(artifact_url, data=f)
                response.raise_for_status()

        if metadata.build_log_url:
            build_info_filename = "build-info.txt"
            self.logger.info(f"uploading build log URL to {build_info_filename}")
            build_info = f"Build log: {metadata.build_log_url}\n"
            build_info_url = urljoin(base_url, quote(build_info_filename))
            put_response = self.requests_session.put(build_info_url, data=build_info)
            put_response.raise_for_status()

    @property
    def name(self):
        return "WebDAV"
