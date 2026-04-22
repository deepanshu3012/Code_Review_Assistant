"""
Sample code files used to demo the Code Review NLP Assistant.
These range from poor quality to good quality Python code.
"""

# ── Sample 1: Poor quality code ───────────────────────────────────────────
POOR_CODE = '''\
import os
import sys

x = 10
y = 20
z = 30

def f(a,b,c):
    result = 0
    for i in range(0,1000):
        if a > 10:
            if b > 20:
                if c > 30:
                    result = a*b*c+x+y+z
                    if result > 9999:
                        result = 9999
    return result

def g(lst):
    try:
        for item in lst:
            if item > 0:
                print(item * 2 + 100)
    except:
        pass

class D:
    def __init__(self,n,v):
        self.n = n
        self.v = v

    def upd(self,new_v):
        self.v = new_v
        return self.v
'''

# ── Sample 2: Medium quality code ────────────────────────────────────────
MEDIUM_CODE = '''\
import requests

BASE_URL = "https://api.example.com"

def get_user(user_id):
    # Fetch user from API
    response = requests.get(f"{BASE_URL}/users/{user_id}")
    if response.status_code == 200:
        return response.json()
    return None

def create_user(name, email, age):
    data = {
        "name": name,
        "email": email,
        "age": age
    }
    response = requests.post(f"{BASE_URL}/users", json=data)
    if response.status_code == 201:
        return response.json()["id"]
    else:
        print(f"Error creating user: {response.status_code}")
        return None

def update_user(user_id, **kwargs):
    response = requests.put(f"{BASE_URL}/users/{user_id}", json=kwargs)
    return response.status_code == 200

def delete_user(user_id):
    response = requests.delete(f"{BASE_URL}/users/{user_id}")
    return response.status_code == 204
'''

# ── Sample 3: Good quality code ───────────────────────────────────────────
GOOD_CODE = '''\
"""
User authentication module for the application.

Provides secure password hashing, token generation,
and session validation utilities.
"""

import hashlib
import secrets
from typing import Optional


MAX_TOKEN_LENGTH: int = 64
HASH_ITERATIONS: int = 100_000


def hash_password(password: str, salt: Optional[str] = None) -> tuple[str, str]:
    """
    Hash a plaintext password using PBKDF2-HMAC-SHA256.

    Parameters
    ----------
    password : str
        The plaintext password to hash.
    salt : str, optional
        A hex salt string. Generated fresh if not provided.

    Returns
    -------
    tuple[str, str]
        A (hashed_password, salt) pair, both as hex strings.
    """
    if salt is None:
        salt = secrets.token_hex(16)
    hashed = hashlib.pbkdf2_hmac(
        "sha256",
        password.encode("utf-8"),
        salt.encode("utf-8"),
        HASH_ITERATIONS,
    )
    return hashed.hex(), salt


def generate_session_token(length: int = MAX_TOKEN_LENGTH) -> str:
    """Generate a cryptographically secure session token."""
    return secrets.token_urlsafe(length)


def validate_password_strength(password: str) -> tuple[bool, list[str]]:
    """
    Check whether a password meets the security policy.

    Returns a (is_valid, list_of_failures) tuple.
    """
    failures: list[str] = []
    if len(password) < 8:
        failures.append("Password must be at least 8 characters")
    if not any(c.isupper() for c in password):
        failures.append("Must contain at least one uppercase letter")
    if not any(c.isdigit() for c in password):
        failures.append("Must contain at least one digit")
    if not any(c in "!@#$%^&*()" for c in password):
        failures.append("Must contain at least one special character")
    return len(failures) == 0, failures
'''

SAMPLES = {
    "Poor quality (grade F/D)":  POOR_CODE,
    "Medium quality (grade C)":  MEDIUM_CODE,
    "Good quality (grade A)":    GOOD_CODE,
}