import os
from enum import Enum


class ChangelogType(Enum):
    # default
    STANDARD = 0

    # follows the Conventional Commit Spec
    CONVENTIONAL = 1

    @staticmethod
    def from_environment():
        type = os.getenv("CHANGELOG_TYPE")
        if type is None:
            return ChangelogType.STANDARD

        for i in ChangelogType:
            if type.isdigit() and int(type) == i.value or type == i.name:
                return i

        # fall back to the default
        return ChangelogType.STANDARD
