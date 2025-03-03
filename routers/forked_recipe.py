from fastapi import APIRouter, Depends, HTTPException
from database import SessionLocal
from typing import Annotated, Optional
from pydantic import BaseModel
from enum import Enum
from sqlalchemy.orm import Session
from .auth import get_current_user
from starlette import status
from models import ForkedRecipes, Recipe

router = APIRouter(
    prefix="/forked-recipe",
    tags=['forked-recipe']
)


class Tag(str, Enum):
    veg = 'veg'
    nonveg = 'nonveg'


class ForkedRecipeRequest(BaseModel):
    recipeName: Optional[str] = None
    description: Optional[str] = None
    recipeType: Tag
    peopleCount: Optional[str] = None


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


db_dependency = Annotated[Session, Depends(get_db)]
user_dependency = Annotated[dict, Depends(get_current_user)]


@router.get('/', status_code=status.HTTP_200_OK)
async def get_all_forked_recipes(user: user_dependency, db: db_dependency):
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Unauthorize user.")

    recipes = db.query(ForkedRecipes).filter(
        ForkedRecipes.userId == user.get('id')).all()

    return {'forked_recipes': recipes}


@router.get('/{forked_id}', status_code=status.HTTP_200_OK)
async def get_forked_recipe_by_id(user: user_dependency, db: db_dependency, forked_id: int):
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Unauthorize user.")

    recipe = db.query(ForkedRecipes).filter((ForkedRecipes.userId == user.get(
        'id')) & (ForkedRecipes.id == forked_id)).first()

    if not recipe:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Recipe not found")

    return {'forked_recipe': recipe}


@router.post('/fork-recipe/{recipe_id}', status_code=status.HTTP_201_CREATED)
async def add_forked_recipe(user: user_dependency, db: db_dependency, recipe_id: int):
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Unauthorize user.")

    existing_recipe = db.query(Recipe).filter(Recipe.id == recipe_id).first()

    if not existing_recipe:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Recipe not found")

    forked_recipe = ForkedRecipes(
        userId=user.get('id'),
        recipeId=existing_recipe.id,
        recipeName=existing_recipe.recipeName,
        description=existing_recipe.description,
        recipeType=existing_recipe.recipeType,
        peopleCount=existing_recipe.peopleCount
    )

    db.add(forked_recipe)

    existing_recipe.forkedCount = existing_recipe.forkedCount + 1

    db.commit()


@router.put('/{forked_id}', status_code=status.HTTP_204_NO_CONTENT)
async def update_forked_recipe(user: user_dependency, db: db_dependency, forked_id: int, forked_recipe_request: ForkedRecipeRequest):
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Unauthorize user.")

    existing_fork = db.query(ForkedRecipes).filter(
        (ForkedRecipes.id == forked_id) & (ForkedRecipes.userId == user.get('id'))).first()

    if not existing_fork:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Forked Recipe not found")

    if forked_recipe_request.recipeName is not None:
        existing_fork.recipeName = forked_recipe_request.recipeName

    if forked_recipe_request.description is not None:
        existing_fork.description = forked_recipe_request.description

    if forked_recipe_request.recipeType is not None:
        existing_fork.recipeType = forked_recipe_request.recipeType

    if forked_recipe_request.peopleCount is not None:
        existing_fork.peopleCount = forked_recipe_request.peopleCount

    db.add(existing_fork)
    db.commit()


@router.delete('/{forked_id}', status_code=status.HTTP_204_NO_CONTENT)
async def delete_forked_recipe(user: user_dependency, db: db_dependency, forked_id: int):
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Unauthorize user.")

    existing_fork = db.query(ForkedRecipes).filter(
        (ForkedRecipes.id == forked_id) & (ForkedRecipes.userId == user.get('id'))).first()

    if not existing_fork:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Forked Recipe not found")

    db.query(ForkedRecipes).filter(ForkedRecipes.id == forked_id).delete()
    db.commit()
