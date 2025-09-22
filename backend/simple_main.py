from fastapi import FastAPI, HTTPException, Depends, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPBearer
from contextlib import asynccontextmanager
import uvicorn
import os
from dotenv import load_dotenv
import json
from datetime import datetime, timedelta
from typing import List, Optional, Dict, Any
import uuid

load_dotenv()

# Simple in-memory storage for demo
users_db = {}
assessments_db = {}
questions_db = {}
responses_db = {}

# Sample data
sample_questions = [
    {
        "id": 1,
        "content": "What time does Sarah wake up?",
        "passage": "Sarah goes to school every day. She wakes up at seven o'clock in the morning.",
        "options": ["6:00 AM", "7:00 AM", "8:00 AM", "9:00 AM"],
        "correct_answer": "7:00 AM",
        "question_type": "multiple_choice",
        "cefr_level": "A2",
        "difficulty_logit": -0.5
    },
    {
        "id": 2,
        "content": "According to the text, what is one benefit of traveling?",
        "passage": "Traveling has become an essential part of modern life. Many people enjoy exploring new places, experiencing different cultures, and meeting people from around the world.",
        "options": ["It's expensive", "It broadens our horizons", "It's always safe", "It's easy to plan"],
        "correct_answer": "It broadens our horizons",
        "question_type": "multiple_choice",
        "cefr_level": "B1",
        "difficulty_logit": 0.2
    }
]

# Initialize sample data
for q in sample_questions:
    questions_db[q["id"]] = q

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    print("🚀 Backend server starting...")
    yield
    # Shutdown
    print("🛑 Backend server stopping...")

