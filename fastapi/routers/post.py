import logging
from enum import Enum
from typing import Annotated

import sqlalchemy

from fastapi import APIRouter, HTTPException, Depends
from fastapi.database import database, post_table, comment_table, like_table
from fastapi.models.post import UserPost, UserPostIn, CommentIn, Comment, UserPostWithComments, PostLike, PostLikeIn, \
    UserPostWithLikes
from fastapi.models.user import User
from fastapi.security import get_current_user

router = APIRouter()

logger = logging.getLogger(__name__)

select_post_and_likes = (
    sqlalchemy.select(post_table, sqlalchemy.func.count(like_table.c.id).label("likes"))
    .select_from(post_table.outerjoin(like_table))
    .group_by(post_table.c.id)
)


async def find_post(post_id: int):
    query = post_table.select().where(post_table.c.id == post_id)
    return await database.fetch_one(query)


@router.post("/post", response_model=UserPost, status_code=201)
async def create_post(post: UserPostIn, current_user: Annotated[User, Depends(get_current_user)]) -> dict:
    data = {**post.model_dump(), "user_id": current_user.id}
    query = post_table.insert().values(data)
    last_recorded_id = await database.execute(query)
    return {**data, "id": last_recorded_id}


class PostSorting(str, Enum):
    new = "new"
    old = "old"
    most_like = "most_like"


@router.get("/post", response_model=list[UserPostWithLikes])
async def get_all_posts(sorting: PostSorting = PostSorting.new):
    match sorting:
        case PostSorting.new:
            query = select_post_and_likes.order_by(post_table.c.id.desc())
        case PostSorting.old:
            query = select_post_and_likes.order_by(post_table.c.id.asc())
        case PostSorting.most_like:
            query = select_post_and_likes.order_by(sqlalchemy.desc("likes"))

    logger.debug(query)
    return await database.fetch_all(query)


@router.post("/comment", response_model=Comment, status_code=201)
async def create_comment(comment: CommentIn, current_user: Annotated[User, Depends(get_current_user)]) -> dict:
    post = await find_post(comment.post_id)
    if not post:
        raise HTTPException(status_code=404, detail="Post not found")

    data = {**comment.model_dump(), "user_id": current_user.id}
    query = comment_table.insert().values(data)
    last_record_id = await database.execute(query)
    return {**data, "id": last_record_id}


@router.get("/post/{post_id}/comment", response_model=list[Comment])
async def get_post_comments(post_id: int):
    query = comment_table.select().where(comment_table.c.post_id == post_id)
    return await database.fetch_all(query)


@router.get("/post/{post_id}", response_model=UserPostWithComments)
async def get_post_with_comments(post_id: int):
    query = select_post_and_likes.where(post_table.c.id == post_id)
    post = await database.fetch_one(query)

    if not post:
        raise HTTPException(status_code=404, detail="Post not found")

    return {
        "post": post,
        "comments": await get_post_comments(post_id),
    }


@router.post("/like", response_model=PostLike, status_code=201)
async def like_post(
        like: PostLikeIn,
        current_user: Annotated[User, Depends(get_current_user)]
) -> dict:
    post = await find_post(like.post_id)
    if not post:
        raise HTTPException(status_code=404, detail="Post not found")

    data = {**like.model_dump(), "user_id": current_user.id}
    query = like_table.insert().values(data)
    last_record_id = await database.execute(query)

    return {**data, "id": last_record_id}
