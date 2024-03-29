import os
from enum import Enum


class ChangelogType(Enum):
    # none
    NONE = -1

    # default
    STANDARD = 0

    # follows the Conventional Commit Spec
    CONVENTIONAL = 1

    @staticmethod
    def from_environment():
        # not set or set to empty value should default to NONE

        type = os.getenv("CHANGELOG_TYPE")

        if type:
            for i in ChangelogType:
                if type.isdigit() and int(type) == i.value or type.lower() == i.name.lower():
                    return i

        return ChangelogType.NONE
