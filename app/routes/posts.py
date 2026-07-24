from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import get_db
from app.models import Post, User
from app.schemas import PostCreate, PostResponse

router = APIRouter()

@router.get("/posts", response_model=list[PostResponse])
def get_posts(db: Session = Depends(get_db)):
    posts = db.query(Post).order_by(Post.created_at.desc()).limit(50).all()

    result = []
    for post in posts:
        user = db.query(User).filter(User.email == post.user_email).first()
        result.append({
            "id": post.id,
            "user_email": post.user_email,
            "content": post.content,
            "likes": post.likes,
            "created_at": post.created_at,
            "full_name": user.full_name if user else "Unknown",
        })

    return result

@router.post("/posts")
def create_post(data: PostCreate, db: Session = Depends(get_db)):
    post = Post(
        user_email=data.user_email,
        content=data.content,
    )
    db.add(post)
    db.commit()
    db.refresh(post)

    return {"message": "Post created", "id": post.id}

@router.post("/posts/{post_id}/like")
def like_post(post_id: int, db: Session = Depends(get_db)):
    post = db.query(Post).filter(Post.id == post_id).first()
    if not post:
        raise HTTPException(status_code=404, detail="Post not found")

    post.likes += 1
    db.commit()
    db.refresh(post)

    return {"likes": post.likes}

@router.delete("/posts/{post_id}")
def delete_post(post_id: int, user_email: str, db: Session = Depends(get_db)):
    post = db.query(Post).filter(Post.id == post_id).first()
    if not post:
        raise HTTPException(status_code=404, detail="Post not found")

    if post.user_email != user_email:
        raise HTTPException(status_code=403, detail="You can only delete your own posts")

    db.delete(post)
    db.commit()

    return {"message": "Post deleted"}