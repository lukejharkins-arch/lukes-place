"""Accounts: PBKDF2 password hashing (stdlib) and opaque session tokens."""
import hashlib
import hmac
import secrets
from datetime import datetime, timedelta, timezone

ITERATIONS = 240_000
SESSION_DAYS = 14


def hash_password(pw: str) -> str:
    if len(pw) < 8:
        raise ValueError("Password must be at least 8 characters")
    salt = secrets.token_hex(16)
    dk = hashlib.pbkdf2_hmac("sha256", pw.encode(), bytes.fromhex(salt), ITERATIONS)
    return f"pbkdf2_sha256${ITERATIONS}${salt}${dk.hex()}"


def verify_password(pw: str, stored: str) -> bool:
    try:
        _, iters, salt, digest = stored.split("$")
    except ValueError:
        return False
    dk = hashlib.pbkdf2_hmac("sha256", pw.encode(), bytes.fromhex(salt), int(iters))
    return hmac.compare_digest(dk.hex(), digest)


def create_session(conn, user_id: int) -> str:
    token = secrets.token_urlsafe(32)
    exp = (datetime.now(timezone.utc) + timedelta(days=SESSION_DAYS)).strftime("%Y-%m-%dT%H:%M:%SZ")
    conn.execute("INSERT INTO sessions(token, user_id, expires_at) VALUES (?,?,?)", (token, user_id, exp))
    conn.commit()
    return token


def user_for_token(conn, token: str):
    if not token:
        return None
    r = conn.execute("""SELECT u.id, u.email, u.display_name, u.role FROM sessions s JOIN users u ON u.id=s.user_id
                        WHERE s.token=? AND s.expires_at > strftime('%Y-%m-%dT%H:%M:%SZ','now')""", (token,)).fetchone()
    return dict(r) if r else None


def destroy_session(conn, token: str):
    conn.execute("DELETE FROM sessions WHERE token=?", (token,))
    conn.commit()
