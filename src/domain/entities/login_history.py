from dataclasses import dataclass
from datetime import datetime
from uuid import UUID


@dataclass
class LoginHistory:
    id: int
    user_id: UUID
    user_agent: str
    login_date: datetime