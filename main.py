from fastapi import FastAPI
from models import Base
from database import engine
from routers import (
    auth,
    user,
    recipe,
    forked_recipe,
    ingredient,
    comment,
    cooking_history,
    wishlist,
    admin,
)

app = FastAPI()

Base.metadata.create_all(bind=engine)

app.include_router(router=auth.router)
app.include_router(router=user.router)
app.include_router(router=recipe.router)
app.include_router(router=forked_recipe.router)
app.include_router(router=ingredient.router)
app.include_router(router=comment.router)
app.include_router(router=cooking_history.router)
app.include_router(router=wishlist.router)
app.include_router(router=admin.router)
