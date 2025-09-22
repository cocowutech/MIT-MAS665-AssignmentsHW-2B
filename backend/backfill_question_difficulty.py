import sys
from typing import Optional

sys.path.append('backend')

from database import SessionLocal  # type: ignore
from models import Question  # type: ignore


def cefr_from_lexile(lex: int) -> str:
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


def estimate_lexile_from_logit(difficulty_logit: float) -> int:
    # Inverse of seeder mapping: difficulty_logit ≈ (lexile - 800) / 250
    est = 800 + 250.0 * difficulty_logit
    # clamp to reasonable range
    est = max(250, min(1250, int(round(est))))
    return est


def estimate_logit_from_lexile(lexile: int) -> float:
    return (lexile - 800) / 250.0


def main():
    s = SessionLocal()
    try:
        qs = s.query(Question).filter(Question.assessment_category == 'reading').all()
        updated = 0
        for q in qs:
            changed = False

            # Ensure passage exists (fallback to empty string if None)
            if q.passage is None:
                q.passage = ""
                changed = True

            # Backfill lexile_level from difficulty_logit
            if q.lexile_level is None and q.difficulty_logit is not None:
                q.lexile_level = estimate_lexile_from_logit(q.difficulty_logit)
                changed = True

            # If difficulty_logit is missing but lexile exists, derive it
            if q.difficulty_logit is None and q.lexile_level is not None:
                q.difficulty_logit = estimate_logit_from_lexile(q.lexile_level)
                q.b_parameter = q.difficulty_logit
                changed = True

            # Backfill CEFR from lexile_level
            if q.cefr_level is None and q.lexile_level is not None:
                q.cefr_level = cefr_from_lexile(q.lexile_level)
                changed = True

            if changed:
                updated += 1

        if updated:
            s.commit()
        print(f"Backfill complete. Updated {updated} questions.")
    finally:
        s.close()


if __name__ == "__main__":
    main()


