from fastapi import status, HTTPException

class UserAlreadyExistsException(HTTPException):
    def __init__(self, detail: str = 'User with this email already exists'):
        super().__init__(status_code=status.HTTP_400_BAD_REQUEST, detail=detail)

class InvalidCredentialsException(HTTPException):
    def __init__(self, detail: str = 'Incorrect email or password'):
        super().__init__(status_code=status.HTTP_401_UNAUTHORIZED, detail=detail)

class RefreshTokenInvalidException(HTTPException):
    def __init__(self, detail: str = 'Refresh token is invalid or expired'):
        super().__init__(status_code=status.HTTP_401_UNAUTHORIZED, detail=detail)


class InactiveUserException(HTTPException):
    def __init__(self, detail: str = 'User account is inactive'):
        super().__init__(status_code=status.HTTP_403_FORBIDDEN, detail=detail)

class RefreshTokenInvalidException(HTTPException):
    def __init__(self, detail: str = 'Refresh token is invalid or expired'):
        super().__init__(status_code=status.HTTP_401_UNAUTHORIZED, detail=detail)