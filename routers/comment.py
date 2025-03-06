from fastapi import APIRouter, Depends, HTTPException
from database import SessionLocal
from typing import Annotated, Optional
from sqlalchemy.orm import Session
from .auth import get_current_user
from starlette import status
from models import RecipeComments, Recipe
from pydantic import BaseModel

router = APIRouter(prefix="/comments", tags=["comments"])


class CommentRequest(BaseModel):
    comment: str
    parentCommentId: Optional[int] = None


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


db_dependency = Annotated[Session, Depends(get_db)]
user_dependency = Annotated[dict, Depends(get_current_user)]


@router.get("/{recipe_id}", status_code=status.HTTP_200_OK)
async def get_all_comments(db: db_dependency, recipe_id: int):
    comments = (
        db.query(RecipeComments).filter(RecipeComments.recipeId == recipe_id).all()
    )

    if not comments:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="No comments found"
        )

    return {"comments": comments}


@router.get("/{recipe_id}/{comment_id}", status_code=status.HTTP_200_OK)
async def get_all_comments(db: db_dependency, recipe_id: int, comment_id: int):
    comment = (
        db.query(RecipeComments)
        .filter(
            (RecipeComments.recipeId == recipe_id) & (RecipeComments.id == comment_id)
        )
        .first()
    )

    if not comment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="No comments found"
        )

    def get_replies(parent_id):
        replies = (
            db.query(RecipeComments)
            .filter(RecipeComments.parentCommentId == parent_id)
            .all()
        )

        return [
            {
                "id": reply.id,
                "userId": reply.userId,
                "comment": reply.comment,
                "replies": get_replies(reply.id),
            }
            for reply in replies
        ]

    comment_data = [
        {
            "id": comment.id,
            "userId": comment.userId,
            "comment": comment.comment,
            "replies": get_replies(comment.id),
        }
    ]

    return comment_data


@router.post("/{recipe_id}", status_code=status.HTTP_201_CREATED)
async def add_comment(
    user: user_dependency,
    db: db_dependency,
    recipe_id: int,
    comment_request: CommentRequest,
):
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Unauthorize User"
        )

    recipe_commented = db.query(Recipe).filter(Recipe.id == recipe_id).first()

    if not recipe_commented:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Recipe not found"
        )

    if comment_request.parentCommentId:
        parent_comment = (
            db.query(RecipeComments)
            .filter(
                (RecipeComments.recipeId == recipe_id)
                & (RecipeComments.id == comment_request.parentCommentId)
            )
            .first()
        )

        if not parent_comment:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Parent comment does not exists.",
            )

    new_comment = RecipeComments(
        userId=user.get("id"),
        recipeId=recipe_id,
        comment=comment_request.comment,
        parentCommentId=comment_request.parentCommentId,
    )

    db.add(new_comment)
    db.commit()


@router.put("/{recipe_id}/{comment_id}", status_code=status.HTTP_204_NO_CONTENT)
async def update_comment(
    user: user_dependency,
    db: db_dependency,
    recipe_id: int,
    comment_id: int,
    comment_request: CommentRequest,
):
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Unauthorize User"
        )

    recipe_comment = (
        db.query(RecipeComments)
        .filter(
            (RecipeComments.id == comment_id)
            & (RecipeComments.userId == user.get("id"))
        )
        .first()
    )

    if not recipe_comment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Comment not found"
        )

    if comment_request.comment is not None:
        recipe_comment.comment = comment_request.comment

    db.commit()


@router.delete("/{recipe_id}/{comment_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_comment(
    user: user_dependency, db: db_dependency, recipe_id: int, comment_id: int
):
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Unauthorize User"
        )

    comment = db.query(RecipeComments).filter(RecipeComments.id == comment_id).first()

    if not comment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Comment not found"
        )

    if comment.userId != user.get("id"):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You can not delete this comment.",
        )

    db.delete(comment)
    db.commit()
