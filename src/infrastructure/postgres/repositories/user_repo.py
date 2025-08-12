from dataclasses import asdict
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload

from src.domain.entities.login_history import LoginHistory
from src.domain.entities.user import User
from src.infrastructure.postgres.exceptions import (RecordNotFoundError,
                                                    RepoTypes)
from src.infrastructure.postgres.repositories.base import BaseRepositoryABC
from src.infrastructure.postgres.tables import LoginHistorySQL, UserSQL


class BaseUserRepository(BaseRepositoryABC):
    def __init__(self, session: AsyncSession):
        self.session = session

    async def create(self, entity: User) -> User:
        data = asdict(entity)
        data.pop("login_history", None)
        user = UserSQL(**data)
        self.session.add(user)
        await self.session.flush()
        await self.session.refresh(user)
        return self._to_entity(user)

    async def get(self, **filters) -> User:
        users = await self.filter(**filters)
        if not users:
            raise RecordNotFoundError(RepoTypes.USERSQL.name, filters)
        return users[0]

    async def filter(self, **filters) -> list[User]:
        stmt = select(UserSQL)
        for field, value in filters.items():
            if hasattr(UserSQL, field):
                stmt = stmt.where(getattr(UserSQL, field) == value)
        result = await self.session.scalars(stmt)
        return [self._to_entity(u) for u in result.all()]

    async def update(self, user_entity: User) -> User:
        new_data = asdict(user_entity)
        user_id = new_data.pop("id")
        if isinstance(user_id, str):
            user_id = UUID(user_id)
        new_data.pop("login_history", None)
        stmt = select(UserSQL).where(UserSQL.id == user_id)
        user = (await self.session.scalars(stmt)).one_or_none()
        if user is None:
            raise RecordNotFoundError(RepoTypes.USERSQL.name, str(user_id))
        for key, value in new_data.items():
            if hasattr(user, key):
                setattr(user, key, value)
        await self.session.flush()
        await self.session.refresh(user)
        return self._to_entity(user)

    async def drop(self, user_id: UUID | str) -> None:
        if isinstance(user_id, str):
            user_id = UUID(user_id)
        stmt = select(UserSQL).where(UserSQL.id == user_id)
        user = (await self.session.scalars(stmt)).one_or_none()
        if user is None:
            raise RecordNotFoundError(RepoTypes.USERSQL.name, str(user_id))
        await self.session.delete(user)

    async def get_with_login_history(
        self,
        user_id: UUID | str,
        limit: int = 10,
        offset: int = 0,
    ) -> tuple[User, int]:
        """
        Возвращает пользователя с историей логинов (пагинация).
        Возвращает (User, total_count).
        """
        if isinstance(user_id, str):
            user_id = UUID(user_id)

        # Получаем пользователя + количество логов
        total_stmt = (
            select(LoginHistorySQL)
            .where(LoginHistorySQL.user_id == user_id)
        )
        total_count = len((await self.session.scalars(total_stmt)).all())

        stmt = (
            select(UserSQL)
            .where(UserSQL.id == user_id)
            .options(joinedload(UserSQL.login_history))
        )
        orm_user = (await self.session.scalars(stmt)).unique().one_or_none()
        if orm_user is None:
            raise RecordNotFoundError(RepoTypes.USERSQL.name, str(user_id))

        # Пагинируем login_history вручную (SQLAlchemy relationship подгрузил всё)
        paginated_history = orm_user.login_history[offset: offset + limit]

        user_entity = self._to_entity(orm_user, paginated_history)
        return user_entity, total_count

    def _to_entity(self, orm_user: UserSQL, login_history=None) -> User:
        return User(
            id=orm_user.id,
            username=orm_user.username,
            first_name=orm_user.first_name,
            last_name=orm_user.last_name,
            password=orm_user.password,
            email=orm_user.email,
            created_at=orm_user.created_at,
            login_history=[
                LoginHistory(
                    id=lh.id,
                    user_id=lh.user_id,
                    user_agent=lh.user_agent,
                    login_date=lh.login_date
                )
                for lh in (login_history if login_history is not None else [])
            ]
        )


class UserRepository(BaseUserRepository):
    async def get_by_id(self, *, user_id: UUID | str) -> User:
        if isinstance(user_id, str):
            user_id = UUID(user_id)
        return await self.get(id=user_id)
