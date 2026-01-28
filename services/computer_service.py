
from typing import Sequence
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from business_backend.database.models.computer import Computer


class ComputerService:
    def __init__(self, session_factory: async_sessionmaker[AsyncSession]) -> None:
        self._session_factory = session_factory

    async def get_all_computers(self) -> Sequence[Computer]:
        async with self._session_factory() as session:
            stmt = select(Computer)
            result = await session.execute(stmt)
            return result.scalars().all()

    async def get_computer(self, computer_id: UUID) -> Computer | None:
        async with self._session_factory() as session:
            stmt = select(Computer).where(Computer.id == computer_id)
            result = await session.execute(stmt)
            return result.scalar_one_or_none()

    async def create_computer(
        self,
        brand: str,
        price: float,
        description: str | None = None,
    ) -> Computer:
        async with self._session_factory() as session:
            computer = Computer(
                brand=brand,
                price=price,
                description=description,
            )
            session.add(computer)
            await session.commit()
            await session.refresh(computer)
            return computer
