"""Shared request schemas for the auth gateway and its clients (e.g. main.py).

Keeping these in one place avoids redefining the same Pydantic models in every
service that talks to the gateway.
"""

from __future__ import annotations

from typing import Optional

from pydantic import BaseModel


class LoginRequest(BaseModel):
    username: str
    password: str


class TokenRequest(BaseModel):
    token: Optional[str] = None


class AuthorizeRequest(BaseModel):
    tool: Optional[str] = None
    resource: Optional[str] = None
    operation: Optional[str] = None


class SessionRequest(BaseModel):
    token: Optional[str] = None


class AgentExecuteRequest(BaseModel):
    session_id: str
    prompt: str
    token: Optional[str] = None


class PromptRollbackRequest(BaseModel):
    version: str
