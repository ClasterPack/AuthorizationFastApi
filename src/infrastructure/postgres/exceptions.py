from __future__ import annotations

from enum import Enum, auto

from loguru import logger


class ErrorMessages(Enum):
    OBJ_DOES_NOT_EXIST = "%s(%s) does not exist"
    CREATION_FAILED = "Failed to create %s with data: %s"
    DELETION_FAILED = "Failed to delete %s(id=%s)"
    INVALID_INPUT = "Invalid input for %s: %s"
    GENERIC_REPO_ERROR = "Repository error in %s: %s"
    NOT_IMPLEMENTED = "Not implemented method: %s"

    def format(self, *args) -> str:
        return self.value % args


class RepoTypes(Enum):
    USERSQL = auto()


class BaseRepositoryError(Exception):
    def __init__(self, message: str, *, original_exception: Exception | None = None):
        self.message = message
        self.original_exception = original_exception

        logger.error(f"{self.__class__.__name__}: {message}")
        if original_exception:
            logger.exception(original_exception)

        super().__init__(message)


class RecordNotFoundError(BaseRepositoryError):
    def __init__(
        self,
        repository: str,
        identifier: str | int,
        *,
        original_exception: Exception | None = None,
    ):
        message = ErrorMessages.OBJ_DOES_NOT_EXIST.format(repository, identifier)
        super().__init__(message, original_exception=original_exception)


class RecordCreationError(BaseRepositoryError):
    def __init__(
        self,
        obj_type: str,
        data: dict,
        *,
        original_exception: Exception | None = None,
    ):
        message = ErrorMessages.CREATION_FAILED.format(obj_type, data)
        super().__init__(message, original_exception=original_exception)


class RecordDeletionError(BaseRepositoryError):
    def __init__(
        self,
        obj_type: str,
        obj_id: int | str,
        *,
        original_exception: Exception | None = None,
    ):
        message = ErrorMessages.DELETION_FAILED.format(obj_type, obj_id)
        super().__init__(message, original_exception=original_exception)


class InvalidInputError(BaseRepositoryError):
    def __init__(
        self,
        obj_type: str,
        data: dict,
        *,
        original_exception: Exception | None = None,
    ):
        message = ErrorMessages.INVALID_INPUT.format(obj_type, data)
        super().__init__(message, original_exception=original_exception)