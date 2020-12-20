from enum import Enum


class BuildType(Enum):
    # default
    UNKNOWN = 0

    # a normal push to a Git branch
    PUSH = 1

    # a tag was created
    TAG = 2

    # a pull request (merge request, ...) is being built
    PULL_REQUEST = 3

    # a scheduled event, e.g., triggered periodically
    SCHEDULED = 4

    # manual build, triggered by the user
    MANUAL = 5
