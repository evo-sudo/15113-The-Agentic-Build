import os
import hashlib
import getpass
from typing import Dict, Any, Optional

from storage import load_users, save_users


def _hash_password(password: str, salt: bytes) -> str:
    # PBKDF2 with SHA-256
    dk = hashlib.pbkdf2_hmac("sha256", password.encode("utf-8"), salt, 100_000)
    return dk.hex()


def create_account() -> Optional[str]:
    users = load_users()

    while True:
        username = input("Enter a new username: ").strip()
        if not username:
            print("Username cannot be empty.")
            continue
        if username in users:
            # “If a user tries to create an account with a username that already exists,
            # the program prompts them to enter a different username.”
            print("That username already exists. Please choose a different username.")
            continue
        break

    while True:
        password = getpass.getpass("Enter a new password: ")
        if not password:
            print("Password cannot be empty.")
            continue
        confirm = getpass.getpass("Confirm password: ")
        if password != confirm:
            print("Passwords do not match. Try again.")
            continue
        break

    salt = os.urandom(16)
    password_hash = _hash_password(password, salt)

    users[username] = {
        "salt": salt.hex(),
        "password_hash": password_hash,
    }
    save_users(users)
    print(f"Account created successfully. You are now logged in as '{username}'.")
    return username


def login() -> Optional[str]:
    users = load_users()
    if not users:
        print("No users exist yet. Please create an account first.")
        return None

    while True:
        username = input("Enter username: ").strip()
        if username not in users:
            print("Invalid username. Please try again.")
            continue

        user_record: Dict[str, Any] = users[username]
        salt = bytes.fromhex(user_record["salt"])
        stored_hash = user_record["password_hash"]

        password = getpass.getpass("Enter password: ")
        attempt_hash = _hash_password(password, salt)

        if attempt_hash == stored_hash:
            print(f"Login successful. Welcome, {username}!")
            return username
        else:
            # “If a user enters the wrong password, the program allows them to retry login.”
            print("Incorrect password. Please try again.")
            # loop continues