from fastapi import FastAPI
from models import Base
from database import engine
from routers import auth, user

app = FastAPI()

Base.metadata.create_all(bind=engine)

@app.get("/")
def test():
    return {"messsage": "Hello World!"}

app.include_router(router=auth.router) 
app.include_router(router=user.router) 