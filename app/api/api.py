from fastapi import APIRouter

from app.api.endpoints import users, auth, articles, categories, tags, comments, search

api_router = APIRouter()

# Include all the endpoint routers
api_router.include_router(auth.router, tags=["auth"])
api_router.include_router(users.router, prefix="/users", tags=["users"])
api_router.include_router(articles.router, prefix="/articles", tags=["articles"])
api_router.include_router(categories.router, prefix="/categories", tags=["categories"])
api_router.include_router(tags.router, prefix="/tags", tags=["tags"])
api_router.include_router(comments.router, prefix="/comments", tags=["comments"])
api_router.include_router(search.router, prefix="/search", tags=["search"]) 