class AppError(Exception):
    status_code = 500

    def __init__(self, message, details=None):
        super().__init__(message)
        self.message = message
        self.details = details

    def to_dto(self):
        body = {"error": self.__class__.__name__, "message": self.message}
        if self.details is not None:
            body["details"] = self.details
        return body


class ValidationError(AppError):
    status_code = 400


class NotFoundError(AppError):
    status_code = 404


class ConflictError(AppError):
    status_code = 409
