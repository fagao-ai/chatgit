from fastapi import APIRouter

from chatgit.backend.views.qa import router as qa_router

app_router = APIRouter(prefix="/api/v1")
app_router.include_router(qa_router)
