from fastapi import APIRouter, Depends, HTTPException
from database import SessionLocal
from .auth import get_current_user
from typing import Annotated
from sqlalchemy.orm import Session
from starlette import status
from passlib.context import CryptContext
from models import Users, Recipe, RecipeComments
from enum import Enum

router = APIRouter(prefix="/admin", tags=["admin"])


class Role(str, Enum):
    admin = "admin"
    user = "user"


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


db_dependency = Annotated[Session, Depends(get_db)]
user_dependency = Annotated[dict, Depends(get_current_user)]
bcrypt_context = CryptContext(schemes="bcrypt", deprecated="auto")


# Recipe management
@router.get("/recipes", status_code=status.HTTP_200_OK)
async def get_all_recipes(db: db_dependency, user: user_dependency):
    if user is None or user.get("role") != Role.admin:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Unauthorized User"
        )

    recipes = db.query(Recipe).all()

    return {"recipes": recipes}


@router.put("/recipes/{recipe_id}/hide", status_code=status.HTTP_204_NO_CONTENT)
async def hide_recipe(db: db_dependency, user: user_dependency, recipe_id: int):
    if user is None or user.get("role") != Role.admin:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Unauthorized User"
        )

    recipe = db.query(Recipe).filter(Recipe.id == recipe_id).first()

    if not recipe:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Recipe not found"
        )

    recipe.isHide = True
    db.commit()


@router.put("/recipes/{recipe_id}/show", status_code=status.HTTP_204_NO_CONTENT)
async def show_recipe(db: db_dependency, user: user_dependency, recipe_id: int):
    if user is None or user.get("role") != Role.admin:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Unauthorized User"
        )

    recipe = db.query(Recipe).filter(Recipe.id == recipe_id).first()

    if not recipe:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Recipe not found"
        )

    recipe.isHide = False
    db.commit()


@router.delete("/recipes/{recipe_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_recipe(db: db_dependency, user: user_dependency, recipe_id: int):
    if user is None or user.get("role") != Role.admin:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Unauthorized User"
        )

    recipe = db.query(Recipe).filter(Recipe.id == recipe_id).first()

    if not recipe:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Recipe not found"
        )

    recipe.isDeleted = True
    db.commit()


# Users management
@router.get("/users", status_code=status.HTTP_200_OK)
async def get_all_users(db: db_dependency, user: user_dependency):
    if user is None or user.get("role") != Role.admin:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Unauthorized User"
        )

    users = db.query(Users).all()

    return {"users": users}


@router.put("/users/{user_id}/block", status_code=status.HTTP_204_NO_CONTENT)
async def block_users(db: db_dependency, user: user_dependency, user_id: int):
    if user is None or user.get("role") != Role.admin:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Unauthorized User"
        )

    existing_user = db.query(Users).filter(Users.id == user_id).first()

    if not existing_user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="User not found"
        )

    existing_user.isBlocked = True
    db.commit()


@router.put("/users/{user_id}/unblock", status_code=status.HTTP_204_NO_CONTENT)
async def unblock_users(db: db_dependency, user: user_dependency, user_id: int):
    if user is None or user.get("role") != Role.admin:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Unauthorized User"
        )

    existing_user = db.query(Users).filter(Users.id == user_id).first()

    if not existing_user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="User not found"
        )

    existing_user.isBlocked = False
    db.commit()


@router.delete("/users/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_users(db: db_dependency, user: user_dependency, user_id: int):
    if user is None or user.get("role") != Role.admin:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Unauthorized User"
        )

    existing_user = db.query(Users).filter(Users.id == user_id).first()

    if not existing_user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="User not found"
        )

    db.delete(existing_user)
    db.commit()


# Comment Deletion
@router.delete("/comments/{comment_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_comments(db: db_dependency, user: user_dependency, comment_id: int):
    if user is None or user.get("role") != Role.admin:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Unauthorized User"
        )

    comment = db.query(RecipeComments).filter(RecipeComments.id == comment_id).first()

    if not comment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Comment not found"
        )

    db.delete(comment)
    db.commit()
