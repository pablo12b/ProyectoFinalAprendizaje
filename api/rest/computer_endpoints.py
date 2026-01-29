
from typing import Annotated

from aioinject import Inject
from aioinject.ext.fastapi import inject
from fastapi import APIRouter
from pydantic import BaseModel

from business_backend.services.computer_service import ComputerService

router = APIRouter()


class ComputerCreate(BaseModel):
    brand: str
    code: str
    price: float
    description: str | None = None


class ComputerResponse(BaseModel):
    id: str  # Simplify UUID to str for JSON response
    brand: str
    code: str
    price: float
    description: str | None


@router.get("/computers")
@inject
async def get_computers(
    service: Annotated[ComputerService, Inject],
) -> list[ComputerResponse]:
    computers = await service.get_all_computers()
    return [
        ComputerResponse(
            id=str(c.id),
            brand=c.brand,
            code=c.code,
            price=float(c.price),
            description=c.description,
        )
        for c in computers
    ]


@router.post("/computers")
@inject
async def create_computer(
    request: ComputerCreate,
    service: Annotated[ComputerService, Inject],
) -> ComputerResponse:
    computer = await service.create_computer(
        brand=request.brand,
        code=request.code,
        price=request.price,
        description=request.description,
    )
    return ComputerResponse(
        id=str(computer.id),
        brand=computer.brand,
        code=computer.code,
        price=float(computer.price),
        description=computer.description,
    )


@router.get("/computers/{computer_id}")
@inject
async def get_computer_details(
    computer_id: str,
    service: Annotated[ComputerService, Inject],
) -> ComputerResponse:
    from uuid import UUID

    try:
        uuid_obj = UUID(computer_id)
    except ValueError:
        from fastapi import HTTPException
        raise HTTPException(status_code=400, detail="Invalid UUID format")

    computer = await service.get_computer(uuid_obj)
    if not computer:
        from fastapi import HTTPException
        raise HTTPException(status_code=404, detail="Computer not found")

    return ComputerResponse(
        id=str(computer.id),
        brand=computer.brand,
        code=computer.code,
        price=float(computer.price),
        description=computer.description,
    )
