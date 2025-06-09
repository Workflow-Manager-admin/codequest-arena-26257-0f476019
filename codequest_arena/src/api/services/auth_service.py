"""
Service logic for authentication:
- Basic in-memory user store (thread-safe)
- Password hashing (SHA256+salt, demo only!)
- JWT encode/decode utils
"""

from typing import Dict, Optional
from threading import Lock
import hashlib
import hmac
import os
import jwt
from datetime import datetime, timedelta

# Demo secret - in production load from env/config!
SECRET_KEY = os.environ.get("CODEQUEST_AUTH_SECRET", "demo-very-insecure-key-demo")
JWT_ALGORITHM = "HS256"
JWT_EXPIRES_MIN = 60 * 24 * 14  # 14 days for convenience


def hash_password(password: str, salt: Optional[str] = None) -> str:
    """Hash a password for the demo store."""
    if not salt:
        salt = os.urandom(8).hex()
    pw_bytes = password.encode("utf-8")
    salt_bytes = salt.encode("utf-8")
    # Combine and hash
    pw_hash = hashlib.pbkdf2_hmac("sha256", pw_bytes, salt_bytes, 100_000)
    return f"{salt}${pw_hash.hex()}"


def verify_password(password: str, stored_hash: str) -> bool:
    """Verify a password against stored hash."""
    try:
        salt, hash_hex = stored_hash.split("$", 1)
    except Exception:
        return False
    test_hash = hash_password(password, salt)
    return hmac.compare_digest(stored_hash, test_hash)


def create_jwt_token(username: str) -> str:
    """Create JWT token for user."""
    now = datetime.utcnow()
    payload = {
        "sub": username,
        "exp": now + timedelta(minutes=JWT_EXPIRES_MIN),
        "iat": now,
    }
    token = jwt.encode(payload, SECRET_KEY, algorithm=JWT_ALGORITHM)
    if isinstance(token, bytes):
        token = token.decode("utf-8")
    return token


def decode_jwt_token(token: str) -> Optional[Dict]:
    """Decode JWT token, return payload, or None."""
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[JWT_ALGORITHM])
        return payload
    except Exception:
        return None


class DemoUserStore:
    """
    Thread-safe demo user store for auth, not persistent!
    """

    def __init__(self):
        self._lock = Lock()
        self._users: Dict[str, Dict] = {}
        # Seed with a demo user for convenience
        self.create_user("demo", "demo123")

    def user_exists(self, username: str) -> bool:
        return username in self._users

    def create_user(self, username: str, password: str) -> None:
        with self._lock:
            if username in self._users:
                raise ValueError("User already exists")
            pw_hash = hash_password(password)
            self._users[username] = {"username": username, "password_hash": pw_hash}

    def get_user(self, username: str) -> Optional[Dict]:
        return self._users.get(username)
