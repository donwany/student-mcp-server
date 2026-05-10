import os
from pathlib import Path

import httpx
from dotenv import load_dotenv, set_key
from fastmcp import FastMCP

BASE_URL = "https://student-auth-api-u5jz.onrender.com"
ENV_FILE = Path(__file__).parent / ".env"

# Load .env on startup so a previously saved token is available immediately
load_dotenv(ENV_FILE)

mcp = FastMCP("students-mcp")

# Seed in-memory token from .env (empty string → None)
_token: str | None = os.getenv("API_TOKEN") or None


# ── helpers ───────────────────────────────────────────────────────────────────

def _auth_headers() -> dict:
    if not _token:
        raise RuntimeError("Not authenticated. Call login(username, password) first.")
    return {"Authorization": f"Bearer {_token}"}


def _request(method: str, path: str, **kwargs) -> dict:
    kwargs.setdefault("headers", {}).update(_auth_headers())
    with httpx.Client() as client:
        response = client.request(method, f"{BASE_URL}{path}", **kwargs)
        response.raise_for_status()
        return response.json()


# ── tools ─────────────────────────────────────────────────────────────────────

@mcp.tool()
def login(username: str, password: str) -> dict:
    """Authenticate with the API. The bearer token is saved to .env and reused
    automatically on the next server start — no need to log in again unless the
    token expires.

    Args:
        username: Account username.
        password: Account password.
    """
    global _token
    with httpx.Client() as client:
        response = client.post(
            f"{BASE_URL}/login",
            json={"username": username, "password": password},
        )
        response.raise_for_status()
        data = response.json()

    token = (
        data.get("access_token")
        or data.get("token")
        or data.get("bearer_token")
    )
    if not token:
        raise ValueError(f"Could not find token in login response: {data}")

    # Persist to .env so the server can reuse it across restarts
    ENV_FILE.touch(exist_ok=True)
    set_key(str(ENV_FILE), "API_TOKEN", token)

    _token = token
    return {"message": "Login successful. Token saved to .env."}


@mcp.tool()
def get_all_students() -> dict:
    """Get a list of all students."""
    return _request("GET", "/v1/students")


@mcp.tool()
def get_student(id: str) -> dict:
    """Get a single student by their ID.

    Args:
        id: The unique identifier of the student.
    """
    return _request("GET", f"/v1/students/{id}")


@mcp.tool()
def create_student(
    name: str,
    email: str,
    age: int | None = None,
    grade: str | None = None,
) -> dict:
    """Create a new student record.

    Args:
        name:  Full name of the student.
        email: Email address of the student.
        age:   Age of the student (optional).
        grade: Grade or class of the student (optional).
    """
    body = {"name": name, "email": email}
    if age is not None:
        body["age"] = age
    if grade is not None:
        body["grade"] = grade
    return _request("POST", "/v1/students", json=body)


@mcp.tool()
def update_student(
    id: str,
    name: str | None = None,
    email: str | None = None,
    age: int | None = None,
    grade: str | None = None,
) -> dict:
    """Update an existing student record.

    Args:
        id:    The unique identifier of the student to update.
        name:  New full name (optional).
        email: New email address (optional).
        age:   New age (optional).
        grade: New grade or class (optional).
    """
    body = {k: v for k, v in {"name": name, "email": email, "age": age, "grade": grade}.items() if v is not None}
    return _request("PUT", f"/v1/students/{id}", json=body)


@mcp.tool()
def delete_student(id: str) -> dict:
    """Delete a student record by their ID.

    Args:
        id: The unique identifier of the student to delete.
    """
    return _request("DELETE", f"/v1/students/{id}")



# ── entry point ───────────────────────────────────────────────────────────────
if __name__ == '__main__':
    mcp.run(transport="http", host="127.0.0.1", port=8000)
    # mcp.run(transport='streamable-http')