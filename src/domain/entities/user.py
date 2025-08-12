import uuid
from dataclasses import dataclass, field
from datetime import UTC, datetime
from typing import List, Optional

from src.services.jwt_utils import hash_pwd


@dataclass(slots=True)
class User:
    id: uuid.UUID
    username: str
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    password: str = ""
    email: str = ""
    created_at: Optional[datetime] = None
    login_history: Optional[List] = field(default_factory=list)
    token_version: int =0

    @classmethod
    def create(
            cls,
            username: str,
            email: str,
            password: str,
            first_name: Optional[str] = None,
            last_name: Optional[str] = None,
    ) -> "User":
        hashed = hash_pwd(password)
        return cls(
            id=uuid.uuid4(),
            username=username,
            first_name=first_name,
            last_name=last_name,
            password=hashed,
            email=email,
            created_at=datetime.now(UTC),
            login_history= [],
        )