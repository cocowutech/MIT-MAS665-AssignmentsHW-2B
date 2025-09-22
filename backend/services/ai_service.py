import google.generativeai as genai
import os
from typing import Dict, List, Any, Optional
import json
import re
from dotenv import load_dotenv

load_dotenv()

class AIService:
    def __init__(self):
        # Configure Gemini API
        genai.configure(api_key=os.getenv("GEMINI_API_KEY", "AIzaSyB-lHK4NaICbNCTojJPQ3wfPXLjKIEtYyo"))
        self.model = genai.GenerativeModel('gemini-pro')
        
    async def generate_reading_questions(self, passage: str, cefr_level: str, num_questions: int = 5) -> List[Dict]:
        """Generate reading comprehension questions from a passage"""
        prompt = f"""
        Generate {num_questions} reading comprehension questions for this passage at CEFR level {cefr_level}.
        
        Passage: {passage}
        
        Create questions that test:
        1. Global comprehension
        2. Inference
        3. Detail extraction
        4. Vocabulary in context
        
        Return as JSON array with this structure:
        [
            {{
                "question": "Question text",
                "type": "multiple_choice",
                "options": ["A", "B", "C", "D"],
                "correct_answer": "A",
                "explanation": "Why this answer is correct",
                "difficulty": 0.5,
                "skill": "comprehension"
            }}
        ]
        """
        
        try:
            response = self.model.generate_content(prompt)
            # Extract JSON from response
            json_match = re.search(r'\[.*\]', response.text, re.DOTALL)
            if json_match:
                return json.loads(json_match.group())
            return []
        except Exception as e:
            print(f"Error generating questions: {e}")
            return []
    
    async def score_speaking(self, transcript: str, prompt: str, cefr_level: str) -> Dict[str, Any]:
        """Score speaking response using AI"""
        scoring_prompt = f"""
        Score this speaking response on a CEFR {cefr_level} rubric:
        
        Prompt: {prompt}
        Response: {transcript}
        
        Score on these criteria (0-5 scale):
        1. Task Achievement: Did they address the prompt?
        2. Grammatical Accuracy: Correct grammar usage
        3. Lexical Range: Vocabulary variety and appropriateness
        4. Fluency: Smoothness and pace
        5. Coherence: Logical organization and discourse markers
        
        Return as JSON:
        {{
            "task_achievement": 4.0,
            "grammatical_accuracy": 3.5,
            "lexical_range": 4.2,
            "fluency": 3.8,
            "coherence": 4.1,
            "overall_score": 4.0,
            "cefr_level": "B1",
            "feedback": "Detailed feedback here",
            "strengths": ["strength1", "strength2"],
            "areas_for_improvement": ["area1", "area2"]
        }}
        """
        
        try:
            response = self.model.generate_content(scoring_prompt)
            json_match = re.search(r'\{.*\}', response.text, re.DOTALL)
            if json_match:
                return json.loads(json_match.group())
            return {}
        except Exception as e:
            print(f"Error scoring speaking: {e}")
            return {}
    
    async def score_writing(self, text: str, prompt: str, cefr_level: str) -> Dict[str, Any]:
        """Score writing response using AI"""
        scoring_prompt = f"""
        Score this writing response on a CEFR {cefr_level} rubric:
        
        Prompt: {prompt}
        Response: {text}
        
        Score on these criteria (0-5 scale):
        1. Task Response: Did they address all parts of the prompt?
        2. Coherence and Cohesion: Logical organization and linking
        3. Lexical Resource: Vocabulary range and accuracy
        4. Grammatical Range and Accuracy: Grammar variety and correctness
        
        Return as JSON:
        {{
            "task_response": 4.0,
            "coherence_cohesion": 3.5,
            "lexical_resource": 4.2,
            "grammatical_range_accuracy": 3.8,
            "overall_score": 4.0,
            "cefr_level": "B1",
            "feedback": "Detailed feedback here",
            "strengths": ["strength1", "strength2"],
            "areas_for_improvement": ["area1", "area2"],
            "annotated_text": "Text with inline comments"
        }}
        """
        
        try:
            response = self.model.generate_content(scoring_prompt)
            json_match = re.search(r'\{.*\}', response.text, re.DOTALL)
            if json_match:
                return json.loads(json_match.group())
            return {}
        except Exception as e:
            print(f"Error scoring writing: {e}")
            return {}
    
    async def generate_content_variants(self, original_content: str, cefr_level: str, num_variants: int = 3) -> List[str]:
        """Generate content variants at different difficulty levels"""
        prompt = f"""
        Create {num_variants} variants of this content for CEFR level {cefr_level}:
        
        Original: {original_content}
        
        Make variants that:
        1. Adjust vocabulary complexity
        2. Modify sentence structure
        3. Change topic focus while maintaining core content
        4. Ensure CEFR level appropriateness
        
        Return as JSON array of strings.
        """
        
        try:
            response = self.model.generate_content(prompt)
            json_match = re.search(r'\[.*\]', response.text, re.DOTALL)
            if json_match:
                return json.loads(json_match.group())
            return []
        except Exception as e:
            print(f"Error generating variants: {e}")
            return []
    
    async def analyze_text_complexity(self, text: str) -> Dict[str, Any]:
        """Analyze text complexity for CEFR level assignment"""
        prompt = f"""
        Analyze this text and determine its CEFR level and complexity metrics:
        
        Text: {text}
        
        Return as JSON:
        {{
            "cefr_level": "B1",
            "lexical_complexity": 0.7,
            "syntactic_complexity": 0.6,
            "average_sentence_length": 15.2,
            "unique_word_ratio": 0.4,
            "difficulty_score": 0.65,
            "key_vocabulary": ["word1", "word2", "word3"],
            "grammar_structures": ["present_perfect", "conditionals"]
        }}
        """
        
        try:
            response = self.model.generate_content(prompt)
            json_match = re.search(r'\{.*\}', response.text, re.DOTALL)
            if json_match:
                return json.loads(json_match.group())
            return {}
        except Exception as e:
            print(f"Error analyzing complexity: {e}")
            return {}
