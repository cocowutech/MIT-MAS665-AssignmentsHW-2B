from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from database import get_db
from models import User, Assessment, Question, ContentItem, Response
from routers.auth import get_current_user
from pydantic import BaseModel
from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta
import pandas as pd
import io

router = APIRouter()

class AdminStats(BaseModel):
    total_users: int
    total_assessments: int
    completed_assessments: int
    average_completion_time: float
    cefr_distribution: Dict[str, int]
    exam_readiness: Dict[str, float]

class UserManagement(BaseModel):
    user_id: int
    action: str  # activate, deactivate, delete

@router.get("/stats")
async def get_admin_stats(
    current_user = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get admin dashboard statistics"""
    
    # Basic counts
    total_users = db.query(User).count()
    total_assessments = db.query(Assessment).count()
    completed_assessments = db.query(Assessment).filter(Assessment.status == "completed").count()
    
    # Average completion time
    completed = db.query(Assessment).filter(Assessment.status == "completed").all()
    if completed:
        total_time = sum([
            (a.completed_at - a.started_at).total_seconds() / 60  # minutes
            for a in completed if a.completed_at and a.started_at
        ])
        avg_completion_time = total_time / len(completed)
    else:
        avg_completion_time = 0
    
    # CEFR level distribution
    cefr_distribution = {}
    for assessment in completed:
        if assessment.cefr_level:
            cefr_distribution[assessment.cefr_level] = cefr_distribution.get(assessment.cefr_level, 0) + 1
    
    # Exam readiness averages
    exam_readiness = {
        "ket": sum(a.ket_readiness for a in completed if a.ket_readiness) / len(completed) if completed else 0,
        "pet": sum(a.pet_readiness for a in completed if a.pet_readiness) / len(completed) if completed else 0,
        "fce": sum(a.fce_readiness for a in completed if a.fce_readiness) / len(completed) if completed else 0
    }
    
    return AdminStats(
        total_users=total_users,
        total_assessments=total_assessments,
        completed_assessments=completed_assessments,
        average_completion_time=avg_completion_time,
        cefr_distribution=cefr_distribution,
        exam_readiness=exam_readiness
    )

@router.get("/users")
async def get_all_users(
    skip: int = 0,
    limit: int = 100,
    current_user = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get all users for admin management"""
    
    users = db.query(User).offset(skip).limit(limit).all()
    
    return [
        {
            "id": user.id,
            "email": user.email,
            "name": user.name,
            "age": user.age,
            "is_active": user.is_active,
            "created_at": user.created_at,
            "total_assessments": db.query(Assessment).filter(Assessment.user_id == user.id).count()
        }
        for user in users
    ]

@router.post("/users/{user_id}/manage")
async def manage_user(
    user_id: int,
    action: str,
    current_user = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Manage user account (activate, deactivate, delete)"""
    
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    if action == "activate":
        user.is_active = True
    elif action == "deactivate":
        user.is_active = False
    elif action == "delete":
        # Delete user and all related data
        db.query(Assessment).filter(Assessment.user_id == user_id).delete()
        db.delete(user)
    else:
        raise HTTPException(status_code=400, detail="Invalid action")
    
    db.commit()
    
    return {"message": f"User {action} successful"}

@router.get("/assessments")
async def get_all_assessments(
    status: Optional[str] = None,
    user_id: Optional[int] = None,
    skip: int = 0,
    limit: int = 100,
    current_user = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get all assessments for admin review"""
    
    query = db.query(Assessment)
    
    if status:
        query = query.filter(Assessment.status == status)
    
    if user_id:
        query = query.filter(Assessment.user_id == user_id)
    
    assessments = query.offset(skip).limit(limit).all()
    
    return [
        {
            "id": a.id,
            "user_id": a.user_id,
            "assessment_type": a.assessment_type,
            "status": a.status,
            "cefr_level": a.cefr_level,
            "raw_score": a.raw_score,
            "theta_score": a.theta_score,
            "ket_readiness": a.ket_readiness,
            "pet_readiness": a.pet_readiness,
            "fce_readiness": a.fce_readiness,
            "started_at": a.started_at,
            "completed_at": a.completed_at
        }
        for a in assessments
    ]

@router.get("/content/overview")
async def get_content_overview(
    current_user = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get content overview for admin"""
    
    # Content items by type
    content_by_type = {}
    content_items = db.query(ContentItem).all()
    for item in content_items:
        content_type = item.content_type
        if content_type not in content_by_type:
            content_by_type[content_type] = 0
        content_by_type[content_type] += 1
    
    # Questions by CEFR level
    questions_by_level = {}
    questions = db.query(Question).all()
    for question in questions:
        level = question.cefr_level
        if level not in questions_by_level:
            questions_by_level[level] = 0
        questions_by_level[level] += 1
    
    # Questions by type
    questions_by_type = {}
    for question in questions:
        q_type = question.question_type
        if q_type not in questions_by_type:
            questions_by_type[q_type] = 0
        questions_by_type[q_type] += 1
    
    return {
        "content_items": {
            "total": len(content_items),
            "by_type": content_by_type
        },
        "questions": {
            "total": len(questions),
            "by_cefr_level": questions_by_level,
            "by_type": questions_by_type
        }
    }

@router.get("/export/assessments")
async def export_assessments(
    format: str = "csv",
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    current_user = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Export assessment data"""
    
    query = db.query(Assessment).filter(Assessment.status == "completed")
    
    if start_date:
        start_dt = datetime.fromisoformat(start_date)
        query = query.filter(Assessment.started_at >= start_dt)
    
    if end_date:
        end_dt = datetime.fromisoformat(end_date)
        query = query.filter(Assessment.started_at <= end_dt)
    
    assessments = query.all()
    
    # Prepare data for export
    data = []
    for assessment in assessments:
        user = db.query(User).filter(User.id == assessment.user_id).first()
        data.append({
            "assessment_id": assessment.id,
            "user_email": user.email if user else "Unknown",
            "user_name": user.name if user else "Unknown",
            "user_age": user.age if user else None,
            "assessment_type": assessment.assessment_type,
            "cefr_level": assessment.cefr_level,
            "raw_score": assessment.raw_score,
            "theta_score": assessment.theta_score,
            "standard_error": assessment.standard_error,
            "ket_readiness": assessment.ket_readiness,
            "pet_readiness": assessment.pet_readiness,
            "fce_readiness": assessment.fce_readiness,
            "started_at": assessment.started_at.isoformat() if assessment.started_at else None,
            "completed_at": assessment.completed_at.isoformat() if assessment.completed_at else None,
            "completion_time_minutes": (
                (assessment.completed_at - assessment.started_at).total_seconds() / 60
                if assessment.completed_at and assessment.started_at else None
            )
        })
    
    if format == "csv":
        df = pd.DataFrame(data)
        output = io.StringIO()
        df.to_csv(output, index=False)
        return {"csv_data": output.getvalue()}
    
    return {"data": data}

@router.get("/export/responses/{assessment_id}")
async def export_assessment_responses(
    assessment_id: int,
    current_user = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Export detailed responses for a specific assessment"""
    
    assessment = db.query(Assessment).filter(Assessment.id == assessment_id).first()
    if not assessment:
        raise HTTPException(status_code=404, detail="Assessment not found")
    
    responses = db.query(Response).filter(Response.assessment_id == assessment_id).all()
    
    data = []
    for response in responses:
        question = db.query(Question).filter(Question.id == response.question_id).first()
        data.append({
            "response_id": response.id,
            "question_id": response.question_id,
            "question_content": question.content if question else "Unknown",
            "question_type": question.question_type if question else "Unknown",
            "response_text": response.response_text,
            "is_correct": response.is_correct,
            "response_time": response.response_time,
            "confidence": response.confidence,
            "created_at": response.created_at.isoformat()
        })
    
    return {"assessment_id": assessment_id, "responses": data}

@router.get("/analytics/performance")
async def get_performance_analytics(
    days: int = 30,
    current_user = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get performance analytics over time"""
    
    end_date = datetime.utcnow()
    start_date = end_date - timedelta(days=days)
    
    # Daily completion counts
    daily_completions = {}
    completed_assessments = db.query(Assessment).filter(
        Assessment.status == "completed",
        Assessment.completed_at >= start_date,
        Assessment.completed_at <= end_date
    ).all()
    
    for assessment in completed_assessments:
        if assessment.completed_at:
            date_key = assessment.completed_at.date().isoformat()
            daily_completions[date_key] = daily_completions.get(date_key, 0) + 1
    
    # CEFR level trends
    cefr_trends = {}
    for assessment in completed_assessments:
        if assessment.cefr_level:
            level = assessment.cefr_level
            if level not in cefr_trends:
                cefr_trends[level] = 0
            cefr_trends[level] += 1
    
    # Average scores by assessment type
    type_scores = {}
    for assessment in completed_assessments:
        a_type = assessment.assessment_type
        if a_type not in type_scores:
            type_scores[a_type] = []
        if assessment.raw_score is not None:
            type_scores[a_type].append(assessment.raw_score)
    
    avg_scores = {
        a_type: sum(scores) / len(scores) if scores else 0
        for a_type, scores in type_scores.items()
    }
    
    return {
        "period_days": days,
        "daily_completions": daily_completions,
        "cefr_distribution": cefr_trends,
        "average_scores_by_type": avg_scores,
        "total_completions": len(completed_assessments)
    }
