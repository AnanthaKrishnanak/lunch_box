class AppError(Exception):
    """Base class for domain errors."""


class NotFoundError(AppError):
    def __init__(self, entity: str, identifier: int | str) -> None:
        self.entity = entity
        self.identifier = identifier
        super().__init__(f"{entity} with id={identifier} not found")


class ConflictError(AppError):
    def __init__(self, message: str) -> None:
        self.message = message
        super().__init__(message)
