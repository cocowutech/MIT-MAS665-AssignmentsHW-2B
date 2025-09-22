from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from sqlalchemy.orm import Session
from database import get_db
from models import ContentItem, Question, Rubric
from routers.auth import get_current_user
from services.ai_service import AIService
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
import os
import uuid

router = APIRouter()
ai_service = AIService()

class ContentItemCreate(BaseModel):
    title: str
    content_type: str
    content: str
    cefr_level: str
    topic_tags: List[str] = []
    exam_tags: List[str] = []

class QuestionGenerate(BaseModel):
    passage_id: int
    num_questions: int = 5
    question_types: List[str] = ["multiple_choice", "true_false"]

class ContentUpload(BaseModel):
    title: str
    cefr_level: str
    topic_tags: List[str] = []
    exam_tags: List[str] = []

@router.post("/upload-text")
async def upload_text_content(
    content_data: ContentUpload,
    current_user = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Upload text content for content generation"""
    
    # Analyze text complexity
    complexity_analysis = await ai_service.analyze_text_complexity(content_data.content)
    
    # Create content item
    content_item = ContentItem(
        title=content_data.title,
        content_type="passage",
        content=content_data.content,
        cefr_level=content_data.cefr_level,
        topic_tags=content_data.topic_tags,
        exam_tags=content_data.exam_tags,
        metadata_json=complexity_analysis
    )
    
    db.add(content_item)
    db.commit()
    db.refresh(content_item)
    
    return {
        "id": content_item.id,
        "title": content_item.title,
        "cefr_level": content_item.cefr_level,
        "complexity_analysis": complexity_analysis
    }

@router.post("/upload-file")
async def upload_file_content(
    file: UploadFile = File(...),
    title: str = "",
    cefr_level: str = "B1",
    topic_tags: List[str] = [],
    exam_tags: List[str] = [],
    current_user = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Upload file content (text, image, audio)"""
    
    # Save file
    file_extension = file.filename.split('.')[-1] if '.' in file.filename else 'txt'
    filename = f"{uuid.uuid4()}.{file_extension}"
    file_path = f"uploads/content/{filename}"
    
    os.makedirs(os.path.dirname(file_path), exist_ok=True)
    
    with open(file_path, "wb") as buffer:
        content = await file.read()
        buffer.write(content)
    
    # Determine content type
    content_type = "text"
    if file_extension.lower() in ['jpg', 'jpeg', 'png', 'gif']:
        content_type = "image"
    elif file_extension.lower() in ['mp3', 'wav', 'm4a']:
        content_type = "audio"
    
    # For text files, read content
    text_content = ""
    if content_type == "text":
        try:
            text_content = content.decode('utf-8')
        except:
            text_content = "Unable to decode text content"
    
    # Create content item
    content_item = ContentItem(
        title=title or file.filename,
        content_type=content_type,
        content=text_content,
        file_path=file_path,
        cefr_level=cefr_level,
        topic_tags=topic_tags,
        exam_tags=exam_tags
    )
    
    db.add(content_item)
    db.commit()
    db.refresh(content_item)
    
    return {
        "id": content_item.id,
        "title": content_item.title,
        "content_type": content_type,
        "file_path": file_path
    }

@router.post("/generate-questions")
async def generate_questions(
    question_data: QuestionGenerate,
    current_user = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Generate questions from content"""
    
    # Get content item
    content_item = db.query(ContentItem).filter(ContentItem.id == question_data.passage_id).first()
    if not content_item:
        raise HTTPException(status_code=404, detail="Content not found")
    
    if content_item.content_type != "passage":
        raise HTTPException(status_code=400, detail="Content is not a passage")
    
    # Generate questions using AI
    questions = await ai_service.generate_reading_questions(
        content_item.content,
        content_item.cefr_level,
        question_data.num_questions
    )
    
    # Save questions to database
    saved_questions = []
    for q in questions:
        question = Question(
            question_type=q.get("type", "multiple_choice"),
            content=q.get("question", ""),
            passage=content_item.content,
            options=q.get("options", []),
            correct_answer=q.get("correct_answer", ""),
            explanation=q.get("explanation", ""),
            difficulty_logit=q.get("difficulty", 0.0),
            cefr_level=content_item.cefr_level,
            topic_tags=content_item.topic_tags,
            exam_tags=content_item.exam_tags
        )
        db.add(question)
        saved_questions.append(question)
    
    db.commit()
    
    return {
        "generated_questions": len(saved_questions),
        "questions": [
            {
                "id": q.id,
                "content": q.content,
                "type": q.question_type,
                "difficulty": q.difficulty_logit
            }
            for q in saved_questions
        ]
    }

@router.post("/generate-variants")
async def generate_content_variants(
    content_id: int,
    num_variants: int = 3,
    current_user = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Generate content variants at different difficulty levels"""
    
    # Get original content
    content_item = db.query(ContentItem).filter(ContentItem.id == content_id).first()
    if not content_item:
        raise HTTPException(status_code=404, detail="Content not found")
    
    if not content_item.content:
        raise HTTPException(status_code=400, detail="Content has no text to generate variants from")
    
    # Generate variants
    variants = await ai_service.generate_content_variants(
        content_item.content,
        content_item.cefr_level,
        num_variants
    )
    
    # Save variants
    saved_variants = []
    for i, variant_text in enumerate(variants):
        variant = ContentItem(
            title=f"{content_item.title} - Variant {i+1}",
            content_type=content_item.content_type,
            content=variant_text,
            cefr_level=content_item.cefr_level,
            topic_tags=content_item.topic_tags,
            exam_tags=content_item.exam_tags,
            metadata_json={"parent_id": content_id, "variant_number": i+1}
        )
        db.add(variant)
        saved_variants.append(variant)
    
    db.commit()
    
    return {
        "generated_variants": len(saved_variants),
        "variants": [
            {
                "id": v.id,
                "title": v.title,
                "content": v.content[:200] + "..." if len(v.content) > 200 else v.content
            }
            for v in saved_variants
        ]
    }

@router.get("/items")
async def get_content_items(
    content_type: Optional[str] = None,
    cefr_level: Optional[str] = None,
    skip: int = 0,
    limit: int = 100,
    current_user = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get content items with optional filtering"""
    
    query = db.query(ContentItem)
    
    if content_type:
        query = query.filter(ContentItem.content_type == content_type)
    
    if cefr_level:
        query = query.filter(ContentItem.cefr_level == cefr_level)
    
    items = query.offset(skip).limit(limit).all()
    
    return [
        {
            "id": item.id,
            "title": item.title,
            "content_type": item.content_type,
            "cefr_level": item.cefr_level,
            "topic_tags": item.topic_tags,
            "exam_tags": item.exam_tags,
            "created_at": item.created_at,
            "content_preview": item.content[:200] + "..." if len(item.content) > 200 else item.content
        }
        for item in items
    ]

@router.get("/items/{item_id}")
async def get_content_item(
    item_id: int,
    current_user = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get specific content item"""
    
    item = db.query(ContentItem).filter(ContentItem.id == item_id).first()
    if not item:
        raise HTTPException(status_code=404, detail="Content not found")
    
    return {
        "id": item.id,
        "title": item.title,
        "content_type": item.content_type,
        "content": item.content,
        "file_path": item.file_path,
        "cefr_level": item.cefr_level,
        "topic_tags": item.topic_tags,
        "exam_tags": item.exam_tags,
        "metadata": item.metadata_json,
        "created_at": item.created_at
    }

@router.delete("/items/{item_id}")
async def delete_content_item(
    item_id: int,
    current_user = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Delete content item"""
    
    item = db.query(ContentItem).filter(ContentItem.id == item_id).first()
    if not item:
        raise HTTPException(status_code=404, detail="Content not found")
    
    # Delete file if exists
    if item.file_path and os.path.exists(item.file_path):
        os.remove(item.file_path)
    
    db.delete(item)
    db.commit()
    
    return {"message": "Content item deleted successfully"}

@router.get("/questions")
async def get_questions(
    cefr_level: Optional[str] = None,
    question_type: Optional[str] = None,
    skip: int = 0,
    limit: int = 100,
    current_user = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get questions with optional filtering"""
    
    query = db.query(Question)
    
    if cefr_level:
        query = query.filter(Question.cefr_level == cefr_level)
    
    if question_type:
        query = query.filter(Question.question_type == question_type)
    
    questions = query.offset(skip).limit(limit).all()
    
    return [
        {
            "id": q.id,
            "content": q.content,
            "question_type": q.question_type,
            "difficulty_logit": q.difficulty_logit,
            "cefr_level": q.cefr_level,
            "topic_tags": q.topic_tags,
            "exam_tags": q.exam_tags,
            "created_at": q.created_at
        }
        for q in questions
    ]
