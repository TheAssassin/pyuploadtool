class Author:
    def __init__(
        self,
        name: str = None,
        email: str = None,
    ):
        self._name = name
        self._email = email

    @property
    def name(self):
        return self._name

    @property
    def email(self):
        return self._email
