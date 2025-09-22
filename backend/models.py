from sqlalchemy import Column, Integer, String, Float, DateTime, Text, Boolean, ForeignKey, JSON
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from database import Base
from enum import Enum

class CEFRLevel(str, Enum):
    A1 = "A1"
    A2 = "A2"
    B1 = "B1"
    B2 = "B2"
    C1 = "C1"
    C2 = "C2"

class AssessmentType(str, Enum):
    READING = "reading"
    SPEAKING = "speaking"
    WRITING = "writing"
    LISTENING = "listening"

class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True)
    name = Column(String)
    age = Column(Integer)
    hashed_password = Column(String)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    assessments = relationship("Assessment", back_populates="user")

class Assessment(Base):
    __tablename__ = "assessments"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    assessment_type = Column(String)
    status = Column(String, default="in_progress")  # in_progress, completed, abandoned
    current_question = Column(Integer, default=0)
    total_questions = Column(Integer, default=15)
    started_at = Column(DateTime(timezone=True), server_default=func.now())
    completed_at = Column(DateTime(timezone=True))
    
    # Results
    cefr_level = Column(String)
    raw_score = Column(Float)
    theta_score = Column(Float)
    standard_error = Column(Float)
    ket_readiness = Column(Float)
    pet_readiness = Column(Float)
    fce_readiness = Column(Float)
    
    # Relationships
    user = relationship("User", back_populates="assessments")
    responses = relationship("Response", back_populates="assessment")
    sub_scores = relationship("SubScore", back_populates="assessment")

class Question(Base):
    __tablename__ = "questions"

    id = Column(Integer, primary_key=True, index=True)
    question_type = Column(String)  # multiple_choice, true_false, fill_blank, etc.
    assessment_category = Column(String, default="reading")
    content = Column(Text)
    passage = Column(Text)
    options = Column(JSON)  # For multiple choice questions
    correct_answer = Column(String)
    explanation = Column(Text)
    
    # Difficulty and categorization
    difficulty_logit = Column(Float)
    discrimination = Column(Float)
    cefr_level = Column(String)
    lexile_level = Column(Integer)
    topic_tags = Column(JSON)
    exam_tags = Column(JSON)  # KET, PET, FCE
    
    # IRT parameters
    a_parameter = Column(Float)  # discrimination
    b_parameter = Column(Float)  # difficulty
    c_parameter = Column(Float, default=0.0)  # guessing
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())

class Response(Base):
    __tablename__ = "responses"
    
    id = Column(Integer, primary_key=True, index=True)
    assessment_id = Column(Integer, ForeignKey("assessments.id"))
    question_id = Column(Integer, ForeignKey("questions.id"))
    response_text = Column(Text)
    response_audio = Column(String)  # File path for audio responses
    is_correct = Column(Boolean)
    response_time = Column(Float)  # Time in seconds
    confidence = Column(Float)  # User confidence rating
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    assessment = relationship("Assessment", back_populates="responses")
    question = relationship("Question")

class SubScore(Base):
    __tablename__ = "sub_scores"
    
    id = Column(Integer, primary_key=True, index=True)
    assessment_id = Column(Integer, ForeignKey("assessments.id"))
    skill = Column(String)  # reading_comprehension, vocabulary, grammar, etc.
    score = Column(Float)
    max_score = Column(Float)
    cefr_level = Column(String)
    feedback = Column(Text)
    
    # Relationships
    assessment = relationship("Assessment", back_populates="sub_scores")

class ContentItem(Base):
    __tablename__ = "content_items"
    
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String)
    content_type = Column(String)  # passage, prompt, audio, image
    content = Column(Text)
    file_path = Column(String)
    cefr_level = Column(String)
    topic_tags = Column(JSON)
    exam_tags = Column(JSON)
    metadata_json = Column(JSON)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

class Rubric(Base):
    __tablename__ = "rubrics"
    
    id = Column(Integer, primary_key=True, index=True)
    skill = Column(String)
    cefr_level = Column(String)
    criteria = Column(JSON)  # Detailed criteria and descriptors
    exemplars = Column(JSON)  # Sample responses for each level
    created_at = Column(DateTime(timezone=True), server_default=func.now())
