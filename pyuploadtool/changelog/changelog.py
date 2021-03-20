from .commit import ChangelogCommit


class Changelog:
    def __init__(self):
        self._data = dict()
        for spec in self.structure():
            self._data[spec] = list()

    def __repr__(self):
        print(f"{self.__name__}({self._data})")

    def __iter__(self):
        return iter(self._data)

    def __getitem__(self, item):
        return self._data[item]

    @staticmethod
    def structure() -> dict:
        """
        Returns a dictionary with a minimal structure of a changelog.
        All commits would be classified as others by default.
        :return:
        :rtype:
        """
        return {"others": "Commits"}

    def push(self, commit: ChangelogCommit):
        """
        Adds a commit to the changelog
        :return: The classification of the commit = other
        :rtype: str
        """
        self._data["others"].append(commit)
        return "others"

    @property
    def changelog(self) -> dict:
        return self._data
