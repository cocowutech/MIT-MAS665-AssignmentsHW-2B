import numpy as np
from typing import List, Dict, Any, Optional
from sqlalchemy.orm import Session
from models import Question, Response, Assessment
import math

class AdaptiveEngine:
    def __init__(self):
        self.initial_theta = 0.0  # Start at average difficulty (roughly B1)
        self.theta_step = 0.5     # Step size for difficulty adjustment
        self.min_questions = 12
        self.max_questions = 15
        # SE threshold in theta units; 70L on 250 L/theta scale => 0.28
        self.se_threshold = 0.28   # Standard error threshold for stopping (≈70L)
        
    @staticmethod
    def _sigmoid(z: float) -> float:
        # numerically stable sigmoid clamp
        z = max(min(z, 6.0), -6.0)
        return 1.0 / (1.0 + math.exp(-z))

    def select_next_question(self, db: Session, assessment_id: int, current_responses: List[Dict]) -> Optional[Question]:
        """Select the next question based on current ability estimate"""
        assessment = db.query(Assessment).filter(Assessment.id == assessment_id).first()
        if not assessment:
            return None

        answered_question_ids = [r.get('question_id') for r in current_responses]

        available_query = db.query(Question).filter(
            Question.assessment_category == assessment.assessment_type
        )

        if answered_question_ids:
            available_query = available_query.filter(Question.id.notin_(answered_question_ids))

        # Only consider questions that meet required fields for serving
        all_candidates = available_query.all()
        def is_servable(q: Question) -> bool:
            try:
                has_passage = bool((q.passage or "").strip())
                has_stem = bool((q.content or "").strip())
                opts = q.options or []
                has_options = isinstance(opts, list) and len(opts) >= 3
                has_key = q.correct_answer is not None and str(q.correct_answer).strip() != ""
                # exactly one correct among options if options are strings
                if has_options and has_key and all(isinstance(o, str) for o in opts):
                    correct_count = sum(1 for o in opts if o == q.correct_answer)
                    if correct_count != 1:
                        return False
                has_lexile = q.lexile_level is not None
                return has_passage and has_stem and has_options and has_key and has_lexile
            except Exception:
                return False

        available_questions = [q for q in all_candidates if is_servable(q)]

        if not available_questions:
            return None

        target_difficulty = self._determine_target_difficulty(current_responses, available_questions)

        # Choose closest difficulty; tie-break by maximum information at current theta
        def key_tuple(question: Question):
            difficulty = question.difficulty_logit or 0.0
            # distance primary key (lower is better)
            dist = abs(difficulty - target_difficulty)
            # information at current target
            z = (target_difficulty - 0.0)  # with a=1, b≈0 in our simplified update
            # better: compute at question difficulty by treating b ≈ question.difficulty
            z = (target_difficulty - difficulty)
            p = self._sigmoid(z)
            info = p * (1 - p)  # max 0.25
            # we want max info, so use negative for sorting (min selects highest)
            return (dist, -info)

        return min(available_questions, key=key_tuple)
    
    def should_stop(self, responses: List[Dict], assessment: Assessment) -> bool:
        """Determine if assessment should stop"""
        
        # Always respect the configured total
        if len(responses) >= assessment.total_questions:
            return True

        # Ensure we ask a reasonable minimum before stopping early
        min_required = min(self.min_questions, assessment.total_questions)
        if len(responses) < min_required:
            return False

        # Check standard error threshold
        se = self._calculate_standard_error(responses)
        if se <= self.se_threshold:
            return True
            
        # Check for convergence (theta not changing much)
        if len(responses) >= 8:
            recent_responses = responses[-5:]
            recent_theta = self._calculate_theta(recent_responses)
            all_theta = self._calculate_theta(responses)
            
            if abs(recent_theta - all_theta) < 0.1:
                return True
                
        return False
    
    def _calculate_theta(self, responses: List[Dict]) -> float:
        """Calculate ability estimate using IRT"""
        if not responses:
            return self.initial_theta
            
        # Simple 2-parameter IRT estimation
        # Using Newton-Raphson method for maximum likelihood estimation
        
        theta = self.initial_theta
        tolerance = 0.001
        max_iterations = 50
        
        for _ in range(max_iterations):
            # Calculate first derivative (gradient)
            first_derivative = 0
            second_derivative = 0
            
            for response in responses:
                question_id = response.get('question_id')
                is_correct = response.get('is_correct', False)
                
                # Get question parameters (simplified - in real implementation, 
                # these would come from the database)
                a = 1.0  # discrimination parameter
                # Prefer difficulty_logit; else derive from lexile; default 0.0
                if response.get('question_difficulty') is not None:
                    b = float(response.get('question_difficulty'))
                elif response.get('question_lexile') is not None:
                    b = (float(response.get('question_lexile')) - 800.0) / 250.0
                else:
                    b = 0.0
                c = 0.0  # guessing parameter
                
                # Calculate probability of correct response
                z = a * (theta - b)
                p = c + (1 - c) * self._sigmoid(z)
                
                # Calculate derivatives
                if is_correct:
                    first_derivative += a * (1 - p)
                    second_derivative += -a * a * p * (1 - p)
                else:
                    first_derivative += -a * p
                    second_derivative += a * a * p * (1 - p)
            
            # Update theta
            if second_derivative != 0:
                step = - first_derivative / second_derivative
                # Limit step to avoid explosions on small information
                if step > 0.5:
                    step = 0.5
                elif step < -0.5:
                    step = -0.5
                new_theta = theta + step
                if abs(new_theta - theta) < tolerance:
                    break
                # Clamp to a reasonable ability range
                theta = max(min(new_theta, 3.0), -3.0)
            else:
                break
                
        return theta
    
    def _calculate_standard_error(self, responses: List[Dict]) -> float:
        """Calculate standard error of theta estimate"""
        if len(responses) < 2:
            return 1.0
            
        # Simplified standard error calculation using Fisher information
        theta = self._calculate_theta(responses)
        information = 0.0
        for response in responses:
            a = 1.0
            if response.get('question_difficulty') is not None:
                b = float(response.get('question_difficulty'))
            elif response.get('question_lexile') is not None:
                b = (float(response.get('question_lexile')) - 800.0) / 250.0
            else:
                b = 0.0
            c = 0.0
            z = a * (theta - b)
            p = c + (1 - c) * self._sigmoid(z)
            information += a * a * p * (1 - p)
        if information <= 0:
            se = 1.0
        else:
            se = 1.0 / math.sqrt(information)
        # Clamp SE to avoid absurd CIs
        return max(0.2, min(se, 1.5))
    
    def _estimate_cefr_level(self, theta: float) -> str:
        """Estimate CEFR level from theta score"""
        if theta < -1.0:
            return "A1"
        elif theta < -0.5:
            return "A2"
        elif theta < 0.0:
            return "B1"
        elif theta < 0.5:
            return "B2"
        elif theta < 1.0:
            return "C1"
        else:
            return "C2"
    
    def calculate_final_scores(self, responses: List[Dict]) -> Dict[str, Any]:
        """Calculate final scores with CEFR aligned to accuracy and lexile.

        - Accuracy = proportion correct
        - Avg lexile = average of question_lexile for items answered correctly (fallback to all if none correct)
        - CEFR primarily from avg lexile with guardrails from accuracy
        """
        # Accuracy
        total = max(len(responses), 1)
        correct = sum(1 for r in responses if r.get("is_correct", False))
        accuracy = correct / total

        # Avg lexile
        correct_lexiles = [r.get("question_lexile") for r in responses if r.get("is_correct", False) and r.get("question_lexile") is not None]
        if correct_lexiles:
            avg_lexile = sum(correct_lexiles) / len(correct_lexiles)
        else:
            all_lex = [r.get("question_lexile") for r in responses if r.get("question_lexile") is not None]
            avg_lexile = (sum(all_lex) / len(all_lex)) if all_lex else 600

        # Base CEFR from lexile
        def lexile_to_cefr(lex: float) -> str:
            if lex < 300:
                return "A1"
            if lex < 500:
                return "A2"
            if lex < 700:
                return "B1"
            if lex < 900:
                return "B2"
            if lex < 1100:
                return "C1"
            return "C2"

        base_cefr = lexile_to_cefr(avg_lexile)

        # Apply guardrails based on accuracy
        cefr_order = ["A1", "A2", "B1", "B2", "C1", "C2"]
        idx = cefr_order.index(base_cefr)
        if accuracy < 0.5:
            idx = max(0, idx - 2)
        elif accuracy < 0.6:
            idx = max(0, idx - 1)
        elif accuracy < 0.7:
            idx = max(0, idx)  # no upgrade beyond base
        # if >=0.7 keep base; >=0.85 we could consider +1 but avoid inflation
        final_cefr = cefr_order[idx]

        # Compute theta/se for internal diagnostics only
        theta = self._calculate_theta(responses)
        try:
            se = self._calculate_standard_error(responses)
        except Exception:
            se = 0.4

        # Convert theta to Lexile-style estimate and CI with realistic bounds
        lexile_estimate = int(round(self._theta_to_lexile(theta)))
        # Bound to typical scale
        lexile_estimate = max(300, min(1350, lexile_estimate))
        lexile_se = se * 250.0
        ci_low = max(300, int(round(lexile_estimate - 1.96 * lexile_se)))
        ci_high = min(1350, int(round(lexile_estimate + 1.96 * lexile_se)))
        rec_low = max(300, int(round(lexile_estimate - 100)))
        rec_high = min(1350, int(round(lexile_estimate + 100)))

        # Exam readiness derived from CEFR and accuracy
        def readiness_for(exam: str) -> float:
            base = {
                "KET": {"A1": 0.4, "A2": 0.7, "B1": 0.85, "B2": 0.95, "C1": 0.98, "C2": 1.0},
                "PET": {"A1": 0.2, "A2": 0.5, "B1": 0.75, "B2": 0.9, "C1": 0.95, "C2": 0.98},
                "FCE": {"A1": 0.1, "A2": 0.3, "B1": 0.55, "B2": 0.8, "C1": 0.92, "C2": 0.97},
            }[exam][final_cefr]
            # Blend with accuracy to temper extremes
            return max(0.0, min(1.0, 0.6 * base + 0.4 * accuracy))

        ket_readiness = readiness_for("KET")
        pet_readiness = readiness_for("PET")
        fce_readiness = readiness_for("FCE")

        return {
            "theta": theta,
            "standard_error": se,
            "cefr_level": final_cefr,
            "ket_readiness": ket_readiness,
            "pet_readiness": pet_readiness,
            "fce_readiness": fce_readiness,
            "confidence_band": f"{final_cefr} ± {se:.2f}",
            "accuracy": accuracy,
            "avg_lexile": avg_lexile,
            "lexile_estimate": lexile_estimate,
            "lexile_ci_low": ci_low,
            "lexile_ci_high": ci_high,
            "recommended_range_low": rec_low,
            "recommended_range_high": rec_high,
        }

    def _theta_to_lexile(self, theta: float) -> float:
        """Rudimentary conversion from theta to a Lexile-style scale."""
        # Anchor theta 0 around 800L and scale gradually.
        return 800 + (theta * 250)

    def _determine_target_difficulty(self, responses: List[Dict], available_questions: List[Question]) -> float:
        """Determine the next target difficulty using rolling correctness rule.

        Rule: If recent correctness rate > 0.5, increase difficulty; if < 0.5, decrease.
        Uses last up to 4 responses for stability; falls back to last item if fewer.
        """
        if not responses:
            return self.initial_theta

        window = responses[-4:] if len(responses) >= 4 else responses
        correct_count = sum(1 for r in window if r.get('is_correct', False))
        rate = correct_count / len(window)

        # Derive last known difficulty (default to initial)
        last_known = None
        for r in reversed(responses):
            if 'question_difficulty' in r and r['question_difficulty'] is not None:
                last_known = r['question_difficulty']
                break
        last_difficulty = last_known if last_known is not None else self.initial_theta

        if rate > 0.5:
            target = last_difficulty + self.theta_step
        elif rate < 0.5:
            target = last_difficulty - self.theta_step
        else:
            target = last_difficulty

        difficulties = [q.difficulty_logit or 0.0 for q in available_questions]
        if not difficulties:
            return target

        min_diff = min(difficulties)
        max_diff = max(difficulties)
        return max(min(target, max_diff), min_diff)
    
    def _calculate_exam_readiness(self, theta: float, exam: str) -> float:
        """Calculate readiness for specific exams (0-1 scale)"""
        # Exam-specific theta thresholds
        thresholds = {
            "KET": -0.5,    # A2 level
            "PET": 0.0,     # B1 level  
            "FCE": 0.5      # B2 level
        }
        
        if exam not in thresholds:
            return 0.0
            
        threshold = thresholds[exam]
        
        # Sigmoid function to convert theta to readiness score
        readiness = 1 / (1 + math.exp(-2 * (theta - threshold)))
        return min(max(readiness, 0.0), 1.0)
