"""
Password hashing and verification utilities using Argon2.

Provides secure password hashing with Argon2id algorithm and automatic
hash updates when cost parameters become outdated.
"""
from typing import Any

from argon2.exceptions import InvalidHashError, VerifyMismatchError
from pwdlib import PasswordHash


_pwd = PasswordHash.recommended()


def hash_password(password: str) -> Any:
    """
    Hash a plain text password using Argon2id algorithm.
    
    Generates a secure password hash suitable for database storage.
    The resulting hash includes algorithm identifier, cost parameters,
    salt, and the actual hash value.
    
    Args:
        password: Plain text password to hash.
    
    Returns:
        Hashed password string in format: $argon2id$v=19$m=...,t=...,p=...$...$...
    
    Note:
        Uses recommended defaults from pwdlib (Argon2id with secure parameters).
    """
    return _pwd.hash(password)


async def verify_password(plain: str, hashed: str) -> bool:
    """
    Verify plain text password against stored hash.
    
    Compares the provided password with the stored hash and automatically
    updates the hash in the database if cost parameters are outdated.
    This ensures security stays current without requiring user action.
    
    Args:
        plain: Plain text password provided by user.
        hashed: Stored password hash from database.
    
    Returns:
        True if password matches the hash, False otherwise.
        Also returns False if hash format is invalid or algorithm is unknown.
    
    Note:
        If hash parameters are outdated and verification succeeds, the function
        automatically rehashes the password with current parameters and updates
        the database asynchronously without blocking the response.
    """
    try:
        verified, new_hash = _pwd.verify_and_update(plain, hashed)
    except InvalidHashError:
        return False
    except VerifyMismatchError:
        return False

    if verified and new_hash:
        from src.database import async_session_maker
        from src.auth.models import User
        import sqlalchemy as sa
        import asyncio

        async def _store():
            async with async_session_maker() as ses:
                await ses.execute(
                    sa.update(User)
                      .where(User.hashed_password == hashed)
                      .values(hashed_password=new_hash)
                )
                await ses.commit()

        asyncio.create_task(_store())

    return verified
