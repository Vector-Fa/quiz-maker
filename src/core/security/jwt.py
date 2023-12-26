from datetime import datetime, timedelta

import jose.exceptions
from jose import jwt

from ..config import settings
from ..excpetions.jwt_exceptions import JwtTokenExpiredException, BadJwtTokenException


class JWTHandler:
    secret_key = settings.SECRET_KEY
    algorithm = settings.ALGORITHM
    access_token_expire = 30
    refresh_token_expire = 24 * 60 * 30

    @staticmethod
    def encode_access_token(payload: dict) -> str:
        expire = datetime.utcnow() + timedelta(minutes=JWTHandler.access_token_expire)
        payload.update({"exp": expire})
        return jwt.encode(
            payload, JWTHandler.secret_key, algorithm=JWTHandler.algorithm
        )

    @staticmethod
    def encode_refresh_token(payload: dict) -> str:
        expire = datetime.utcnow() + timedelta(minutes=JWTHandler.refresh_token_expire)
        payload.update({"exp": expire})
        return jwt.encode(
            payload, JWTHandler.secret_key, algorithm=JWTHandler.algorithm
        )

    @staticmethod
    def decode_access(token: str) -> dict:
        payload = JWTHandler.decode_token(token)
        return payload

    @staticmethod
    def decode_refresh(token: str) -> dict:
        payload = JWTHandler.decode_token(token)
        if payload.get("refresh_user_id") is None:
            raise BadJwtTokenException
        return payload

    @classmethod
    def decode_token(cls, token: str) -> dict:
        try:
            return jwt.decode(
                token, JWTHandler.secret_key, algorithms=[JWTHandler.algorithm]
            )
        except jose.exceptions.ExpiredSignatureError:
            raise JwtTokenExpiredException

        except jose.exceptions.JWTError:
            raise BadJwtTokenException
