from fastapi import APIRouter, Depends, HTTPException
from database import SessionLocal
from typing import Annotated
from sqlalchemy.orm import Session
from pydantic import BaseModel
from .auth import get_current_user
from starlette import status
from models import CookingHistory, Recipe
from datetime import datetime

router = APIRouter(
    prefix="/cooking-history",
    tags=['cooking-history']
)


class CookingHistoryRequest(BaseModel):
    recipe_id: int


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


db_dependency = Annotated[Session, Depends(get_db)]
user_dependency = Annotated[dict, Depends(get_current_user)]


@router.get('/', status_code=status.HTTP_200_OK)
async def get_user_cooking_history(user: user_dependency, db: db_dependency):
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Unauthorize user.")

    history = db.query(CookingHistory).filter(
        CookingHistory.userId == user.get('id')).order_by(CookingHistory.createdAt.desc()).all()

    return {'cooking_history': history}


@router.post('/', status_code=status.HTTP_201_CREATED)
async def add_cooking_history(user: user_dependency, db: db_dependency, request: CookingHistoryRequest):
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Unauthorized user."
        )
    recipe_id = request.recipe_id

    recipe = db.query(Recipe).filter(Recipe.id == recipe_id).first()
    if not recipe:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Recipe not found."
        )

    existing_history = db.query(CookingHistory).filter(
        CookingHistory.userId == user.get("id"), CookingHistory.recipeId == recipe_id).first()

    if existing_history:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                            detail="Cooking history already exists.")

    new_history = CookingHistory(userId=user.get("id"), recipeId=recipe_id)

    db.add(new_history)
    db.commit()


@router.put('/{recipe_id}', status_code=status.HTTP_204_NO_CONTENT)
async def update_cooking_history(user: user_dependency, db: db_dependency, recipe_id: int):
    if not user:
        raise HTTPException(status_code=401, detail="Unauthorized user.")

    history = db.query(CookingHistory).filter(
        CookingHistory.userId == user.get('id'),
        CookingHistory.recipeId == recipe_id
    ).first()

    if not history:
        raise HTTPException(
            status_code=404, detail="Cooking history not found.")

    history.updatedAt = datetime.now()

    db.commit()


@router.delete('/{recipe_id}', status_code=status.HTTP_204_NO_CONTENT)
async def delete_cooking_history(user: user_dependency, db: db_dependency, recipe_id: int):
    if not user:
        raise HTTPException(status_code=401, detail="Unauthorized user.")

    history = db.query(CookingHistory).filter(
        CookingHistory.userId == user.get('id'),
        CookingHistory.recipeId == recipe_id
    ).first()

    if not history:
        raise HTTPException(
            status_code=404, detail="Cooking history not found.")

    db.delete(history)
    db.commit()
