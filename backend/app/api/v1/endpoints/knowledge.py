from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.db.session import get_db
from app.models.knowledge import KnowledgeDocument
from app.schemas.common import ApiResponse
from pydantic import BaseModel
from typing import Optional

router = APIRouter()


class KnowledgeCreateRequest(BaseModel):
    title: str
    source: str = "manual"
    content: str
    tags: Optional[list[str]] = None


@router.get("")
async def list_knowledge(db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(KnowledgeDocument).order_by(KnowledgeDocument.created_at.desc()))
    docs = result.scalars().all()
    return ApiResponse(data=[
        {
            "id": d.id,
            "title": d.title,
            "source": d.source,
            "content": d.content,
            "tags": d.tags,
            "created_at": d.created_at.isoformat() if d.created_at else None,
        }
        for d in docs
    ])


@router.post("")
async def create_knowledge(body: KnowledgeCreateRequest, db: AsyncSession = Depends(get_db)):
    import json
    doc = KnowledgeDocument(
        title=body.title,
        source=body.source,
        content=body.content,
        tags=json.dumps(body.tags or [], ensure_ascii=False),
    )
    db.add(doc)
    await db.flush()
    return ApiResponse(data={"id": doc.id, "title": doc.title}, message="Knowledge document created")
