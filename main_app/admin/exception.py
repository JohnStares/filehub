
class CannotDeleteAdmin(Exception):
    def __init__(self, message: str) -> None:
        super().__init__(message)


class UserAlreadyExist(Exception):
    def __init__(self, message: str) -> None:
        super().__init__(message)


class EmailAlreadyExist(Exception):
    def __init__(self, message: str) -> None:
        super().__init__(message)


class MessageDoesNotExist(Exception):
    def __init__(self, message: str) -> None:
        super().__init__(message)