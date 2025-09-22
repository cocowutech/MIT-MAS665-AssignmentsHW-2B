import speech_recognition as sr
import pytesseract
from PIL import Image
import io
import tempfile
import os
from typing import Dict, Any, Optional, List
import numpy as np
from services.ai_service import AIService

class ScoringService:
    def __init__(self):
        self.ai_service = AIService()
        self.speech_recognizer = sr.Recognizer()
        
    async def process_audio_response(self, audio_file_path: str) -> Dict[str, Any]:
        """Convert audio to text and extract fluency metrics"""
        try:
            # Convert audio to text
            with sr.AudioFile(audio_file_path) as source:
                audio = self.speech_recognizer.record(source)
                transcript = self.speech_recognizer.recognize_google(audio)
            
            # Calculate fluency metrics
            fluency_metrics = self._calculate_fluency_metrics(audio_file_path, transcript)
            
            return {
                "transcript": transcript,
                "fluency_metrics": fluency_metrics,
                "success": True
            }
        except Exception as e:
            return {
                "transcript": "",
                "fluency_metrics": {},
                "success": False,
                "error": str(e)
            }
    
    def _calculate_fluency_metrics(self, audio_file_path: str, transcript: str) -> Dict[str, float]:
        """Calculate fluency metrics from audio and transcript"""
        # This is a simplified version - in production, you'd use more sophisticated audio analysis
        
        # Basic metrics
        word_count = len(transcript.split())
        
        # Estimate speaking rate (words per minute)
        # In production, you'd calculate actual duration from audio file
        estimated_duration = 60  # seconds - placeholder
        words_per_minute = (word_count / estimated_duration) * 60 if estimated_duration > 0 else 0
        
        # Calculate pause ratio (simplified)
        # In production, you'd analyze actual audio for pauses
        pause_ratio = 0.1  # placeholder
        
        # Calculate repetition ratio
        words = transcript.lower().split()
        unique_words = set(words)
        repetition_ratio = 1 - (len(unique_words) / len(words)) if words else 0
        
        return {
            "words_per_minute": words_per_minute,
            "pause_ratio": pause_ratio,
            "repetition_ratio": repetition_ratio,
            "word_count": word_count,
            "unique_word_count": len(unique_words)
        }
    
    async def process_writing_response(self, image_file_path: Optional[str] = None, text: Optional[str] = None) -> Dict[str, Any]:
        """Process writing response with OCR if needed"""
        if image_file_path and not text:
            # Perform OCR on image
            try:
                image = Image.open(image_file_path)
                text = pytesseract.image_to_string(image)
            except Exception as e:
                return {
                    "text": "",
                    "success": False,
                    "error": f"OCR failed: {str(e)}"
                }
        
        if not text:
            return {
                "text": "",
                "success": False,
                "error": "No text provided"
            }
        
        return {
            "text": text,
            "success": True
        }
    
    async def score_reading_response(self, question_id: int, response: str, correct_answer: str) -> Dict[str, Any]:
        """Score reading comprehension response"""
        is_correct = response.strip().lower() == correct_answer.strip().lower()
        
        return {
            "is_correct": is_correct,
            "score": 1.0 if is_correct else 0.0,
            "feedback": "Correct!" if is_correct else f"Correct answer: {correct_answer}"
        }
    
    async def score_speaking_response(self, transcript: str, prompt: str, cefr_level: str) -> Dict[str, Any]:
        """Score speaking response using AI"""
        return await self.ai_service.score_speaking(transcript, prompt, cefr_level)
    
    async def score_writing_response(self, text: str, prompt: str, cefr_level: str) -> Dict[str, Any]:
        """Score writing response using AI"""
        return await self.ai_service.score_writing(text, prompt, cefr_level)
    
    def calculate_sub_scores(self, responses: List[Dict], assessment_type: str) -> List[Dict[str, Any]]:
        """Calculate sub-scores for different skills"""
        sub_scores = []
        
        if assessment_type == "reading":
            # Reading sub-skills
            skills = {
                "comprehension": "Global comprehension",
                "inference": "Inference and deduction", 
                "detail": "Detail extraction",
                "vocabulary": "Vocabulary in context"
            }
            
            for skill, description in skills.items():
                # Filter responses by skill (in practice, questions would be tagged with skills)
                skill_responses = [r for r in responses if r.get('skill') == skill]
                
                if skill_responses:
                    score = sum(r.get('score', 0) for r in skill_responses) / len(skill_responses)
                    sub_scores.append({
                        "skill": skill,
                        "description": description,
                        "score": score,
                        "max_score": 1.0,
                        "cefr_level": self._score_to_cefr(score)
                    })
        
        elif assessment_type == "speaking":
            # Speaking sub-skills
            if responses:
                # Average scores across all speaking responses
                avg_scores = {}
                for response in responses:
                    scores = response.get('ai_scores', {})
                    for skill, score in scores.items():
                        if skill != 'overall_score':
                            avg_scores[skill] = avg_scores.get(skill, 0) + score
                
                for skill, total in avg_scores.items():
                    avg_score = total / len(responses)
                    sub_scores.append({
                        "skill": skill,
                        "description": self._get_skill_description(skill),
                        "score": avg_score,
                        "max_score": 5.0,
                        "cefr_level": self._score_to_cefr(avg_score / 5.0)
                    })
        
        elif assessment_type == "writing":
            # Writing sub-skills
            if responses:
                avg_scores = {}
                for response in responses:
                    scores = response.get('ai_scores', {})
                    for skill, score in scores.items():
                        if skill != 'overall_score':
                            avg_scores[skill] = avg_scores.get(skill, 0) + score
                
                for skill, total in avg_scores.items():
                    avg_score = total / len(responses)
                    sub_scores.append({
                        "skill": skill,
                        "description": self._get_skill_description(skill),
                        "score": avg_score,
                        "max_score": 5.0,
                        "cefr_level": self._score_to_cefr(avg_score / 5.0)
                    })
        
        return sub_scores
    
    def _score_to_cefr(self, score: float) -> str:
        """Convert normalized score (0-1) to CEFR level"""
        if score < 0.2:
            return "A1"
        elif score < 0.4:
            return "A2"
        elif score < 0.6:
            return "B1"
        elif score < 0.8:
            return "B2"
        else:
            return "C1"
    
    def _get_skill_description(self, skill: str) -> str:
        """Get human-readable description for skill"""
        descriptions = {
            "task_achievement": "Task Achievement",
            "grammatical_accuracy": "Grammatical Accuracy",
            "lexical_range": "Lexical Range",
            "fluency": "Fluency",
            "coherence": "Coherence",
            "task_response": "Task Response",
            "coherence_cohesion": "Coherence and Cohesion",
            "lexical_resource": "Lexical Resource",
            "grammatical_range_accuracy": "Grammatical Range and Accuracy"
        }
        return descriptions.get(skill, skill.replace('_', ' ').title())
