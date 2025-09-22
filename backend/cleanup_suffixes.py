import re
import sys

sys.path.append('backend')

from database import SessionLocal  # type: ignore
from models import Question  # type: ignore


def strip_suffix(text: str) -> str:
    # Remove trailing ' (n)' at end of content
    return re.sub(r"\s*\(\d+\)\s*$", "", text).strip()


def main():
    s = SessionLocal()
    try:
        qs = s.query(Question).filter(Question.assessment_category == 'reading').all()
        changed = 0
        seen = set()
        for q in qs:
            original = q.content or ""
            cleaned = strip_suffix(original)
            if cleaned != original:
                # avoid duplicates
                if cleaned in seen:
                    continue
                q.content = cleaned
                changed += 1
                seen.add(cleaned)
        if changed:
            s.commit()
        print(f"Updated {changed} questions (removed trailing numeric suffixes).")
    finally:
        s.close()


if __name__ == "__main__":
    main()


