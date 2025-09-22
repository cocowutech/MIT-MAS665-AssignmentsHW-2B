from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from sqlalchemy.orm import Session
from database import get_db
from models import Assessment, Question, Response, User, SubScore
from routers.auth import get_current_user
from services.adaptive_engine import AdaptiveEngine
from services.scoring_service import ScoringService
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
import os
import uuid
from datetime import datetime

router = APIRouter()
adaptive_engine = AdaptiveEngine()
scoring_service = ScoringService()

class AssessmentStart(BaseModel):
    assessment_type: str  # reading, speaking, writing

class QuestionResponse(BaseModel):
    question_id: int
    response_text: Optional[str] = None
    response_audio: Optional[str] = None
    response_time: float
    confidence: Optional[float] = None

class AssessmentResult(BaseModel):
    assessment_id: int
    cefr_level: str
    raw_score: float
    theta_score: float
    standard_error: float
    ket_readiness: float
    pet_readiness: float
    fce_readiness: float
    sub_scores: List[Dict[str, Any]]
    feedback: str
    recommendations: List[str]
    lexile_estimate: int | None = None
    lexile_ci_low: int | None = None
    lexile_ci_high: int | None = None
    recommended_range_low: int | None = None
    recommended_range_high: int | None = None

@router.post("/start")
async def start_assessment(
    assessment_data: AssessmentStart,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Start a new assessment"""
    
    # Determine available question pool for this assessment type
    available_questions = db.query(Question).filter(
        Question.assessment_category == assessment_data.assessment_type
    ).all()

    if not available_questions:
        raise HTTPException(status_code=404, detail="No questions available for this assessment type")

    # Create new assessment
    assessment = Assessment(
        user_id=current_user.id,
        assessment_type=assessment_data.assessment_type,
        status="in_progress",
        total_questions=15 if len(available_questions) >= 15 else len(available_questions)
    )
    db.add(assessment)
    db.commit()
    db.refresh(assessment)

    # Get first question (medium difficulty start is handled in adaptive engine)
    first_question = adaptive_engine.select_next_question(db, assessment.id, [])

    if not first_question:
        raise HTTPException(status_code=404, detail="No questions available")

    assessment.current_question = 1
    db.commit()

    return {
        "assessment_id": assessment.id,
        "question": {
            "id": first_question.id,
            "content": first_question.content,
            "passage": first_question.passage,
            "options": first_question.options,
            "question_type": first_question.question_type,
            "lexile_level": first_question.lexile_level,
            "assessment_category": first_question.assessment_category,
            "difficulty_logit": first_question.difficulty_logit
        },
        "progress": {
            "current": 1,
            "total": assessment.total_questions
        }
    }

@router.get("/{assessment_id}/next")
async def get_next_question(
    assessment_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get the next question in the assessment"""
    
    # Get assessment
    assessment = db.query(Assessment).filter(
        Assessment.id == assessment_id,
        Assessment.user_id == current_user.id
    ).first()
    
    if not assessment:
        raise HTTPException(status_code=404, detail="Assessment not found")
    
    if assessment.status != "in_progress":
        raise HTTPException(status_code=400, detail="Assessment not in progress")
    
    # Get current responses
    responses = db.query(Response).filter(Response.assessment_id == assessment_id).order_by(Response.created_at).all()
    response_data = [
        {
            "question_id": r.question_id,
            "is_correct": r.is_correct,
            "response_time": r.response_time,
            "question_difficulty": r.question.difficulty_logit,
            "question_lexile": r.question.lexile_level
        }
        for r in responses
    ]
    
    # Check if should stop
    if adaptive_engine.should_stop(response_data, assessment):
        result = await complete_assessment(assessment_id, current_user, db)
        return {
            "completed": True,
            "result": result
        }
    
    # Get next question
    next_question = adaptive_engine.select_next_question(db, assessment_id, response_data)
    
    if not next_question:
        result = await complete_assessment(assessment_id, current_user, db)
        return {
            "completed": True,
            "result": result
        }

    # Update progress to reflect the upcoming question number
    assessment.current_question = len(responses) + 1
    db.commit()
    
    return {
        "question": {
            "id": next_question.id,
            "content": next_question.content,
            "passage": next_question.passage,
            "options": next_question.options,
            "question_type": next_question.question_type,
            "lexile_level": next_question.lexile_level,
            "assessment_category": next_question.assessment_category,
            "difficulty_logit": next_question.difficulty_logit
        },
        "progress": {
            "current": assessment.current_question,
            "total": assessment.total_questions
        }
    }

@router.post("/{assessment_id}/respond")
async def submit_response(
    assessment_id: int,
    response_data: QuestionResponse,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Submit a response to a question"""
    
    # Get assessment
    assessment = db.query(Assessment).filter(
        Assessment.id == assessment_id,
        Assessment.user_id == current_user.id
    ).first()
    
    if not assessment:
        raise HTTPException(status_code=404, detail="Assessment not found")
    
    if assessment.status != "in_progress":
        raise HTTPException(status_code=400, detail="Assessment not in progress")
    
    # Get question
    question = db.query(Question).filter(Question.id == response_data.question_id).first()
    if not question:
        raise HTTPException(status_code=404, detail="Question not found")
    
    # Score the response
    if assessment.assessment_type == "reading":
        score_result = await scoring_service.score_reading_response(
            response_data.question_id,
            response_data.response_text or "",
            question.correct_answer
        )
    else:
        # For speaking/writing, we'll score later with AI
        score_result = {"is_correct": True, "score": 1.0, "feedback": ""}
    
    # Save response
    response = Response(
        assessment_id=assessment_id,
        question_id=response_data.question_id,
        response_text=response_data.response_text,
        response_audio=response_data.response_audio,
        is_correct=score_result["is_correct"],
        response_time=response_data.response_time,
        confidence=response_data.confidence
    )
    db.add(response)
    db.commit()

    # Determine if another question should be served
    responses = db.query(Response).filter(Response.assessment_id == assessment_id).order_by(Response.created_at).all()
    response_history = [
        {
            "question_id": r.question_id,
            "is_correct": r.is_correct,
            "response_time": r.response_time,
            "question_difficulty": r.question.difficulty_logit,
            "question_lexile": r.question.lexile_level
        }
        for r in responses
    ]

    if adaptive_engine.should_stop(response_history, assessment):
        result = await complete_assessment(assessment_id, current_user, db)
        return {
            "response_id": response.id,
            "is_correct": score_result["is_correct"],
            "feedback": score_result.get("feedback", ""),
            "next_question_available": False,
            "completed": True,
            "result": result
        }

    next_question = adaptive_engine.select_next_question(db, assessment_id, response_history)

    if not next_question:
        result = await complete_assessment(assessment_id, current_user, db)
        return {
            "response_id": response.id,
            "is_correct": score_result["is_correct"],
            "feedback": score_result.get("feedback", ""),
            "next_question_available": False,
            "completed": True,
            "result": result
        }

    return {
        "response_id": response.id,
        "is_correct": score_result["is_correct"],
        "feedback": score_result.get("feedback", ""),
        "next_question_available": True,
        "completed": False
    }

@router.post("/{assessment_id}/upload-audio")
async def upload_audio_response(
    assessment_id: int,
    question_id: int,
    audio_file: UploadFile = File(...),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Upload audio response for speaking assessment"""
    
    # Get assessment
    assessment = db.query(Assessment).filter(
        Assessment.id == assessment_id,
        Assessment.user_id == current_user.id
    ).first()
    
    if not assessment:
        raise HTTPException(status_code=404, detail="Assessment not found")
    
    if assessment.assessment_type != "speaking":
        raise HTTPException(status_code=400, detail="Not a speaking assessment")
    
    # Save audio file
    file_extension = audio_file.filename.split('.')[-1] if '.' in audio_file.filename else 'wav'
    filename = f"{assessment_id}_{question_id}_{uuid.uuid4()}.{file_extension}"
    file_path = f"uploads/audio/{filename}"
    
    os.makedirs(os.path.dirname(file_path), exist_ok=True)
    
    with open(file_path, "wb") as buffer:
        content = await audio_file.read()
        buffer.write(content)
    
    # Process audio
    audio_result = await scoring_service.process_audio_response(file_path)
    
    if not audio_result["success"]:
        raise HTTPException(status_code=400, detail=f"Audio processing failed: {audio_result.get('error', 'Unknown error')}")
    
    # Get question for scoring
    question = db.query(Question).filter(Question.id == question_id).first()
    if not question:
        raise HTTPException(status_code=404, detail="Question not found")
    
    # Score speaking response
    ai_scores = await scoring_service.score_speaking_response(
        audio_result["transcript"],
        question.content,
        "B1"  # Default CEFR level for scoring
    )
    
    # Save response
    response = Response(
        assessment_id=assessment_id,
        question_id=question_id,
        response_text=audio_result["transcript"],
        response_audio=file_path,
        is_correct=True,  # Speaking responses are not simply correct/incorrect
        response_time=0.0,  # Will be calculated from audio duration
        confidence=ai_scores.get("overall_score", 0) / 5.0
    )
    db.add(response)
    db.commit()
    
    return {
        "transcript": audio_result["transcript"],
        "fluency_metrics": audio_result["fluency_metrics"],
        "ai_scores": ai_scores,
        "response_id": response.id
    }

@router.post("/{assessment_id}/upload-writing")
async def upload_writing_response(
    assessment_id: int,
    question_id: int,
    image_file: Optional[UploadFile] = File(None),
    text: Optional[str] = None,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Upload writing response (text or image)"""
    
    # Get assessment
    assessment = db.query(Assessment).filter(
        Assessment.id == assessment_id,
        Assessment.user_id == current_user.id
    ).first()
    
    if not assessment:
        raise HTTPException(status_code=404, detail="Assessment not found")
    
    if assessment.assessment_type != "writing":
        raise HTTPException(status_code=400, detail="Not a writing assessment")
    
    file_path = None
    if image_file:
        # Save image file
        file_extension = image_file.filename.split('.')[-1] if '.' in image_file.filename else 'png'
        filename = f"{assessment_id}_{question_id}_{uuid.uuid4()}.{file_extension}"
        file_path = f"uploads/writing/{filename}"
        
        os.makedirs(os.path.dirname(file_path), exist_ok=True)
        
        with open(file_path, "wb") as buffer:
            content = await image_file.read()
            buffer.write(content)
    
    # Process writing
    writing_result = await scoring_service.process_writing_response(file_path, text)
    
    if not writing_result["success"]:
        raise HTTPException(status_code=400, detail=f"Writing processing failed: {writing_result.get('error', 'Unknown error')}")
    
    # Get question for scoring
    question = db.query(Question).filter(Question.id == question_id).first()
    if not question:
        raise HTTPException(status_code=404, detail="Question not found")
    
    # Score writing response
    ai_scores = await scoring_service.score_writing_response(
        writing_result["text"],
        question.content,
        "B1"  # Default CEFR level for scoring
    )
    
    # Save response
    response = Response(
        assessment_id=assessment_id,
        question_id=question_id,
        response_text=writing_result["text"],
        response_audio=file_path,
        is_correct=True,  # Writing responses are not simply correct/incorrect
        response_time=0.0,
        confidence=ai_scores.get("overall_score", 0) / 5.0
    )
    db.add(response)
    db.commit()
    
    return {
        "text": writing_result["text"],
        "ai_scores": ai_scores,
        "response_id": response.id
    }

async def complete_assessment(
    assessment_id: int,
    current_user: User,
    db: Session
) -> AssessmentResult:
    """Complete assessment and calculate final scores"""
    
    # Get assessment
    assessment = db.query(Assessment).filter(
        Assessment.id == assessment_id,
        Assessment.user_id == current_user.id
    ).first()
    
    if not assessment:
        raise HTTPException(status_code=404, detail="Assessment not found")
    
    # Get all responses
    responses = db.query(Response).filter(Response.assessment_id == assessment_id).all()
    response_data = [
        {
            "question_id": r.question_id,
            "is_correct": r.is_correct,
            "response_time": r.response_time,
            "ai_scores": {}  # Will be populated from AI scoring
        }
        for r in responses
    ]
    
    # Calculate final scores
    final_scores = adaptive_engine.calculate_final_scores(response_data)
    
    # Calculate sub-scores
    sub_scores = scoring_service.calculate_sub_scores(response_data, assessment.assessment_type)
    
    # Update assessment
    assessment.status = "completed"
    assessment.completed_at = datetime.utcnow()
    assessment.cefr_level = final_scores["cefr_level"]
    assessment.raw_score = sum(r.is_correct for r in responses) / len(responses) if responses else 0
    assessment.theta_score = final_scores["theta"]
    assessment.standard_error = final_scores["standard_error"]
    assessment.ket_readiness = final_scores["ket_readiness"]
    assessment.pet_readiness = final_scores["pet_readiness"]
    assessment.fce_readiness = final_scores["fce_readiness"]
    
    db.commit()
    
    # Generate feedback and recommendations
    feedback = (
        f"Your CEFR level is {final_scores['cefr_level']}. "
        f"Estimated Lexile: {final_scores['lexile_estimate']}L "
        f"(CI {final_scores['lexile_ci_low']}–{final_scores['lexile_ci_high']}L)."
    )
    recommendations = [
        f"KET readiness: {final_scores['ket_readiness']:.1%}",
        f"PET readiness: {final_scores['pet_readiness']:.1%}",
        f"FCE readiness: {final_scores['fce_readiness']:.1%}",
        f"Recommended reading range: {final_scores['recommended_range_low']}–{final_scores['recommended_range_high']}L"
    ]
    
    assessment_result = AssessmentResult(
        assessment_id=assessment_id,
        cefr_level=final_scores["cefr_level"],
        raw_score=assessment.raw_score,
        theta_score=final_scores["theta"],
        standard_error=final_scores["standard_error"],
        ket_readiness=final_scores["ket_readiness"],
        pet_readiness=final_scores["pet_readiness"],
        fce_readiness=final_scores["fce_readiness"],
        sub_scores=sub_scores,
        feedback=feedback,
        recommendations=recommendations,
        lexile_estimate=final_scores.get("lexile_estimate"),
        lexile_ci_low=final_scores.get("lexile_ci_low"),
        lexile_ci_high=final_scores.get("lexile_ci_high"),
        recommended_range_low=final_scores.get("recommended_range_low"),
        recommended_range_high=final_scores.get("recommended_range_high"),
    )

    return assessment_result.model_dump()

@router.get("/{assessment_id}/result")
async def get_assessment_result(
    assessment_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get assessment result"""
    
    assessment = db.query(Assessment).filter(
        Assessment.id == assessment_id,
        Assessment.user_id == current_user.id
    ).first()
    
    if not assessment:
        raise HTTPException(status_code=404, detail="Assessment not found")
    
    if assessment.status != "completed":
        raise HTTPException(status_code=400, detail="Assessment not completed")
    
    # Get sub-scores
    sub_scores = db.query(SubScore).filter(SubScore.assessment_id == assessment_id).all()
    # Reconstruct response history to compute lexile estimate and CI for the report
    responses = db.query(Response).filter(Response.assessment_id == assessment_id).order_by(Response.created_at).all()
    response_data = [
        {
            "question_id": r.question_id,
            "is_correct": r.is_correct,
            "response_time": r.response_time,
            "question_difficulty": r.question.difficulty_logit if r.question else None,
            "question_lexile": r.question.lexile_level if r.question else None,
        }
        for r in responses
    ]
    final_scores = adaptive_engine.calculate_final_scores(response_data) if responses else {
        "lexile_estimate": None,
        "lexile_ci_low": None,
        "lexile_ci_high": None,
        "recommended_range_low": None,
        "recommended_range_high": None,
    }
    sub_score_data = [
        {
            "skill": s.skill,
            "score": s.score,
            "max_score": s.max_score,
            "cefr_level": s.cefr_level,
            "feedback": s.feedback
        }
        for s in sub_scores
    ]
    
    return {
        "assessment_id": assessment_id,
        "cefr_level": assessment.cefr_level,
        "raw_score": assessment.raw_score,
        "theta_score": assessment.theta_score,
        "standard_error": assessment.standard_error,
        "ket_readiness": assessment.ket_readiness,
        "pet_readiness": assessment.pet_readiness,
        "fce_readiness": assessment.fce_readiness,
        "sub_scores": sub_score_data,
        "completed_at": assessment.completed_at,
        "lexile_estimate": final_scores.get("lexile_estimate"),
        "lexile_ci_low": final_scores.get("lexile_ci_low"),
        "lexile_ci_high": final_scores.get("lexile_ci_high"),
        "recommended_range_low": final_scores.get("recommended_range_low"),
        "recommended_range_high": final_scores.get("recommended_range_high"),
    }

@router.get("/user/{user_id}/assessments")
async def get_user_assessments(
    user_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get all assessments for a user"""
    
    if current_user.id != user_id:
        raise HTTPException(status_code=403, detail="Not authorized")
    
    assessments = db.query(Assessment).filter(Assessment.user_id == user_id).all()
    
    result_list = []
    for a in assessments:
        stored_lex = getattr(a, 'lexile_estimate', None)
        computed_lex = None
        try:
            if stored_lex is None and a.theta_score is not None:
                computed_lex = int(round(800 + (a.theta_score * 250)))
        except Exception:
            computed_lex = None
        result_list.append({
            "id": a.id,
            "assessment_type": a.assessment_type,
            "status": a.status,
            "cefr_level": a.cefr_level,
            "lexile_estimate": stored_lex if stored_lex is not None else computed_lex,
            "theta_score": a.theta_score,
            "started_at": a.started_at,
            "completed_at": a.completed_at
        })
    return result_list