app = FastAPI(
    title="Adaptive English Placement Assessment",
    description="AI-powered adaptive English placement test for KET/PET/FCE preparation",
    version="1.0.0",
    lifespan=lifespan
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Security
security = HTTPBearer()

@app.get("/")
async def root():
    return {"message": "Adaptive English Placement Assessment API", "status": "running"}

@app.get("/health")
async def health_check():
    return {"status": "healthy", "timestamp": datetime.now().isoformat()}

# Authentication endpoints
@app.post("/api/auth/register")
async def register(user_data: dict):
    user_id = str(uuid.uuid4())
    users_db[user_id] = {
        "id": user_id,
        "email": user_data["email"],
        "name": user_data["name"],
        "age": user_data["age"],
        "created_at": datetime.now().isoformat()
    }
    return {"access_token": f"demo_token_{user_id}", "token_type": "bearer"}

@app.post("/api/auth/login")
async def login(credentials: dict):
    # Simple demo login - accept any email/password
    user_id = str(uuid.uuid4())
    users_db[user_id] = {
        "id": user_id,
        "email": credentials["email"],
        "name": "Demo User",
        "age": 14,
        "created_at": datetime.now().isoformat()
    }
    return {"access_token": f"demo_token_{user_id}", "token_type": "bearer"}

@app.get("/api/auth/me")
async def get_current_user():
    return {
        "id": "demo_user",
        "email": "demo@example.com",
        "name": "Demo User",
        "age": 14,
        "is_active": True
    }

# --- Helper functions for reading assessment ---
def get_reading_question(target_lexile: int, question_number: int) -> dict:
    """Generate a reading question at the target Lexile level"""
    # Expanded passages with different Lexile levels and more variety
    passages = {
        200: [
            {
                "text": "Tom is a boy. He likes to play with his dog. The dog is brown and white. Tom and his dog run in the park every day.",
                "question": "What color is Tom's dog?",
                "options": ["Black and white", "Brown and white", "All brown", "All white"],
                "correct_answer": "Brown and white",
                "lexile": 200
            },
            {
                "text": "The sun is bright. It gives us light and warmth. Plants need the sun to grow. Without the sun, we would be cold and dark.",
                "question": "What does the sun give us?",
                "options": ["Cold and dark", "Light and warmth", "Water and food", "Wind and rain"],
                "correct_answer": "Light and warmth",
                "lexile": 200
            },
            {
                "text": "Mary has a red car. She drives to work every morning. The car is small and fast. Mary likes her red car very much.",
                "question": "What color is Mary's car?",
                "options": ["Blue", "Red", "Green", "Yellow"],
                "correct_answer": "Red",
                "lexile": 200
            },
            {
                "text": "The cat sits on the chair. It is sleeping. The chair is brown. The cat is black and white.",
                "question": "Where is the cat?",
                "options": ["On the table", "On the chair", "On the floor", "In the box"],
                "correct_answer": "On the chair",
                "lexile": 200
            }
        ],
        400: [
            {
                "text": "Sarah loves to read books. She goes to the library every week. The library has many books for children. Sarah likes stories about animals and adventures. She has read over fifty books this year.",
                "question": "How many books has Sarah read this year?",
                "options": ["Twenty books", "Fifty books", "One hundred books", "The text doesn't say"],
                "correct_answer": "Fifty books",
                "lexile": 400
            },
            {
                "text": "The ocean is very big and deep. Many fish live in the ocean. Some fish are small and some are very large. The ocean is also home to whales, dolphins, and sharks.",
                "question": "What animals live in the ocean?",
                "options": ["Only fish", "Fish, whales, dolphins, and sharks", "Only whales and dolphins", "Only small fish"],
                "correct_answer": "Fish, whales, dolphins, and sharks",
                "lexile": 400
            },
            {
                "text": "John works at a hospital. He is a doctor. He helps sick people get better. John works long hours but he loves his job. He saves many lives every day.",
                "question": "What does John do for work?",
                "options": ["Teacher", "Doctor", "Engineer", "Lawyer"],
                "correct_answer": "Doctor",
                "lexile": 400
            },
            {
                "text": "The weather is nice today. The sun is shining and the sky is blue. People are walking in the park. Children are playing on the swings and slides.",
                "question": "What are children doing in the park?",
                "options": ["Reading books", "Playing on swings and slides", "Eating lunch", "Sleeping"],
                "correct_answer": "Playing on swings and slides",
                "lexile": 400
            }
        ],
        600: [
            {
                "text": "The Amazon rainforest is home to millions of species of plants and animals. Many of these species are found nowhere else on Earth. The rainforest helps regulate the world's climate by absorbing carbon dioxide and producing oxygen. However, deforestation threatens this vital ecosystem.",
                "question": "What threatens the Amazon rainforest?",
                "options": ["Too many animals", "Deforestation", "Too much rain", "Cold weather"],
                "correct_answer": "Deforestation",
                "lexile": 600
            },
            {
                "text": "Ancient Egypt was one of the world's first great civilizations. The Egyptians built magnificent pyramids as tombs for their pharaohs. They also developed a system of writing called hieroglyphics and made advances in mathematics and medicine.",
                "question": "What did the Egyptians build as tombs?",
                "options": ["Temples", "Pyramids", "Houses", "Gardens"],
                "correct_answer": "Pyramids",
                "lexile": 600
            },
            {
                "text": "The human brain is one of the most complex organs in the body. It controls all our thoughts, movements, and emotions. The brain contains billions of nerve cells that communicate through electrical signals. Scientists are still learning about how the brain works.",
                "question": "What does the brain control?",
                "options": ["Only movements", "Only thoughts", "Thoughts, movements, and emotions", "Only emotions"],
                "correct_answer": "Thoughts, movements, and emotions",
                "lexile": 600
            },
            {
                "text": "Climate change is affecting weather patterns around the world. Rising temperatures are causing ice caps to melt and sea levels to rise. Many countries are working together to reduce greenhouse gas emissions and slow down global warming.",
                "question": "What is causing ice caps to melt?",
                "options": ["Cold weather", "Rising temperatures", "Rain", "Wind"],
                "correct_answer": "Rising temperatures",
                "lexile": 600
            }
        ],
        800: [
            {
                "text": "Photosynthesis is the process by which plants convert light energy into chemical energy. During this process, plants absorb carbon dioxide from the atmosphere and water from the soil, using sunlight to transform these raw materials into glucose and oxygen. This process is essential for life on Earth.",
                "question": "What is essential for life on Earth?",
                "options": ["Only water", "Only sunlight", "The process of photosynthesis", "Only carbon dioxide"],
                "correct_answer": "The process of photosynthesis",
                "lexile": 800
            },
            {
                "text": "The Industrial Revolution began in Britain in the late 18th century and spread throughout the world. It marked a shift from hand production methods to machines, new chemical manufacturing processes, and the use of steam power. This revolution transformed society and led to urbanization.",
                "question": "What did the Industrial Revolution mark a shift from?",
                "options": ["Machines to hand production", "Hand production methods to machines", "Urban to rural life", "Steam to electric power"],
                "correct_answer": "Hand production methods to machines",
                "lexile": 800
            }
        ],
        1000: [
            {
                "text": "The concept of sustainable development emerged from growing concerns about environmental degradation and social inequality. It advocates for meeting present needs without compromising the ability of future generations to meet their own needs, requiring a delicate balance between economic growth, environmental protection, and social equity.",
                "question": "What does sustainable development aim to balance?",
                "options": ["Past and present needs", "Economic growth, environmental protection, and social equity", "Individual and collective interests", "Local and global concerns"],
                "correct_answer": "Economic growth, environmental protection, and social equity",
                "lexile": 1000
            },
            {
                "text": "Quantum mechanics is a fundamental theory in physics that describes the physical properties of nature at the scale of atoms and subatomic particles. It is the foundation of all quantum physics including quantum chemistry, quantum field theory, quantum technology, and quantum information science.",
                "question": "What does quantum mechanics describe?",
                "options": ["Large objects only", "The physical properties of nature at the atomic scale", "Only chemical reactions", "Only technology"],
                "correct_answer": "The physical properties of nature at the atomic scale",
                "lexile": 1000
            }
        ],
        1200: [
            {
                "text": "The philosophical concept of existentialism emphasizes individual existence, freedom, and choice. It holds that human beings define their own meaning in life and try to make rational decisions despite existing in an irrational universe. Key figures include Jean-Paul Sartre, Albert Camus, and Simone de Beauvoir.",
                "question": "What does existentialism emphasize?",
                "options": ["Collective meaning", "Individual existence, freedom, and choice", "Rational universe", "Predetermined fate"],
                "correct_answer": "Individual existence, freedom, and choice",
                "lexile": 1200
            }
        ]
    }
    
    # Find the closest Lexile level
    available_levels = list(passages.keys())
    closest_lexile = min(available_levels, key=lambda x: abs(x - target_lexile))
    
    # Get a passage from that level, cycling through available passages
    level_passages = passages[closest_lexile]
    passage_data = level_passages[question_number % len(level_passages)]
    
    # Add some variety by occasionally switching to adjacent Lexile levels
    if question_number > 3 and question_number % 3 == 0:
        # Every 3rd question, try a different Lexile level for variety
        available_levels = list(passages.keys())
        if len(available_levels) > 1:
            # Pick a different level
            other_levels = [l for l in available_levels if l != closest_lexile]
            if other_levels:
                alternate_lexile = min(other_levels, key=lambda x: abs(x - target_lexile))
                alternate_passages = passages[alternate_lexile]
                passage_data = alternate_passages[question_number % len(alternate_passages)]
                closest_lexile = alternate_lexile
    
    return {
        "id": f"reading_{question_number}_{closest_lexile}",
        "content": passage_data["question"],
        "passage": passage_data["text"],
        "options": passage_data["options"],
        "correct_answer": passage_data["correct_answer"],
        "question_type": "multiple_choice",
        "cefr_level": get_cefr_from_lexile(closest_lexile),
        "difficulty_logit": (passage_data["lexile"] - 600) / 200,
        "lexile": passage_data["lexile"]
    }

def get_cefr_from_lexile(lexile: int) -> str:
    """Convert Lexile score to CEFR level"""
    if lexile < 300:
        return "A1"
    elif lexile < 500:
        return "A2"
    elif lexile < 700:
        return "B1"
    elif lexile < 900:
        return "B2"
    elif lexile < 1100:
        return "C1"
    else:
        return "C2"

def update_lexile_estimate(current_lexile: int, is_correct: bool, question_lexile: int) -> int:
    """Update Lexile estimate based on response"""
    if is_correct:
        # Move up if correct
        return min(current_lexile + 50, 1200)
    else:
        # Move down if incorrect
        return max(current_lexile - 30, 200)

# Assessment endpoints
@app.post("/api/assessment/start")
async def start_assessment(assessment_data: dict):
    assessment_id = str(uuid.uuid4())
    assessment_type = assessment_data["assessment_type"]
    
    # Check if user already has an active assessment
    active_assessment = None
    for aid, assessment in assessments_db.items():
        if (assessment["user_id"] == "demo_user" and 
            assessment["assessment_type"] == assessment_type and 
            assessment["status"] == "in_progress"):
            active_assessment = assessment
            assessment_id = aid
            break
    
    if not active_assessment:
        # Create new assessment
        assessments_db[assessment_id] = {
            "id": assessment_id,
            "user_id": "demo_user",
            "assessment_type": assessment_type,
            "status": "in_progress",
            "current_question": 0,
            "total_questions": 15,
            "started_at": datetime.now().isoformat(),
            "responses": [],
            "current_lexile": 600,  # Starting Lexile for reading
            "confidence_band": 100
        }
    
    # Get first question based on assessment type
    if assessment_type == "reading":
        first_question = get_reading_question(600, 1)  # Start with 600L, question 1
    else:
        first_question = sample_questions[0]
    
    return {
        "assessment_id": assessment_id,
        "question": first_question,
        "progress": {"current": 1, "total": 15}
    }

@app.get("/api/assessment/{assessment_id}/next")
async def get_next_question(assessment_id: str):
    if assessment_id not in assessments_db:
        raise HTTPException(status_code=404, detail="Assessment not found")
    
    assessment = assessments_db[assessment_id]
    current_q = assessment["current_question"]
    
    # Check if assessment is already completed
    if assessment["status"] == "completed":
        return {
            "completed": True,
            "result": {
                "cefr_level": assessment.get("cefr_level", "B1"),
                "raw_score": assessment.get("raw_score", 0.75),
                "theta_score": assessment.get("theta_score", 0.5),
                "standard_error": assessment.get("standard_error", 0.3),
                "ket_readiness": assessment.get("ket_readiness", 0.8),
                "pet_readiness": assessment.get("pet_readiness", 0.6),
                "fce_readiness": assessment.get("fce_readiness", 0.4),
                "lexile_estimate": assessment.get("current_lexile", 600),
                "lexile_range": f"{assessment.get('current_lexile', 600) - 100}L - {assessment.get('current_lexile', 600) + 100}L"
            }
        }
    
    if current_q > assessment["total_questions"]:
        # Assessment completed
        assessment["status"] = "completed"
        assessment["completed_at"] = datetime.now().isoformat()
        
        # Calculate final scores
        if assessment["assessment_type"] == "reading":
            final_lexile = assessment.get("current_lexile", 600)
            assessment["cefr_level"] = get_cefr_from_lexile(final_lexile)
            assessment["raw_score"] = min(final_lexile / 1000, 1.0)
            assessment["theta_score"] = (final_lexile - 400) / 800
            assessment["standard_error"] = 0.3
            assessment["ket_readiness"] = 0.8 if final_lexile >= 500 else 0.6
            assessment["pet_readiness"] = 0.6 if final_lexile >= 700 else 0.4
            assessment["fce_readiness"] = 0.4 if final_lexile >= 900 else 0.2
        else:
            assessment["cefr_level"] = "B1"
            assessment["raw_score"] = 0.75
            assessment["theta_score"] = 0.5
            assessment["standard_error"] = 0.3
            assessment["ket_readiness"] = 0.8
            assessment["pet_readiness"] = 0.6
            assessment["fce_readiness"] = 0.4
        
        return {
            "completed": True,
            "result": {
                "cefr_level": assessment["cefr_level"],
                "raw_score": assessment["raw_score"],
                "theta_score": assessment["theta_score"],
                "standard_error": assessment["standard_error"],
                "ket_readiness": assessment["ket_readiness"],
                "pet_readiness": assessment["pet_readiness"],
                "fce_readiness": assessment["fce_readiness"],
                "lexile_estimate": assessment.get("current_lexile", 600),
                "lexile_range": f"{assessment.get('current_lexile', 600) - 100}L - {assessment.get('current_lexile', 600) + 100}L"
            }
        }
    
    # Get next question based on assessment type
    if assessment["assessment_type"] == "reading":
        current_lexile = assessment.get("current_lexile", 600)
        question = get_reading_question(current_lexile, current_q + 1)
    else:
        question = sample_questions[current_q % len(sample_questions)]
    
    return {
        "question": question,
        "progress": {"current": current_q + 1, "total": assessment["total_questions"]}
    }

@app.post("/api/assessment/{assessment_id}/respond")
async def submit_response(assessment_id: str, response_data: dict):
    if assessment_id not in assessments_db:
        raise HTTPException(status_code=404, detail="Assessment not found")
    
    assessment = assessments_db[assessment_id]
    question_id = response_data["question_id"]
    user_response = response_data.get("response_text", "")
    
    # For reading assessment, check if answer is correct
    is_correct = True  # Default for demo
    if assessment["assessment_type"] == "reading":
        # Get the correct answer for this question
        # For demo, we'll check if the response matches any of the options
        # In a real system, you'd have proper answer validation
        is_correct = len(user_response) > 0  # Simple demo logic - any response is "correct"
    
    # Store response
    response_id = str(uuid.uuid4())
    responses_db[response_id] = {
        "id": response_id,
        "assessment_id": assessment_id,
        "question_id": question_id,
        "response_text": user_response,
        "is_correct": is_correct,
        "response_time": response_data.get("response_time", 0),
        "created_at": datetime.now().isoformat()
    }
    
    # Update assessment progress
    assessment["current_question"] += 1
    assessment["responses"].append(response_id)
    
    # For reading assessment, update Lexile estimate
    if assessment["assessment_type"] == "reading":
        current_lexile = assessment.get("current_lexile", 600)
        question_lexile = 600  # Default for demo
        new_lexile = update_lexile_estimate(current_lexile, is_correct, question_lexile)
        assessment["current_lexile"] = new_lexile
    
    # Check if assessment is complete
    if assessment["current_question"] > assessment["total_questions"]:
        assessment["status"] = "completed"
        assessment["completed_at"] = datetime.now().isoformat()
        
        # Calculate final scores
        if assessment["assessment_type"] == "reading":
            final_lexile = assessment.get("current_lexile", 600)
            assessment["cefr_level"] = get_cefr_from_lexile(final_lexile)
            assessment["raw_score"] = min(final_lexile / 1000, 1.0)
            assessment["theta_score"] = (final_lexile - 400) / 800
            assessment["standard_error"] = 0.3
            assessment["ket_readiness"] = 0.8 if final_lexile >= 500 else 0.6
            assessment["pet_readiness"] = 0.6 if final_lexile >= 700 else 0.4
            assessment["fce_readiness"] = 0.4 if final_lexile >= 900 else 0.2
        else:
            assessment["cefr_level"] = "B1"
            assessment["raw_score"] = 0.75
            assessment["theta_score"] = 0.5
            assessment["standard_error"] = 0.3
            assessment["ket_readiness"] = 0.8
            assessment["pet_readiness"] = 0.6
            assessment["fce_readiness"] = 0.4
        
        return {
            "response_id": response_id,
            "is_correct": is_correct,
            "feedback": "Assessment completed!",
            "next_question_available": False,
            "completed": True,
            "result": {
                "cefr_level": assessment["cefr_level"],
                "raw_score": assessment["raw_score"],
                "theta_score": assessment["theta_score"],
                "standard_error": assessment["standard_error"],
                "ket_readiness": assessment["ket_readiness"],
                "pet_readiness": assessment["pet_readiness"],
                "fce_readiness": assessment["fce_readiness"],
                "lexile_estimate": assessment.get("current_lexile", 600),
                "lexile_range": f"{assessment.get('current_lexile', 600) - 100}L - {assessment.get('current_lexile', 600) + 100}L"
            }
        }
    
    return {
        "response_id": response_id,
        "is_correct": is_correct,
        "feedback": "Good job!" if is_correct else "Keep trying!",
        "next_question_available": True
    }

@app.post("/api/assessment/{assessment_id}/upload-audio")
async def upload_audio_response(assessment_id: str, audio_file: UploadFile = File(...)):
    return {
        "transcript": "This is a demo transcript of the audio recording.",
        "fluency_metrics": {
            "words_per_minute": 120,
            "pause_ratio": 0.1,
            "repetition_ratio": 0.05
        },
        "ai_scores": {
            "task_achievement": 4.0,
            "grammatical_accuracy": 3.5,
            "lexical_range": 4.2,
            "fluency": 3.8,
            "coherence": 4.1,
            "overall_score": 4.0
        },
        "response_id": str(uuid.uuid4())
    }

@app.post("/api/assessment/{assessment_id}/upload-writing")
async def upload_writing_response(assessment_id: str, text: str = None, image_file: UploadFile = File(None)):
    return {
        "text": text or "This is a demo writing response.",
        "ai_scores": {
            "task_response": 4.0,
            "coherence_cohesion": 3.5,
            "lexical_resource": 4.2,
            "grammatical_range_accuracy": 3.8,
            "overall_score": 4.0
        },
        "response_id": str(uuid.uuid4())
    }

@app.get("/api/assessment/{assessment_id}/result")
async def get_assessment_result(assessment_id: str):
    if assessment_id not in assessments_db:
        raise HTTPException(status_code=404, detail="Assessment not found")
    
    assessment = assessments_db[assessment_id]
    
    return {
        "assessment_id": assessment_id,
        "cefr_level": assessment.get("cefr_level", "B1"),
        "raw_score": assessment.get("raw_score", 0.75),
        "theta_score": assessment.get("theta_score", 0.5),
        "standard_error": assessment.get("standard_error", 0.3),
        "ket_readiness": assessment.get("ket_readiness", 0.8),
        "pet_readiness": assessment.get("pet_readiness", 0.6),
        "fce_readiness": assessment.get("fce_readiness", 0.4),
        "sub_scores": [
            {
                "skill": "reading_comprehension",
                "score": 4.0,
                "max_score": 5.0,
                "cefr_level": "B1",
                "feedback": "Good comprehension skills"
            }
        ],
        "completed_at": assessment.get("completed_at", datetime.now().isoformat())
    }

@app.get("/api/assessment/user/{user_id}/assessments")
async def get_user_assessments(user_id: str):
    user_assessments = []
    for assessment_id, assessment in assessments_db.items():
        if assessment["user_id"] == user_id:
            user_assessments.append({
                "id": assessment_id,
                "assessment_type": assessment["assessment_type"],
                "status": assessment["status"],
                "cefr_level": assessment.get("cefr_level", "B1"),
                "started_at": assessment["started_at"],
                "completed_at": assessment.get("completed_at"),
                "current_question": assessment["current_question"],
                "total_questions": assessment["total_questions"],
                "lexile_estimate": assessment.get("current_lexile", 600)
            })
    return user_assessments

if __name__ == "__main__":
    print("🚀 Starting simplified backend server...")
    uvicorn.run(app, host="0.0.0.0", port=8000)
