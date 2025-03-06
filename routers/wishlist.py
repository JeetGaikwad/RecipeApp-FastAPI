from fastapi import APIRouter, Depends, HTTPException
from database import SessionLocal
from typing import Annotated, Optional
from pydantic import BaseModel
from enum import Enum
from sqlalchemy.orm import Session
from .auth import get_current_user
from starlette import status
from models import Wishlists, Recipe

router = APIRouter(prefix="/wishlists", tags=["wishlists"])


class VisibilityEnum(str, Enum):
    public = "public"
    private = "private"


class WishlistRequest(BaseModel):
    recipeId: int
    visibility: VisibilityEnum = VisibilityEnum.private


class WishlistUpdateRequest(BaseModel):
    visibility: VisibilityEnum = VisibilityEnum.private


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


db_dependency = Annotated[Session, Depends(get_db)]
user_dependency = Annotated[dict, Depends(get_current_user)]


@router.get("/public", status_code=status.HTTP_200_OK)
async def get_all_public_wishlist(user: user_dependency, db: db_dependency):
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Unauthorized user."
        )

    wishlist = (
        db.query(Wishlists).filter(Wishlists.visibility == VisibilityEnum.public).all()
    )

    return {"wishlist": wishlist}


@router.get("/", status_code=status.HTTP_200_OK)
async def get_user_wishlist(user: user_dependency, db: db_dependency):
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Unauthorized user."
        )

    wishlist = db.query(Wishlists).filter(Wishlists.userId == user.get("id")).all()

    return {"wishlist": wishlist}


@router.post("/", status_code=status.HTTP_201_CREATED)
async def add_to_wishlist(
    user: user_dependency, db: db_dependency, request: WishlistRequest
):
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Unauthorized user."
        )

    recipe_id = request.recipeId
    visibility = request.visibility

    recipe = db.query(Recipe).filter(Recipe.id == recipe_id).first()
    if not recipe:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Recipe not found."
        )

    existing_wishlist = (
        db.query(Wishlists)
        .filter(Wishlists.userId == user.get("id"), Wishlists.recipeId == recipe_id)
        .first()
    )

    if existing_wishlist:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Recipe is already in the wishlist.",
        )

    new_wishlist = Wishlists(
        userId=user.get("id"), recipeId=recipe_id, visibility=visibility
    )

    db.add(new_wishlist)
    db.commit()


@router.put("/{recipe_id}", status_code=status.HTTP_204_NO_CONTENT)
async def update_wishlist_visibility(
    user: user_dependency,
    db: db_dependency,
    recipe_id: int,
    request: WishlistUpdateRequest,
):
    if not user:
        raise HTTPException(status_code=401, detail="Unauthorized user.")

    wishlist_entry = (
        db.query(Wishlists)
        .filter(Wishlists.userId == user.get("id"), Wishlists.recipeId == recipe_id)
        .first()
    )

    if not wishlist_entry:
        raise HTTPException(status_code=404, detail="Wishlist entry not found.")

    wishlist_entry.visibility = request.visibility
    db.commit()


@router.delete("/{recipe_id}", status_code=status.HTTP_204_NO_CONTENT)
async def remove_from_wishlist(
    user: user_dependency, db: db_dependency, recipe_id: int
):
    if not user:
        raise HTTPException(status_code=401, detail="Unauthorized user.")

    wishlist_entry = (
        db.query(Wishlists)
        .filter(Wishlists.userId == user.get("id"), Wishlists.recipeId == recipe_id)
        .first()
    )

    if not wishlist_entry:
        raise HTTPException(status_code=404, detail="Wishlist entry not found.")

    db.delete(wishlist_entry)
    db.commit()
