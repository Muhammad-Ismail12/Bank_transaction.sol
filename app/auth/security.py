from datetime import datetime, timedelta, timezone
from typing import Optional

from jose import JWTError, jwt
from passlib.context import CryptContext

from ..core.config import settings


pwd_context = CryptContext(schemes=["pbkdf2_sha256"], deprecated="auto")


def hash_password(plain_password: str) -> str:
	return pwd_context.hash(plain_password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
	return pwd_context.verify(plain_password, hashed_password)


def create_access_token(subject: str, expires_delta: Optional[timedelta] = None) -> str:
	if expires_delta is None:
		expires_delta = timedelta(minutes=settings.access_token_expire_minutes)
	expire = datetime.now(tz=timezone.utc) + expires_delta
	to_encode = {"sub": subject, "exp": expire}
	encoded_jwt = jwt.encode(to_encode, settings.secret_key, algorithm="HS256")
	return encoded_jwt


def decode_access_token(token: str) -> Optional[str]:
	try:
		payload = jwt.decode(token, settings.secret_key, algorithms=["HS256"])
		return payload.get("sub")
	except JWTError:
		return None
