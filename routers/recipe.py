from fastapi import APIRouter, Depends, HTTPException
from database import SessionLocal
from sqlalchemy.orm import Session
from typing import Annotated, Optional
from pydantic import BaseModel
from starlette import status
from enum import Enum
from models import Recipe
from .auth import get_current_user

router = APIRouter(
    prefix='/recipes',
    tags=['recipes']
)


class Tag(str, Enum):
    veg = 'veg'
    nonveg = 'nonveg'


class RecipeRequest(BaseModel):
    recipeName: str
    description: str
    recipeType: Tag
    peopleCount: int


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


db_dependency = Annotated[Session, Depends(get_db)]
user_dependency = Annotated[dict, Depends(get_current_user)]


@router.get('/', status_code=status.HTTP_200_OK)
async def get_all_recipes(db: db_dependency):
    return db.query(Recipe).all()


@router.get('/{recipe_id}', status_code=status.HTTP_200_OK)
async def get_recipe_by_id(db: db_dependency, recipe_id: int):

    recipes = db.query(Recipe).filter(Recipe.userId == recipe_id).all()

    return {'recipes': recipes}


@router.get('/by-user-id', status_code=status.HTTP_200_OK)
async def get_recipe_by_user_id(db: db_dependency, user: user_dependency):
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Unauthorize User")

    recipes = db.query(Recipe).filter(Recipe.userId == user.get('id')).all()

    return {'recipes': recipes}


@router.get('/by-type/{recipetype}', status_code=status.HTTP_200_OK)
async def get_recipe_by_type(db: db_dependency, recipetype: Tag, user: user_dependency):
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Unauthorize User")

    recipes = db.query(Recipe).filter(Recipe.recipeType == recipetype).all()

    return {'recipes': recipes}


@router.get('/by-people-count/{people_count}', status_code=status.HTTP_200_OK)
async def get_recipe_by_people_count(db: db_dependency, people_count: int, user: user_dependency):
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Unauthorize User")

    recipes = db.query(Recipe).filter(Recipe.peopleCount == people_count).all()

    return {'recipes': recipes}


@router.get('/search/', status_code=status.HTTP_200_OK)
async def search_recipes(db: db_dependency, query: str):
    recipes = db.query(Recipe).filter((Recipe.recipeName.like(f'%{query}%')) | (
        Recipe.description.like(f'%{query}%'))).all()

    return {'recipes': recipes}


@router.post('/recipe/', status_code=status.HTTP_201_CREATED)
async def create_recipe(db: db_dependency, user: user_dependency, create_recipe: RecipeRequest):
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Unauthorize User")

    recipe_model = Recipe(
        userId=user.get('id'),
        recipeName=create_recipe.recipeName,
        description=create_recipe.description,
        recipeType=create_recipe.recipeType,
        peopleCount=create_recipe.peopleCount
    )

    db.add(recipe_model)
    db.commit()


@router.put('/{recipe_id}', status_code=status.HTTP_204_NO_CONTENT)
async def update_recipe(db: db_dependency, user: user_dependency, update_recipe: RecipeRequest, recipe_id: int):
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Unauthorize User")

    recipe_model = db.query(Recipe).filter(
        (Recipe.userId == user.get('id')) & (Recipe.id == recipe_id)).first()

    if recipe_model is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Recipe not found")

    recipe_model.recipeName = update_recipe.recipeName
    recipe_model.description = update_recipe.description
    recipe_model.recipeType = Tag(update_recipe.recipeType)
    recipe_model.peopleCount = update_recipe.peopleCount

    db.add(recipe_model)
    db.commit()


@router.delete('/{recipe_id}', status_code=status.HTTP_204_NO_CONTENT)
async def delete_recipe(db: db_dependency, user: user_dependency, recipe_id: int):
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Unauthorize User")

    recipe_model = db.query(Recipe).filter(
        (Recipe.userId == user.get('id')) & (Recipe.id == recipe_id)).first()

    if recipe_model is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Recipe not found")

    db.query(Recipe).filter(Recipe.id == recipe_id).delete()
    db.commit()
