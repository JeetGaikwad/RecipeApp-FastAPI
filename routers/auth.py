from fastapi import APIRouter, Depends, HTTPException
from database import SessionLocal
from sqlalchemy.orm import Session
from typing import Annotated, Optional
from passlib.context import CryptContext
from models import Users
from pydantic import BaseModel
from fastapi.security import OAuth2PasswordRequestForm, OAuth2PasswordBearer
from enum import Enum
from starlette import status
from jose import jwt, JWTError
from datetime import timedelta, datetime, timezone, date
import os
from dotenv import load_dotenv

load_dotenv()

router = APIRouter(prefix="/auth", tags=["auth"])

SECRET_KEY = os.getenv("SECRET_KEY")
ALGORITHM = os.getenv("ALGORITHM")

bcrypt_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth_bearer = OAuth2PasswordBearer(tokenUrl="auth/token")


class Token(BaseModel):
    access_token: str
    token_type: str


class AddUserRole(str, Enum):
    admin = "admin"
    user = "user"


class CreateUserRequest(BaseModel):
    email: str
    username: str
    first_name: str
    last_name: str
    password: str
    bio: str
    profilePhoto: Optional[str] = None
    dateOfBirth: date
    phoneNumber: str
    role: AddUserRole


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


db_dependency = Annotated[Session, Depends(get_db)]


def authenticate_user(username: str, password: str, db):
    user = db.query(Users).filter(Users.username == username).first()

    if not user:
        return False

    if not bcrypt_context.verify(password, user.password):
        return False

    if user.isBlocked:
        return False

    return user


def create_access_token(
    username: str, user_id: int, role: AddUserRole, expires_delta: timedelta
):
    encode = {"sub": username, "id": user_id, "role": role.value}
    expires = datetime.now(timezone.utc) + expires_delta
    encode.update({"exp": expires})
    return jwt.encode(encode, SECRET_KEY, ALGORITHM)


async def get_current_user(token: Annotated[str, Depends(oauth_bearer)]):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        user_id: int = payload.get("id")
        user_role: str = payload.get("role")

        if username is None or user_id is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Could not validate user.",
            )
        return {"username": username, "id": user_id, "role": user_role}

    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Could not validate user."
        )


@router.post("/create/user", status_code=status.HTTP_201_CREATED)
async def create_user(db: db_dependency, create_user: CreateUserRequest):
    existing_user = (
        db.query(Users)
        .filter(
            (Users.username == create_user.username)
            | (Users.email == create_user.email)
        )
        .first()
    )

    if existing_user:
        raise HTTPException(status_code=400, detail="Username or Email already exists")

    new_user = Users(
        email=create_user.email,
        username=create_user.username,
        firstName=create_user.first_name,
        lastName=create_user.last_name,
        bio=create_user.bio,
        profilePhoto=create_user.profilePhoto,
        dateOfBirth=create_user.dateOfBirth,
        phoneNumber=create_user.phoneNumber,
        password=bcrypt_context.hash(create_user.password),
        role=create_user.role,
    )

    db.add(new_user)
    db.commit()


@router.post("/token", response_model=Token)
async def login_access_token(
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()], db: db_dependency
):

    user = authenticate_user(form_data.username, form_data.password, db)

    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Could not validate user"
        )

    token = create_access_token(
        user.username, user.id, user.role, timedelta(minutes=20)
    )

    return {"access_token": token, "token_type": "bearer"}
