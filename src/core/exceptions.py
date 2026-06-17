class AppError(Exception):
    status_code: int = 500
    detail: str = "Internal server error"

    def __init__(self, detail: str | None = None) -> None:
        self.detail = detail or self.detail


class NotFoundError(AppError):
    status_code = 404
    detail = "Resource not found"


class ConflictError(AppError):
    status_code = 409
    detail = "Resource already exists"


class UnauthorizedError(AppError):
    status_code = 401
    detail = "Authentication required"


class ForbiddenError(AppError):
    status_code = 403
    detail = "Access denied"


class BadRequestError(AppError):
    status_code = 400
    detail = "Bad request"
