from fastapi import APIRouter, Depends, HTTPException
from database import SessionLocal
from .auth import get_current_user
from typing import Annotated, Optional
from sqlalchemy.orm import Session
from starlette import status
from passlib.context import CryptContext
from models import Users, Follows
from pydantic import BaseModel
from datetime import date

router = APIRouter(prefix="/user", tags=["user"])


class UserVerification(BaseModel):
    password: str
    new_password: str


class UpdateUserRequest(BaseModel):
    email: Optional[str] = None
    username: Optional[str] = None
    firstName: Optional[str] = None
    lastName: Optional[str] = None
    bio: Optional[str] = None
    profilePhoto: Optional[str] = None
    dateOfBirth: Optional[date] = None
    phoneNumber: Optional[str] = None


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


db_dependency = Annotated[Session, Depends(get_db)]
user_dependency = Annotated[dict, Depends(get_current_user)]
bcrypt_context = CryptContext(schemes="bcrypt", deprecated="auto")


@router.get("/", status_code=status.HTTP_200_OK)
async def get_user(db: db_dependency, user: user_dependency):
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Unauthorized User"
        )

    return db.query(Users).filter(Users.id == user.get("id")).first()


@router.post("/follow/{followee_id}", status_code=status.HTTP_204_NO_CONTENT)
def follow_user(followee_id: int, user: user_dependency, db: db_dependency):
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Unauthorize User"
        )

    follower_id = user.get("id")

    if follower_id == followee_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="You cannot follow yourself"
        )

    existing_follow = (
        db.query(Follows)
        .filter(
            (Follows.followerId == user.get("id")) & (Follows.followeeId == followee_id)
        )
        .first()
    )

    if existing_follow:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="You already follow the user",
        )

    new_follower = Follows(followerId=follower_id, followeeId=followee_id)
    db.add(new_follower)

    db.query(Users).filter(Users.id == follower_id).update(
        {"followingCount": Users.followingCount + 1}
    )
    db.query(Users).filter(Users.id == followee_id).update(
        {"followersCount": Users.followersCount + 1}
    )

    db.commit()


@router.post("/unfollow/{followee_id}", status_code=status.HTTP_204_NO_CONTENT)
def unfollow_user(followee_id: int, user: user_dependency, db: db_dependency):
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Unauthorize User"
        )

    follower_id = user.get("id")

    follow = (
        db.query(Follows)
        .filter(
            (Follows.followerId == follower_id) & (Follows.followeeId == followee_id)
        )
        .first()
    )

    if not follow:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="You have not followed the user",
        )

    db.delete(follow)

    db.query(Users).filter(Users.id == follower_id).update(
        {"followingCount": Users.followingCount - 1}
    )
    db.query(Users).filter(Users.id == followee_id).update(
        {"followersCount": Users.followersCount - 1}
    )

    db.commit()


@router.put("/password", status_code=status.HTTP_204_NO_CONTENT)
async def change_password(
    db: db_dependency, user: user_dependency, user_verificaiton: UserVerification
):
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Unauthorized User"
        )

    user_model = db.query(Users).filter(Users.id == user.get("id")).first()

    if not bcrypt_context.verify(user_verificaiton.password, user_model.password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid Password"
        )

    user_model.password = bcrypt_context.hash(user_verificaiton.new_password)

    db.add(user_model)
    db.commit()


@router.put("/profile", status_code=status.HTTP_204_NO_CONTENT)
async def update_profile(
    db: db_dependency, user: user_dependency, update_user: UpdateUserRequest
):
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Unauthorized User"
        )

    user_model = db.query(Users).filter(Users.id == user.get("id")).first()

    user_model.email = update_user.email
    user_model.username = update_user.username
    user_model.firstName = update_user.firstName
    user_model.lastName = update_user.lastName
    user_model.bio = update_user.bio
    user_model.profilePhoto = update_user.profilePhoto
    user_model.dateOfBirth = update_user.dateOfBirth
    user_model.phoneNumber = update_user.phoneNumber

    db.add(user_model)
    db.commit()
