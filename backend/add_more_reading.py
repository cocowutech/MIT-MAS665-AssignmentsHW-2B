import sys
import random
from datetime import datetime

sys.path.append('backend')

from database import SessionLocal  # type: ignore
from models import Question  # type: ignore


def main():
    session = SessionLocal()
    try:
        existing = session.query(Question).filter(Question.assessment_category == 'reading').all()
        existing_texts = {q.content for q in existing}
        current_count = len(existing)
        target = 20
        to_add = max(0, target - current_count)
        if to_add == 0:
            print(f"Reading questions already at {current_count} (>= {target}). Nothing to add.")
            return

        print(f"Adding {to_add} reading questions (current={current_count}, target={target})")

        # Generate a spread of difficulties and lexiles
        base_passages = [
            (
                500,
                "Many schools encourage students to read daily. Regular reading helps improve vocabulary, comprehension, and critical thinking skills.",
            ),
            (
                650,
                "Cities around the world are building more parks. Green spaces provide shade, reduce noise, and give residents places to relax and exercise.",
            ),
            (
                800,
                "Researchers are studying how sleep affects memory. Evidence suggests that deep sleep helps the brain consolidate new information into long-term memory.",
            ),
            (
                950,
                "Economists debate the effects of globalization. While it can increase economic growth, it may also lead to unequal distribution of benefits across regions.",
            ),
            (
                1100,
                "The development of renewable energy technologies has accelerated. Advances in storage and grid integration are making intermittent sources more reliable.",
            ),
        ]

        mc_templates = [
            (
                "What is one benefit mentioned in the passage?",
                [
                    "It guarantees immediate results",
                    "It supports the main goal described",
                    "It removes the need for planning",
                    "It eliminates all challenges",
                ],
                "It supports the main goal described",
            ),
            (
                "What is the primary purpose discussed?",
                [
                    "To discourage the topic",
                    "To describe an observed trend",
                    "To compare two unrelated ideas",
                    "To present a fictional narrative",
                ],
                "To describe an observed trend",
            ),
            (
                "Which statement best captures the main idea?",
                [
                    "A minor detail dominates the outcome",
                    "The subject has only negative effects",
                    "The subject influences outcomes in multiple ways",
                    "The subject is irrelevant to most people",
                ],
                "The subject influences outcomes in multiple ways",
            ),
        ]

        created = 0
        while created < to_add:
            lexile, passage = random.choice(base_passages)
            q_text, options, correct = random.choice(mc_templates)

            # Adjust difficulty_logit roughly from lexile
            difficulty_logit = (lexile - 800) / 250.0  # centered at ~B2

            content = q_text
            # Ensure uniqueness by slight paraphrase instead of suffixes
            unique_content = content
            if unique_content in existing_texts:
                variants = [
                    content.replace("primary", "main"),
                    content.replace("best captures", "best summarizes"),
                    content.replace("purpose", "goal"),
                ]
                for v in variants:
                    if v not in existing_texts:
                        unique_content = v
                        break
                if unique_content in existing_texts:
                    unique_content = f"{content} - choose the most accurate option"

            question = Question(
                question_type="multiple_choice",
                assessment_category="reading",
                content=unique_content,
                passage=passage,
                options=options,
                correct_answer=correct,
                explanation="",
                difficulty_logit=difficulty_logit,
                discrimination=1.0,
                cefr_level=None,
                lexile_level=lexile,
                topic_tags=None,
                exam_tags=None,
                a_parameter=1.0,
                b_parameter=difficulty_logit,
                c_parameter=0.0,
            )

            session.add(question)
            existing_texts.add(unique_content)
            created += 1

        session.commit()
        print(f"Added {created} reading questions. New total should be {current_count + created}.")
    finally:
        session.close()


if __name__ == "__main__":
    main()


