from fastapi import APIRouter, Depends, HTTPException
from database import SessionLocal
from sqlalchemy.orm import Session
from typing import Annotated
from pydantic import BaseModel
from starlette import status
from enum import Enum
from models import RecipeIngredients, Recipe, Ingredients
from .auth import get_current_user
from decimal import Decimal

router = APIRouter(
    prefix='/ingredients',
    tags=['ingredients']
)


class WeightUnit(str, Enum):
    gram = "gram"
    kilogram = "kilogram"
    liter = "liter"
    mililiter = "mililiter"
    teaspoon = "teaspoon"
    tablespoon = "tablespoon"
    cup = "cup"
    piece = "piece"


class IngredientRequest(BaseModel):
    ingredientName: str


class RecipeIngredientRequest(BaseModel):
    quantity: Decimal
    unit: WeightUnit


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


db_dependency = Annotated[Session, Depends(get_db)]
user_dependency = Annotated[dict, Depends(get_current_user)]


@router.get('/{recipe_id}/ingredients', status_code=status.HTTP_200_OK)
async def get_recipe_ingredients(db: db_dependency, recipe_id: int):
    ingredients = db.query(Ingredients.ingredientName, RecipeIngredients.quantity, RecipeIngredients.unit) \
        .join(RecipeIngredients, Ingredients.id == RecipeIngredients.ingredientId) \
        .filter(RecipeIngredients.recipeId == recipe_id).all()

    if not ingredients:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail="No ingredients found for this recipe.")

    return [{'ingredientName': ing.ingredientName, 'quantity': ing.quantity, 'unit': ing.unit.value} for ing in ingredients]


@router.get('/search', status_code=status.HTTP_200_OK)
async def get_ingredient_by_name(user: user_dependency, db: db_dependency, ingredient_name: str):
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Unauthorized User")

    ingredient_search = db.query(Ingredients).filter(
        Ingredients.ingredientName.ilike(f"%{ingredient_name}%")).all()

    return {'ingredients': ingredient_search}


@router.post('/{recipe_id}/ingredients', status_code=status.HTTP_201_CREATED)
async def add_recipe_ingredient(user: user_dependency, db: db_dependency, recipe_id: int,
                                ingredient_request: IngredientRequest, recipe_ing_request: RecipeIngredientRequest):
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Unauthorized User")

    existing_recipe = db.query(Recipe).filter(
        (Recipe.userId == user.get('id')) & (Recipe.id == recipe_id)).first()

    if not existing_recipe:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Recipe not found")

    ingredient = db.query(Ingredients).filter(
        Ingredients.ingredientName == ingredient_request.ingredientName.capitalize()).first()

    if not ingredient:
        ingredient_model = Ingredients(
            ingredientName=ingredient_request.ingredientName.capitalize())
        db.add(ingredient_model)
        db.commit()
        db.refresh(ingredient_model)
        ingredient = ingredient_model

    recipe_ingredient = RecipeIngredients(
        ingredientId=ingredient.id,
        recipeId=existing_recipe.id,
        quantity=recipe_ing_request.quantity,
        unit=recipe_ing_request.unit
    )

    db.add(recipe_ingredient)
    db.commit()


@router.put('/{recipe_id}/ingredients/{ingredient_id}', status_code=status.HTTP_204_NO_CONTENT)
async def update_recipe_ingredient(user: user_dependency, db: db_dependency, recipe_id: int, ingredient_id: int,
                                   recipe_ing_request: RecipeIngredientRequest):
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Unauthorized User")

    existing_recipe = db.query(Recipe).filter(
        (Recipe.userId == user.get('id')) & (Recipe.id == recipe_id)).first()

    if not existing_recipe:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Recipe not found")

    recipe_ingredient = db.query(RecipeIngredients).filter(
        (RecipeIngredients.recipeId == recipe_id) & (RecipeIngredients.ingredientId == ingredient_id)).first()

    if not recipe_ingredient:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail="Ingredient not found in recipe")

    recipe_ingredient.quantity = recipe_ing_request.quantity
    recipe_ingredient.unit = recipe_ing_request.unit

    db.commit()


@router.delete("/{recipe_id}/ingredients/{ingredient_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_recipe_ingredient(user: user_dependency, db: db_dependency, recipe_id: int, ingredient_id: int):
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Unauthorized User")

    existing_recipe = db.query(Recipe).filter(
        (Recipe.userId == user.get('id')) & (Recipe.id == recipe_id)).first()

    if not existing_recipe:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Recipe not found")

    ingredient = db.query(RecipeIngredients).filter_by(
        recipeId=recipe_id, ingredientId=ingredient_id).first()

    if not ingredient:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Ingredient not found")

    db.delete(ingredient)
    db.commit()
