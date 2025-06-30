class AuthenticationError(Exception):
    pass

class AuthNotProvided(AuthenticationError):
    pass

class TokenExpired(AuthenticationError):
    pass

class AuthorizationError(Exception):
    pass