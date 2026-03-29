import os
import sys
import hashlib
import msvcrt
from typing import Dict, Any, Optional

from storage import load_users, save_users


# ---------------------------------------------------------
# Windows-compatible password masking with *
# ---------------------------------------------------------
def input_password(prompt="Password: "):
    print(prompt, end="", flush=True)
    password = ""

    while True:
        ch = msvcrt.getwch()

        # Enter key
        if ch == "\r":
            print()
            break

        # Backspace
        if ch == "\b":
            if len(password) > 0:
                password = password[:-1]
                sys.stdout.write("\b \b")
                sys.stdout.flush()
            continue

        # Ignore special keys (arrows, etc.)
        if ch in ("\x00", "\xe0"):
            msvcrt.getwch()  # skip the next character
            continue

        # Normal character
        password += ch
        sys.stdout.write("*")
        sys.stdout.flush()

    return password


# ---------------------------------------------------------
# Password hashing
# ---------------------------------------------------------
def _hash_password(password: str, salt: bytes) -> str:
    dk = hashlib.pbkdf2_hmac("sha256", password.encode("utf-8"), salt, 100_000)
    return dk.hex()


# ---------------------------------------------------------
# Account creation
# ---------------------------------------------------------
def create_account() -> Optional[str]:
    users = load_users()

    while True:
        username = input("Enter a new username: ").strip()
        if not username:
            print("Username cannot be empty.")
            continue
        if username in users:
            print("That username already exists. Please choose a different username.")
            continue
        break

    while True:
        password = input_password("Enter a new password: ")
        if not password:
            print("Password cannot be empty.")
            continue

        confirm = input_password("Confirm password: ")
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


# ---------------------------------------------------------
# Login
# ---------------------------------------------------------
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

        password = input_password("Enter password: ")
        attempt_hash = _hash_password(password, salt)

        if attempt_hash == stored_hash:
            print(f"Login successful. Welcome, {username}!")
            return username
        else:
            print("Incorrect password. Please try again.")