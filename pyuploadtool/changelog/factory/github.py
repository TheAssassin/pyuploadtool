import github

from typing import Optional
from github import Github
from github.GitRelease import GitRelease

from .. import Changelog
from .base import ChangelogFactory
from ..commit import ChangelogEntry
from ...metadata import ReleaseMetadata
from ...logging import make_logger


class GitHubChangelogFactory(ChangelogFactory):
    logger = make_logger("github-changelog-generator")

    def __init__(self, github_client: Github, metadata: ReleaseMetadata):
        """
        Prepares the changelog using GitHub REST API by
        comparing the current commit against the latest release (pre-release / stable)
        """
        super().__init__()
        self.metadata = metadata
        self.github_client = github_client
        self.repository = github_client.get_repo(metadata.repository_slug)

    def get_latest_release(self):
        """
        Gets the latest release by semver, like v8.0.1, v4.5.9, if not
        Fallback to continuous releases, like 'continuous', 'stable', 'nightly'

        :return: the tag name of the latest release, and the date on which it was created
        :rtype: GitRelease
        """

        releases = self.repository.get_releases()
        latest_release = None
        rolling_release = None
        for release in releases:
            if not release.tag_name.startswith("v") or not release.tag_name[0].isdigit():
                # the release does not follow semver specs

                if rolling_release is None or (rolling_release and release.created_at > rolling_release.created_at):
                    # probably, we are looking at a rolling release
                    # like 'continuous', 'beta', etc..
                    rolling_release = release

            elif latest_release is None:
                # we still dont have a latest release,
                # so we need to set whatever release we currently are at
                # as the latest release
                latest_release = release

            elif release.created_at > latest_release.created_at:
                # we found a release for which, the current release is newer
                # than the stored one
                latest_release = release

        # we found a release which does not follow
        # semver specs, and it is a probably a rolling release
        # just provide that as the latest release
        # so we need to return that, if we didnt find a suitable latest_release
        return latest_release or rolling_release

    def get_commits_since(self, tag) -> Optional[github.Comparison.Comparison]:
        """
        Gets all the commits since a tag to self.commit_sha
        :return
        """
        try:
            commits = self.repository.compare(tag, self.metadata.commit).commits
        except Exception as e:
            self.logger.warn(
                f"Failed to compared across {tag} and " f"{self.metadata.commit}: {e}. " f"Not generating changelog."
            )
            return list()
        return commits

    def get_changelog(self):
        """
        Wrapper command to generate the changelog
        :return: markdown data as changelog
        :rtype: Changelog
        """

        latest_release = self.get_latest_release()

        if latest_release is None:
            # We couldn't find out the latest release. Lets stick with
            # the commit above the commit we are working against.

            # FIXME: Looks like it works fine... Need some tests here
            latest_release = f"{self.metadata.commit}^1"
        else:
            latest_release = latest_release.tag_name

        commits = self.get_commits_since(latest_release)
        self.logger.debug(f"Found {len(commits)} commits")

        changelog = self.changelog_generator()

        for commit in commits:
            changelog.push(ChangelogEntry.from_github_commit(commit))

        return changelog
