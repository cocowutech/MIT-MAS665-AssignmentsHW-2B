"""Import the curated reading bank into the questions table.

Removes existing reading-category questions and loads items from
data/reading_bank_cefr_a2_c2.jsonl, mapping each entry to the Question model.
"""

from pathlib import Path
import json
import sys

from sqlalchemy.orm import Session

ROOT = Path(__file__).resolve().parents[1]
BACKEND_ROOT = ROOT / "backend"
for path in (ROOT, BACKEND_ROOT):
    if str(path) not in sys.path:
        sys.path.insert(0, str(path))

from database import SessionLocal
from models import Question


LETTER_TO_INDEX = {"A": 0, "B": 1, "C": 2, "D": 3}


def load_bank(path: Path) -> list[dict]:
    items: list[dict] = []
    with path.open("r", encoding="utf-8") as handle:
        for line in handle:
            line = line.strip()
            if not line:
                continue
            items.append(json.loads(line))
    return items


def import_reading_questions(session: Session, items: list[dict]) -> None:
    session.query(Question).filter(Question.assessment_category == "reading").delete()

    for item in items:
        options = item["options"]
        answer_letter = (item.get("answer_key") or "").strip().upper()
        idx = LETTER_TO_INDEX.get(answer_letter)
        if idx is None or idx >= len(options):
            raise ValueError(f"Invalid answer key '{answer_letter}' for {item['id']}")
        correct_value = options[idx]

        lexile = item["lexile_level"]
        difficulty = (lexile - 800.0) / 250.0

        question = Question(
            question_type="multiple_choice",
            assessment_category="reading",
            content=item["question"],
            passage=item["passage"],
            options=options,
            correct_answer=correct_value,
            explanation=item["rationale"],
            difficulty_logit=difficulty,
            discrimination=1.0,
            cefr_level=item["cefr_level"],
            lexile_level=lexile,
            topic_tags=[item.get("topic")] if item.get("topic") else [],
            exam_tags=[],
            a_parameter=1.0,
            b_parameter=difficulty,
            c_parameter=0.2,
        )
        session.add(question)

    session.commit()


def main() -> None:
    data_path = Path("data/reading_bank_cefr_a2_c2.jsonl")
    if not data_path.exists():
        raise SystemExit(f"Missing data file: {data_path}")

    items = load_bank(data_path)
    with SessionLocal() as session:
        import_reading_questions(session, items)
    print(f"Loaded {len(items)} reading questions into the database.")


if __name__ == "__main__":
    main()
