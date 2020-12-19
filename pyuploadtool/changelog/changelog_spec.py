import re

from .changelog import Changelog
from .commit import ChangelogEntry


class ConventionalCommitChangelog(Changelog):
    @staticmethod
    def structure() -> dict:
        """
        Returns a structure of the Conventional Commit Spec
        according to https://cheatography.com/albelop/cheat-sheets/conventional-commits/

        The order of the commits in the dictionary is according to the
        priority
        :return:
        :rtype:
        """
        return {
            "feat": "Features",
            "fix": "Bug Fixes",
            "perf": "Performance Improvements",
            "docs": "Documentation",
            "ci": "Continuous Integration",
            "refactor": "Refactoring",
            "test": "Tests",
            "build": "Builds",
            "revert": "Reverts",
            "chore": "Chores",
            "others": "Commits",
        }

    def push(self, commit: ChangelogEntry) -> str:
        """
        Adds a commit to the changelog and aligns each commit
        based on their category. See self.structure
        :param commit
        :type commit: ChangelogEntry
        :return: The classification of the commit == self.structure.keys()
        :rtype: str
        """

        for spec in self.structure():
            if commit.message.startswith(f"{spec}:"):
                commit.message = commit.message[len(f"{spec}:") + 1 :].strip()
                self._data[spec].append(commit)
                return spec
            elif re.search(f"{spec}.*(.*):.*", commit.message):
                commit.message = commit.message[commit.message.find(":") + 1 :].strip()
                self._data[spec].append(commit)
                return spec

        # it did not fit into any proper category, lets push to others
        self._data["others"].append(commit)
        return "others"
