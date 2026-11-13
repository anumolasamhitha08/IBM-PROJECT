"""
auth.py – Admin authentication for the monitoring dashboard.
Uses bcrypt for password hashing. Credentials stored in .env.
"""
from __future__ import annotations

import hashlib
import hmac
import logging
import os
import time
from typing import Optional

import bcrypt
import streamlit as st

import config

logger = logging.getLogger("finsaakhi.auth")

_RATE_LIMIT: dict = {}   # ip → (attempt_count, first_attempt_time)
MAX_ATTEMPTS = 5
LOCKOUT_SECONDS = 300


def hash_password(password: str) -> str:
    """Generate a bcrypt hash for a plaintext password."""
    return bcrypt.hashpw(password.encode(), bcrypt.gensalt(rounds=12)).decode()


def verify_password(password: str, hashed: str) -> bool:
    """Verify a plaintext password against stored bcrypt hash."""
    try:
        return bcrypt.checkpw(password.encode(), hashed.encode())
    except Exception:
        return False


def _check_rate_limit(username: str) -> bool:
    """Return False if user is locked out."""
    now = time.time()
    key = username.lower()
    if key in _RATE_LIMIT:
        count, first_time = _RATE_LIMIT[key]
        if now - first_time > LOCKOUT_SECONDS:
            del _RATE_LIMIT[key]
            return True
        if count >= MAX_ATTEMPTS:
            return False
    return True


def _record_attempt(username: str):
    now = time.time()
    key = username.lower()
    if key in _RATE_LIMIT:
        count, first_time = _RATE_LIMIT[key]
        _RATE_LIMIT[key] = (count + 1, first_time)
    else:
        _RATE_LIMIT[key] = (1, now)


def authenticate(username: str, password: str) -> bool:
    """Authenticate admin user. Returns True on success."""
    if not _check_rate_limit(username):
        logger.warning("Rate limit exceeded for: %s", username)
        return False

    expected_user = config.ADMIN_USERNAME
    stored_hash = config.ADMIN_PASSWORD_HASH

    # Constant-time username comparison
    user_match = hmac.compare_digest(username.strip(), expected_user)

    if not user_match:
        _record_attempt(username)
        return False

    # If no hash configured, fall back to env default for dev
    if not stored_hash or stored_hash == "generate_with_python_bcrypt":
        # Dev mode: accept "admin123" as default
        pw_match = hmac.compare_digest(password, "admin123")
    else:
        pw_match = verify_password(password, stored_hash)

    if not pw_match:
        _record_attempt(username)
        return False

    return True


def is_authenticated() -> bool:
    return st.session_state.get("admin_authenticated", False)


def login_page():
    """Render the login page and handle authentication."""
    st.markdown("""
    <style>
    .login-container { max-width: 400px; margin: 60px auto; padding: 2rem;
        background: #f7f8fa; border-radius: 12px; border: 1px solid #e5e7eb; }
    </style>
    """, unsafe_allow_html=True)

    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.markdown("## 🔐 FinSakhi Admin")
        st.markdown("**Monitoring Dashboard**")
        st.divider()

        with st.form("login_form"):
            username = st.text_input("Username", placeholder="admin")
            password = st.text_input("Password", type="password", placeholder="••••••••")
            submitted = st.form_submit_button("Sign In", use_container_width=True)

        if submitted:
            if authenticate(username, password):
                st.session_state["admin_authenticated"] = True
                st.session_state["admin_user"] = username
                st.rerun()
            else:
                remaining_attempts = MAX_ATTEMPTS - _RATE_LIMIT.get(username.lower(), (0, 0))[0]
                if remaining_attempts <= 0:
                    st.error(f"Account temporarily locked. Try again in {LOCKOUT_SECONDS // 60} minutes.")
                else:
                    st.error("Invalid credentials.")

        st.caption("Default dev credentials: admin / admin123")
        st.caption("Set ADMIN_PASSWORD_HASH in .env for production.")


def logout():
    st.session_state["admin_authenticated"] = False
    st.session_state.pop("admin_user", None)
    st.rerun()
