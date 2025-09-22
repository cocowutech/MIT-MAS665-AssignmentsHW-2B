from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from database import get_db
from models import Assessment, User, Response, SubScore
from routers.auth import get_current_user
from typing import List, Dict, Any, Optional
from pydantic import BaseModel
from datetime import datetime, timedelta
import json

router = APIRouter()

class DetailedReport(BaseModel):
    assessment_id: int
    user_info: Dict[str, Any]
    overall_scores: Dict[str, Any]
    sub_scores: List[Dict[str, Any]]
    detailed_feedback: str
    recommendations: List[str]
    next_steps: List[str]

@router.get("/user/{user_id}/summary")
async def get_user_summary(
    user_id: int,
    current_user = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get summary report for a user"""
    
    if current_user.id != user_id:
        raise HTTPException(status_code=403, detail="Not authorized")
    
    # Get user's assessments
    assessments = db.query(Assessment).filter(
        Assessment.user_id == user_id,
        Assessment.status == "completed"
    ).all()
    
    if not assessments:
        return {"message": "No completed assessments found"}
    
    # Get latest assessment
    latest_assessment = max(assessments, key=lambda a: a.completed_at)
    
    # Calculate progress over time
    progress_data = []
    for assessment in sorted(assessments, key=lambda a: a.completed_at):
        progress_data.append({
            "date": assessment.completed_at.isoformat(),
            "cefr_level": assessment.cefr_level,
            "theta_score": assessment.theta_score,
            "ket_readiness": assessment.ket_readiness,
            "pet_readiness": assessment.pet_readiness,
            "fce_readiness": assessment.fce_readiness
        })
    
    # Calculate best scores
    best_cefr = max(assessments, key=lambda a: self._cefr_to_numeric(a.cefr_level))
    best_theta = max(assessments, key=lambda a: a.theta_score or 0)
    
    return {
        "user": {
            "name": current_user.name,
            "email": current_user.email,
            "age": current_user.age
        },
        "assessment_summary": {
            "total_assessments": len(assessments),
            "latest_cefr_level": latest_assessment.cefr_level,
            "latest_theta_score": latest_assessment.theta_score,
            "best_cefr_level": best_cefr.cefr_level,
            "best_theta_score": best_theta.theta_score
        },
        "exam_readiness": {
            "ket": latest_assessment.ket_readiness,
            "pet": latest_assessment.pet_readiness,
            "fce": latest_assessment.fce_readiness
        },
        "progress_over_time": progress_data
    }

@router.get("/assessment/{assessment_id}/detailed")
async def get_detailed_assessment_report(
    assessment_id: int,
    current_user = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get detailed report for a specific assessment"""
    
    # Get assessment
    assessment = db.query(Assessment).filter(
        Assessment.id == assessment_id,
        Assessment.user_id == current_user.id
    ).first()
    
    if not assessment:
        raise HTTPException(status_code=404, detail="Assessment not found")
    
    if assessment.status != "completed":
        raise HTTPException(status_code=400, detail="Assessment not completed")
    
    # Get user info
    user = db.query(User).filter(User.id == assessment.user_id).first()
    
    # Get sub-scores
    sub_scores = db.query(SubScore).filter(SubScore.assessment_id == assessment_id).all()
    sub_score_data = [
        {
            "skill": s.skill,
            "description": s.description,
            "score": s.score,
            "max_score": s.max_score,
            "cefr_level": s.cefr_level,
            "feedback": s.feedback
        }
        for s in sub_scores
    ]
    
    # Generate detailed feedback
    detailed_feedback = self._generate_detailed_feedback(assessment, sub_score_data)
    
    # Generate recommendations
    recommendations = self._generate_recommendations(assessment, sub_score_data)
    
    # Generate next steps
    next_steps = self._generate_next_steps(assessment)
    
    return DetailedReport(
        assessment_id=assessment_id,
        user_info={
            "name": user.name,
            "email": user.email,
            "age": user.age
        },
        overall_scores={
            "cefr_level": assessment.cefr_level,
            "theta_score": assessment.theta_score,
            "standard_error": assessment.standard_error,
            "raw_score": assessment.raw_score,
            "ket_readiness": assessment.ket_readiness,
            "pet_readiness": assessment.pet_readiness,
            "fce_readiness": assessment.fce_readiness
        },
        sub_scores=sub_score_data,
        detailed_feedback=detailed_feedback,
        recommendations=recommendations,
        next_steps=next_steps
    )

@router.get("/assessment/{assessment_id}/responses")
async def get_assessment_responses(
    assessment_id: int,
    current_user = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get detailed responses for an assessment"""
    
    # Get assessment
    assessment = db.query(Assessment).filter(
        Assessment.id == assessment_id,
        Assessment.user_id == current_user.id
    ).first()
    
    if not assessment:
        raise HTTPException(status_code=404, detail="Assessment not found")
    
    # Get responses with questions
    responses = db.query(Response).filter(Response.assessment_id == assessment_id).all()
    
    response_data = []
    for response in responses:
        from models import Question
        question = db.query(Question).filter(Question.id == response.question_id).first()
        
        response_data.append({
            "question_id": response.question_id,
            "question_content": question.content if question else "Unknown",
            "question_type": question.question_type if question else "Unknown",
            "response_text": response.response_text,
            "is_correct": response.is_correct,
            "response_time": response.response_time,
            "confidence": response.confidence,
            "created_at": response.created_at.isoformat()
        })
    
    return {
        "assessment_id": assessment_id,
        "assessment_type": assessment.assessment_type,
        "total_questions": len(response_data),
        "responses": response_data
    }

@router.get("/cohort/{cohort_id}")
async def get_cohort_report(
    cohort_id: str,
    current_user = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get cohort-level report (for teachers/admins)"""
    
    # This would typically involve checking if the user has permission to view this cohort
    # For now, we'll assume they can access it
    
    # Get assessments for this cohort
    # In a real implementation, you'd have a cohort table and relationships
    assessments = db.query(Assessment).filter(
        Assessment.status == "completed"
        # Add cohort filtering logic here
    ).all()
    
    if not assessments:
        return {"message": "No assessments found for this cohort"}
    
    # Calculate cohort statistics
    cefr_distribution = {}
    exam_readiness = {"ket": [], "pet": [], "fce": []}
    completion_times = []
    
    for assessment in assessments:
        # CEFR distribution
        if assessment.cefr_level:
            cefr_distribution[assessment.cefr_level] = cefr_distribution.get(assessment.cefr_level, 0) + 1
        
        # Exam readiness
        if assessment.ket_readiness:
            exam_readiness["ket"].append(assessment.ket_readiness)
        if assessment.pet_readiness:
            exam_readiness["pet"].append(assessment.pet_readiness)
        if assessment.fce_readiness:
            exam_readiness["fce"].append(assessment.fce_readiness)
        
        # Completion time
        if assessment.completed_at and assessment.started_at:
            completion_time = (assessment.completed_at - assessment.started_at).total_seconds() / 60
            completion_times.append(completion_time)
    
    # Calculate averages
    avg_exam_readiness = {
        exam: sum(scores) / len(scores) if scores else 0
        for exam, scores in exam_readiness.items()
    }
    
    avg_completion_time = sum(completion_times) / len(completion_times) if completion_times else 0
    
    return {
        "cohort_id": cohort_id,
        "total_students": len(assessments),
        "cefr_distribution": cefr_distribution,
        "average_exam_readiness": avg_exam_readiness,
        "average_completion_time_minutes": avg_completion_time,
        "completion_rate": len(assessments) / len(assessments) if assessments else 0  # This would be calculated differently in practice
    }

def _cefr_to_numeric(self, cefr_level: str) -> int:
    """Convert CEFR level to numeric value for comparison"""
    levels = {"A1": 1, "A2": 2, "B1": 3, "B2": 4, "C1": 5, "C2": 6}
    return levels.get(cefr_level, 0)

def _generate_detailed_feedback(self, assessment: Assessment, sub_scores: List[Dict]) -> str:
    """Generate detailed feedback based on assessment results"""
    
    feedback_parts = []
    
    # Overall performance
    cefr_level = assessment.cefr_level
    theta_score = assessment.theta_score or 0
    
    if theta_score > 0.5:
        feedback_parts.append(f"Excellent performance! You've achieved CEFR level {cefr_level} with strong confidence.")
    elif theta_score > 0:
        feedback_parts.append(f"Good performance! You've achieved CEFR level {cefr_level}.")
    else:
        feedback_parts.append(f"You've achieved CEFR level {cefr_level}. There's room for improvement.")
    
    # Exam readiness
    if assessment.ket_readiness and assessment.ket_readiness > 0.8:
        feedback_parts.append("You're well-prepared for the KET exam.")
    elif assessment.ket_readiness and assessment.ket_readiness > 0.6:
        feedback_parts.append("You're approaching readiness for the KET exam.")
    
    if assessment.pet_readiness and assessment.pet_readiness > 0.8:
        feedback_parts.append("You're well-prepared for the PET exam.")
    elif assessment.pet_readiness and assessment.pet_readiness > 0.6:
        feedback_parts.append("You're approaching readiness for the PET exam.")
    
    if assessment.fce_readiness and assessment.fce_readiness > 0.8:
        feedback_parts.append("You're well-prepared for the FCE exam.")
    elif assessment.fce_readiness and assessment.fce_readiness > 0.6:
        feedback_parts.append("You're approaching readiness for the FCE exam.")
    
    # Sub-skill feedback
    for sub_score in sub_scores:
        skill = sub_score["skill"]
        score = sub_score["score"]
        max_score = sub_score["max_score"]
        percentage = (score / max_score) * 100 if max_score > 0 else 0
        
        if percentage >= 80:
            feedback_parts.append(f"Strong performance in {skill.replace('_', ' ').title()}.")
        elif percentage >= 60:
            feedback_parts.append(f"Good performance in {skill.replace('_', ' ').title()}, with room for improvement.")
        else:
            feedback_parts.append(f"Focus on improving {skill.replace('_', ' ').title()}.")
    
    return " ".join(feedback_parts)

def _generate_recommendations(self, assessment: Assessment, sub_scores: List[Dict]) -> List[str]:
    """Generate learning recommendations based on assessment results"""
    
    recommendations = []
    
    # CEFR-based recommendations
    cefr_level = assessment.cefr_level
    if cefr_level in ["A1", "A2"]:
        recommendations.extend([
            "Focus on building basic vocabulary and grammar foundations",
            "Practice with simple reading materials and basic conversations",
            "Work on pronunciation and basic speaking skills"
        ])
    elif cefr_level in ["B1", "B2"]:
        recommendations.extend([
            "Practice with intermediate-level materials and authentic texts",
            "Focus on fluency and natural expression in speaking and writing",
            "Work on understanding implicit meaning and inference"
        ])
    else:  # C1, C2
        recommendations.extend([
            "Engage with advanced, authentic materials across various topics",
            "Focus on nuanced expression and sophisticated language use",
            "Practice with complex texts and academic writing"
        ])
    
    # Sub-skill specific recommendations
    for sub_score in sub_scores:
        skill = sub_score["skill"]
        score = sub_score["score"]
        max_score = sub_score["max_score"]
        percentage = (score / max_score) * 100 if max_score > 0 else 0
        
        if percentage < 60:
            if "vocabulary" in skill.lower():
                recommendations.append("Expand vocabulary through reading and vocabulary building exercises")
            elif "grammar" in skill.lower():
                recommendations.append("Review grammar rules and practice with grammar exercises")
            elif "fluency" in skill.lower():
                recommendations.append("Practice speaking regularly to improve fluency and confidence")
            elif "coherence" in skill.lower():
                recommendations.append("Work on organizing ideas and using linking words effectively")
    
    return list(set(recommendations))  # Remove duplicates

def _generate_next_steps(self, assessment: Assessment) -> List[str]:
    """Generate next steps based on assessment results"""
    
    next_steps = []
    
    # Immediate next steps
    next_steps.append("Review your detailed feedback and focus areas")
    next_steps.append("Set specific learning goals based on your CEFR level")
    
    # Exam preparation
    if assessment.ket_readiness and assessment.ket_readiness > 0.7:
        next_steps.append("Consider registering for the KET exam")
    if assessment.pet_readiness and assessment.pet_readiness > 0.7:
        next_steps.append("Consider registering for the PET exam")
    if assessment.fce_readiness and assessment.fce_readiness > 0.7:
        next_steps.append("Consider registering for the FCE exam")
    
    # Learning path
    cefr_level = assessment.cefr_level
    if cefr_level in ["A1", "A2"]:
        next_steps.append("Continue with A2/B1 level course materials")
    elif cefr_level in ["B1", "B2"]:
        next_steps.append("Progress to B2/C1 level course materials")
    else:
        next_steps.append("Focus on advanced practice and exam preparation")
    
    next_steps.append("Schedule regular practice sessions and track your progress")
    
    return next_steps
