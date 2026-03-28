from typing import List

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from starlette import status
from starlette.exceptions import HTTPException

from database_config import get_db
from resp_models import UserCreate, UserResponse
from user_repository import UserRepository

router = APIRouter(prefix="/users", tags=["Users"])



@router.post("/", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def create_user(user_data: UserCreate, db: AsyncSession = Depends(get_db)): #dependency injection

    repo = UserRepository(db)

    existing_user = repo.get_user_by_email(user_data.email)

    if existing_user:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="User Already exists with this email")

    user = await repo.create(user_data)
    return user
@router.get("/", response_model=List[UserResponse])
async def get_users(skip: int = 0, limit: int = 10, db: AsyncSession = Depends(get_db)):
    repo = UserRepository(db)
    users = await repo.get_all_users(skip=skip, limit=limit)
    return users

@router.get("/{user_id}")
async def get_user(user_id: int, db: AsyncSession = Depends(get_db)):
    repo = UserRepository(db)
    user = await repo.get_user_by_id(user_id=user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )

    return user