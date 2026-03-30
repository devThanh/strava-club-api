from fastapi import HTTPException, status


class ResponseError:
    @staticmethod
    def unauthorized(message: str = "Unauthorized"):
        return HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail={
                "status": status.HTTP_401_UNAUTHORIZED,
                "message": message,
            },
        )

    @staticmethod
    def bad_request(message: str = "Bad request"):
        return HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={
                "status": status.HTTP_400_BAD_REQUEST,
                "message": message,
            },
        )