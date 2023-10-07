from rest_framework_simplejwt.authentication import JWTAuthentication
from asgiref.sync import sync_to_async

@sync_to_async
def _get_user(token: str):
    jwt = JWTAuthentication()
    return jwt.get_user(jwt.get_validated_token(token))

class TokenAuthMiddleware:
    def __init__(self, app) -> None:
        self.app = app

    async def __call__(self, scope, receive, send):
        # Look up user from query string (you should also do things like
        # checking if it is a valid user ID, or if scope["user"] is already
        # populated).
        from urllib.parse import parse_qs
        token = parse_qs(str(scope["query_string"], 'UTF-8')).get('token', [None])[0]
        if token:
            user = await _get_user(token)
            if user:
                scope['user'] = user
                return await self.app(scope, receive, send)