"""
Demo data seeder for the Adaptive English Placement Assessment System
This script populates the database with sample content and questions for testing.
"""

import os
import sys
from sqlalchemy.orm import Session
from database import SessionLocal, engine
from models import Base, User, Question, ContentItem, Rubric
from passlib.context import CryptContext
import json

# Create tables
Base.metadata.create_all(bind=engine)

# Password hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def get_password_hash(password):
    return pwd_context.hash(password)

def seed_database():
    """Seed the database with demo data"""
    db = SessionLocal()
    
    try:
        print("🌱 Seeding database with demo data...")
        
        # Create demo users
        demo_users = [
            {
                "email": "student1@example.com",
                "name": "Alice Johnson",
                "age": 14,
                "password": "password123"
            },
            {
                "email": "student2@example.com", 
                "name": "Bob Smith",
                "age": 12,
                "password": "password123"
            },
            {
                "email": "admin@example.com",
                "name": "Admin User",
                "age": 25,
                "password": "admin123"
            }
        ]
        
        print("👥 Creating demo users...")
        for user_data in demo_users:
            existing_user = db.query(User).filter(User.email == user_data["email"]).first()
            if not existing_user:
                user = User(
                    email=user_data["email"],
                    name=user_data["name"],
                    age=user_data["age"],
                    hashed_password=get_password_hash(user_data["password"])
                )
                db.add(user)
        
        # Create sample content items
        print("📚 Creating sample content...")
        sample_content = [
            {
                "title": "School Life - A2 Level",
                "content": "Sarah goes to school every day. She wakes up at seven o'clock in the morning. She has breakfast with her family. Then she walks to school with her friends. School starts at eight thirty. Sarah likes her teachers and enjoys learning new things. She has lunch at school with her classmates. After school, she does her homework and plays with her brother.",
                "content_type": "passage",
                "cefr_level": "A2",
                "topic_tags": ["school", "daily_routine", "family"],
                "exam_tags": ["KET"]
            },
            {
                "title": "Travel and Tourism - B1 Level", 
                "content": "Traveling has become an essential part of modern life. Many people enjoy exploring new places, experiencing different cultures, and meeting people from around the world. Whether it's a short weekend trip to a nearby city or an extended vacation to a foreign country, travel offers numerous benefits. It broadens our horizons, helps us understand different perspectives, and creates lasting memories. However, travel also requires careful planning, including booking accommodations, arranging transportation, and considering cultural differences.",
                "content_type": "passage",
                "cefr_level": "B1", 
                "topic_tags": ["travel", "tourism", "culture"],
                "exam_tags": ["PET"]
            },
            {
                "title": "Environmental Issues - B2 Level",
                "content": "Climate change represents one of the most pressing challenges of our time. The scientific consensus is clear: human activities, particularly the burning of fossil fuels, have significantly contributed to global warming. Rising temperatures, melting ice caps, and extreme weather events are just some of the observable consequences. Addressing this crisis requires immediate action from governments, businesses, and individuals alike. Renewable energy sources, sustainable practices, and international cooperation are essential components of any effective solution.",
                "content_type": "passage",
                "cefr_level": "B2",
                "topic_tags": ["environment", "climate", "science"],
                "exam_tags": ["FCE"]
            }
        ]
        
        for content_data in sample_content:
            existing_content = db.query(ContentItem).filter(ContentItem.title == content_data["title"]).first()
            if not existing_content:
                content = ContentItem(**content_data)
                db.add(content)
        
        # Create sample questions
        print("❓ Creating sample questions...")
        sample_questions = [
            # Reading comprehension set – Lexile-style progression
            {
                "question_type": "multiple_choice",
                "assessment_category": "reading",
                "content": "According to the passage, why does Maya enjoy visiting the library?",
                "passage": "Maya visits the library every Saturday morning. She likes to sit by the big windows where the sunlight warms the tables. Her favorite part is the storytelling hour, where she can listen to new adventures and borrow the stories to read again at home.",
                "options": [
                    "Because it is quiet",
                    "Because her friends are there",
                    "Because she enjoys the storytelling hour",
                    "Because she works there"
                ],
                "correct_answer": "Because she enjoys the storytelling hour",
                "explanation": "The passage says Maya's favorite part is the storytelling hour, and she borrows the stories to read again at home.",
                "difficulty_logit": -0.8,
                "discrimination": 1.1,
                "cefr_level": "A2",
                "lexile_level": 450,
                "topic_tags": ["library", "free_time"],
                "exam_tags": ["KET"]
            },
            {
                "question_type": "multiple_choice",
                "assessment_category": "reading",
                "content": "What is one benefit of the travel experience described in the text?",
                "passage": "Traveling has become an essential part of modern life. Many people enjoy exploring new places, experiencing different cultures, and meeting people from around the world. Travel broadens our horizons and helps us understand different perspectives.",
                "options": [
                    "It guarantees a relaxing vacation",
                    "It broadens our horizons",
                    "It is always inexpensive",
                    "It removes the need for planning"
                ],
                "correct_answer": "It broadens our horizons",
                "explanation": "The passage explicitly states that travel broadens our horizons and helps us understand different perspectives.",
                "difficulty_logit": -0.1,
                "discrimination": 1.0,
                "cefr_level": "B1",
                "lexile_level": 650,
                "topic_tags": ["travel", "culture"],
                "exam_tags": ["PET"]
            },
            {
                "question_type": "multiple_choice",
                "assessment_category": "reading",
                "content": "What is the author's main concern about climate change?",
                "passage": "Climate change represents one of the most pressing challenges of our time. Human activities, particularly the burning of fossil fuels, have significantly contributed to global warming. Rising temperatures, melting ice caps, and extreme weather events demonstrate the urgency of coordinated action.",
                "options": [
                    "Weather changes are temporary",
                    "Human influence is minimal",
                    "Coordinated action is urgently needed",
                    "Renewable energy is too expensive"
                ],
                "correct_answer": "Coordinated action is urgently needed",
                "explanation": "The passage emphasizes the urgency of action from governments, businesses, and individuals to address the crisis.",
                "difficulty_logit": 0.6,
                "discrimination": 1.4,
                "cefr_level": "B2",
                "lexile_level": 880,
                "topic_tags": ["climate", "science"],
                "exam_tags": ["FCE"]
            },
            {
                "question_type": "multiple_choice",
                "assessment_category": "reading",
                "content": "What does the author suggest about successful innovators?",
                "passage": "Successful innovators rarely arrive at the right answer on the first attempt. Instead, they rely on rapid experimentation—testing small ideas, analyzing feedback, and refining their approach. This iterative cycle allows them to discover solutions that truly meet people's needs.",
                "options": [
                    "They avoid testing ideas",
                    "They rely on luck",
                    "They use an iterative process",
                    "They wait for perfect conditions"
                ],
                "correct_answer": "They use an iterative process",
                "explanation": "The passage highlights rapid experimentation with feedback and refinement, describing an iterative process.",
                "difficulty_logit": 1.0,
                "discrimination": 1.3,
                "cefr_level": "C1",
                "lexile_level": 1020,
                "topic_tags": ["innovation", "technology"],
                "exam_tags": ["FCE", "CAE"]
            },
            {
                "question_type": "multiple_choice",
                "assessment_category": "reading",
                "content": "Why does the community start a weekend market?",
                "passage": "Residents in Westbridge launched a weekend market after the local supermarket closed. Volunteers set up stalls, arranged deliveries from nearby farms, and organized a rotating schedule of helpers. The market quickly became more than a place to buy food—it turned into a social hub where neighbours shared recipes and supported local musicians.",
                "options": [
                    "To compete with nearby cities",
                    "Because produce was too cheap",
                    "To replace a closed supermarket",
                    "To fund local musicians"
                ],
                "correct_answer": "To replace a closed supermarket",
                "explanation": "The passage says residents launched the market after the supermarket closed, highlighting the need to replace it.",
                "difficulty_logit": 0.3,
                "discrimination": 1.1,
                "cefr_level": "B1",
                "lexile_level": 700,
                "topic_tags": ["community", "markets"],
                "exam_tags": ["PET"]
            },
            {
                "question_type": "multiple_choice",
                "assessment_category": "reading",
                "content": "According to the passage, what challenges did the research crew face?",
                "passage": "The research crew spent six months in the Arctic cataloging the region's wildlife. While the long daylight hours helped them gather extensive footage, unpredictable ice movement frequently forced them to relocate their camp. Their supply flights were also delayed by sudden storms, leaving the team to ration food and share equipment.",
                "options": [
                    "They lacked expertise with cameras",
                    "They could not find wildlife",
                    "Unstable ice and delayed supplies",
                    "They had too many volunteers"
                ],
                "correct_answer": "Unstable ice and delayed supplies",
                "explanation": "The passage describes relocating because of ice movement and rationing supplies due to delayed flights.",
                "difficulty_logit": 0.9,
                "discrimination": 1.2,
                "cefr_level": "B2",
                "lexile_level": 920,
                "topic_tags": ["science", "expedition"],
                "exam_tags": ["FCE"]
            },
            {
                "question_type": "multiple_choice",
                "assessment_category": "reading",
                "content": "What lesson does the author learn from caring for plants?",
                "passage": "When Leila first started caring for houseplants, she expected quick results. After overwatering several succulents, she joined an online forum where members emphasized patience. By monitoring sunlight, measuring water carefully, and accepting slow growth, Leila discovered that progress often happens quietly before it is visible.",
                "options": [
                    "Plants grow fastest with lots of water",
                    "Online forums waste time",
                    "Patience and observation lead to growth",
                    "Succulents are too delicate to keep"
                ],
                "correct_answer": "Patience and observation lead to growth",
                "explanation": "The passage explains that by being patient and observant, Leila learned to care for plants successfully.",
                "difficulty_logit": -0.4,
                "discrimination": 1.0,
                "cefr_level": "A2",
                "lexile_level": 520,
                "topic_tags": ["hobbies", "home"],
                "exam_tags": ["KET"]
            },
            # Speaking prompts
            {
                "question_type": "open_prompt",
                "assessment_category": "speaking",
                "content": "Describe a memorable celebration in your community. What happened, and why was it meaningful to you?",
                "passage": None,
                "options": None,
                "correct_answer": None,
                "explanation": None,
                "difficulty_logit": 0.0,
                "discrimination": 1.0,
                "cefr_level": "B1",
                "lexile_level": None,
                "topic_tags": ["community", "culture"],
                "exam_tags": ["PET"]
            },
            {
                "question_type": "open_prompt",
                "assessment_category": "speaking",
                "content": "You have five minutes to prepare a short talk about how technology changes the way students learn. Give examples and explain whether you think the changes are positive.",
                "passage": None,
                "options": None,
                "correct_answer": None,
                "explanation": None,
                "difficulty_logit": 0.8,
                "discrimination": 1.2,
                "cefr_level": "B2",
                "lexile_level": None,
                "topic_tags": ["technology", "education"],
                "exam_tags": ["FCE"]
            },
            # Writing prompts
            {
                "question_type": "writing_prompt",
                "assessment_category": "writing",
                "content": "Write an email to your teacher describing a project you would like the class to complete together. Explain what the project is, why it interests you, and how classmates can help.",
                "passage": None,
                "options": None,
                "correct_answer": None,
                "explanation": None,
                "difficulty_logit": 0.0,
                "discrimination": 1.0,
                "cefr_level": "B1",
                "lexile_level": None,
                "topic_tags": ["school", "communication"],
                "exam_tags": ["PET"]
            },
            {
                "question_type": "writing_prompt",
                "assessment_category": "writing",
                "content": "Many cities are trying to reduce traffic congestion. Write an essay discussing two strategies that could work in your area and evaluate the advantages and disadvantages of each.",
                "passage": None,
                "options": None,
                "correct_answer": None,
                "explanation": None,
                "difficulty_logit": 0.9,
                "discrimination": 1.2,
                "cefr_level": "B2",
                "lexile_level": None,
                "topic_tags": ["transport", "society"],
                "exam_tags": ["FCE"]
            }
        ]
        
        for question_data in sample_questions:
            existing_question = db.query(Question).filter(Question.content == question_data["content"]).first()
            if not existing_question:
                question = Question(**question_data)
                db.add(question)
        
        # Create sample rubrics
        print("📋 Creating sample rubrics...")
        sample_rubrics = [
            {
                "skill": "speaking_fluency",
                "cefr_level": "B1",
                "criteria": {
                    "5": "Speaks fluently with only occasional hesitation",
                    "4": "Speaks with minor hesitation but maintains flow",
                    "3": "Speaks with some hesitation but generally coherent",
                    "2": "Speaks with frequent hesitation affecting fluency",
                    "1": "Speaks with constant hesitation and difficulty"
                },
                "exemplars": {
                    "5": "I really enjoy traveling because it allows me to experience different cultures and meet new people from around the world.",
                    "3": "I like travel... um... because... it's good to see... different places and... people.",
                    "1": "Travel is... um... good... I think... because... um... places are... nice."
                }
            },
            {
                "skill": "writing_coherence",
                "cefr_level": "B2",
                "criteria": {
                    "5": "Ideas are well-organized with clear logical progression",
                    "4": "Ideas are generally well-organized with minor issues",
                    "3": "Ideas are somewhat organized but some confusion",
                    "2": "Ideas are poorly organized with frequent confusion",
                    "1": "Ideas are very poorly organized and difficult to follow"
                },
                "exemplars": {
                    "5": "Climate change is a serious issue that requires immediate action. First, governments must implement policies to reduce emissions. Second, businesses should adopt sustainable practices. Finally, individuals can make environmentally conscious choices.",
                    "3": "Climate change is bad. We need to do something. Governments should help. People should help too. It's important.",
                    "1": "Climate bad. Help needed. Government help. People help. Important."
                }
            }
        ]
        
        for rubric_data in sample_rubrics:
            existing_rubric = db.query(Rubric).filter(
                Rubric.skill == rubric_data["skill"],
                Rubric.cefr_level == rubric_data["cefr_level"]
            ).first()
            if not existing_rubric:
                rubric = Rubric(**rubric_data)
                db.add(rubric)
        
        # Commit all changes
        db.commit()
        print("✅ Database seeded successfully!")
        print("\n📝 Demo accounts created:")
        print("   Student 1: student1@example.com / password123")
        print("   Student 2: student2@example.com / password123") 
        print("   Admin: admin@example.com / admin123")
        print("\n🎯 You can now start the application and test the assessments!")
        
    except Exception as e:
        print(f"❌ Error seeding database: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    seed_database()
