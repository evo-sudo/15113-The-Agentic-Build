import os
import pickle
from typing import Any, Dict

USERS_FILE = "users.dat"
HISTORY_FILE = "history.dat"


def _load_binary(path: str) -> Dict[str, Any]:
    if not os.path.exists(path):
        return {}
    with open(path, "rb") as f:
        try:
            return pickle.load(f)
        except Exception:
            # If corrupted, reset to empty
            return {}


def _save_binary(path: str, data: Dict[str, Any]) -> None:
    with open(path, "wb") as f:
        pickle.dump(data, f)


def load_users() -> Dict[str, Any]:
    return _load_binary(USERS_FILE)


def save_users(users: Dict[str, Any]) -> None:
    _save_binary(USERS_FILE, users)


def load_history() -> Dict[str, Any]:
    return _load_binary(HISTORY_FILE)


def save_history(history: Dict[str, Any]) -> None:
    _save_binary(HISTORY_FILE, history)