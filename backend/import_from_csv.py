import csv
import json
import os
import re
import sys
from typing import List, Optional

sys.path.append('backend')

from database import SessionLocal  # type: ignore
from models import Question, Rubric  # type: ignore


def find_path(candidates: List[str]) -> Optional[str]:
    for p in candidates:
        if os.path.exists(p):
            return p
    return None


def normalize_criteria(val: str):
    if not val:
        return []
    val = val.strip()
    if not val:
        return []
    try:
        data = json.loads(val)
        if isinstance(data, list):
            return data
        if isinstance(data, dict):
            return [data]
    except Exception:
        pass
    # fallback: split by ';'
    return [s.strip() for s in val.split(';') if s.strip()]


def a_b_c_d_to_text(row):
    options = []
    for key in ['option_a', 'option_b', 'option_c', 'option_d']:
        text = (row.get(key) or '').strip()
        if text:
            options.append(text)
    return options


def parse_options_with_ids(row):
    """Return (options_texts, option_ids).
    Supports options_json as list of strings or list of objects {id, text}.
    Fallback to A–D columns.
    """
    raw = row.get('options_json')
    if raw and raw.strip():
        try:
            data = json.loads(raw)
            if isinstance(data, list):
                texts = []
                ids = []
                for item in data:
                    if isinstance(item, dict):
                        text = str(item.get('text') or item.get('label') or item.get('option') or '').strip()
                        oid = str(item.get('id') or '').strip()
                        if text:
                            texts.append(text)
                            ids.append(oid or None)
                    else:
                        text = str(item).strip()
                        if text:
                            texts.append(text)
                            ids.append(None)
                if texts:
                    return texts, ids
        except Exception:
            pass
    texts = a_b_c_d_to_text(row)
    ids = ['A','B','C','D'][:len(texts)]
    return texts, ids


def answer_key_to_text(answer_key: str, options: List[str], option_ids: Optional[List[Optional[str]]] = None) -> Optional[str]:
    if not options:
        return None
    key = (answer_key or '').strip().upper()
    idx_map = {'A': 0, 'B': 1, 'C': 2, 'D': 3}
    # Prefer matching by provided ids if available
    if option_ids:
        for i, oid in enumerate(option_ids):
            if oid and oid.upper() == key and i < len(options):
                return options[i]
    if key in idx_map and idx_map[key] < len(options):
        return options[idx_map[key]]
    # Try numeric index (1-based)
    if key.isdigit():
        i = int(key) - 1
        if 0 <= i < len(options):
            return options[i]
    # Try exact text match
    for o in options:
        if o.strip().lower() == key.strip().lower():
            return o
    return None


def ensure_float(val, default=None):
    try:
        return float(val)
    except Exception:
        return default


def ensure_int(val, default=None):
    try:
        return int(float(val))
    except Exception:
        return default


def import_reading_items(session, csv_path: str) -> int:
    created = 0
    with open(csv_path, 'r', encoding='utf-8-sig') as f:
        reader = csv.DictReader(f)
        for row in reader:
            passage = (row.get('passage') or '').strip()
            stem_raw = (row.get('stem') or '').strip()
            # Normalize stem by removing trailing numeric suffix like "(6)"
            stem = re.sub(r"\s*\(\d+\)\s*$", "", stem_raw)
            if not passage or not stem:
                continue
            options, option_ids = parse_options_with_ids(row)
            if len(options) < 3:
                continue
            correct = answer_key_to_text(row.get('answer_key', ''), options, option_ids)
            if not correct:
                continue
            # Validate exactly one correct among options
            if sum(1 for o in options if o == correct) != 1:
                continue

            # Compute lexile
            lexile = ensure_int(row.get('difficulty_lexile'))
            if lexile is None:
                lexile = ensure_int(row.get('lexile_band'))

            cefr = (row.get('cefr_level') or '').strip() or None
            diff = ensure_float(row.get('difficulty_logit'))
            if diff is None and lexile is not None:
                diff = (lexile - 800) / 250.0

            # Build metadata/tags
            topic = (row.get('topic') or '').strip() or None
            genre = (row.get('genre') or '').strip() or None
            age_band = (row.get('age_band') or '').strip() or None
            irt_version = (row.get('irt_version') or '').strip() or None
            active_val = (row.get('active') or '').strip()
            active = None
            if active_val:
                if active_val.lower() in ('true','1','yes','y'): active = True
                elif active_val.lower() in ('false','0','no','n'): active = False
            rationale = (row.get('rationale') or '').strip() or None
            evidence_raw = (row.get('evidence_quotes_json') or '').strip()
            try:
                evidence = json.loads(evidence_raw) if evidence_raw else None
            except Exception:
                evidence = None
            distractors_raw = (row.get('distractor_types_json') or '').strip()
            try:
                distractor_types = json.loads(distractors_raw) if distractors_raw else None
            except Exception:
                distractor_types = None

            skill = (row.get('skill') or '').strip() or None
            content_tags = {
                'skill': skill,
                'topic': topic,
                'genre': genre,
                'age_band': age_band,
                'irt_version': irt_version,
                'active': active,
                'rationale': rationale,
                'evidence_quotes': evidence,
                'distractor_types': distractor_types,
                'source': 'csv_bank'
            }

            # Upsert: match by passage and normalized stem (ignoring trailing (n))
            candidates = session.query(Question).filter(
                Question.assessment_category == 'reading',
                Question.passage == passage
            ).all()
            def norm(s: str) -> str:
                return re.sub(r"\s*\(\d+\)\s*$", "", (s or '').strip())
            existing = next((q for q in candidates if norm(q.content) == stem), None)

            if existing:
                existing.options = options
                existing.correct_answer = correct
                existing.difficulty_logit = diff
                existing.cefr_level = cefr
                existing.lexile_level = lexile
                existing.topic_tags = content_tags
                existing.exam_tags = existing.exam_tags or None
                existing.a_parameter = 1.0
                existing.b_parameter = diff if diff is not None else existing.b_parameter
                existing.c_parameter = 0.0
            else:
                q = Question(
                    question_type='multiple_choice',
                    assessment_category='reading',
                    content=stem,
                    passage=passage,
                    options=options,
                    correct_answer=correct,
                    explanation='',
                    difficulty_logit=diff,
                    discrimination=1.0,
                    cefr_level=cefr,
                    lexile_level=lexile,
                    topic_tags=content_tags,
                    exam_tags=None,
                    a_parameter=1.0,
                    b_parameter=diff if diff is not None else 0.0,
                    c_parameter=0.0,
                )
                session.add(q)
                created += 1

    session.commit()
    return created


def import_scoring_rules(session, csv_path: str) -> int:
    created = 0
    with open(csv_path, 'r', encoding='utf-8-sig') as f:
        reader = csv.DictReader(f)
        for row in reader:
            skill = (row.get('skill') or '').strip()
            cefr = (row.get('cefr_level') or '').strip()
            if not skill or not cefr:
                continue
            criteria = normalize_criteria(row.get('criteria') or '')
            exemplars_raw = row.get('exemplars') or ''
            exemplars = []
            if exemplars_raw.strip():
                try:
                    exemplars = json.loads(exemplars_raw)
                except Exception:
                    exemplars = normalize_criteria(exemplars_raw)

            # Upsert based on (skill, cefr_level)
            existing = session.query(Rubric).filter(
                Rubric.skill == skill,
                Rubric.cefr_level == cefr
            ).first()

            if existing:
                existing.criteria = criteria
                existing.exemplars = exemplars
            else:
                r = Rubric(
                    skill=skill,
                    cefr_level=cefr,
                    criteria=criteria,
                    exemplars=exemplars
                )
                session.add(r)
                created += 1

    session.commit()
    return created


def main():
    # Accept files in either canonical or nested path
    items_path = find_path([
        'backend/data/reading_items.csv',
        'backend/data/reading_items_lexile_bank.csv',
        'backend/data/backend/data/reading_items.csv',
        'backend/data/backend/data/reading_items_lexile_bank.csv',
    ])
    rules_path = find_path([
        'backend/data/scoring_rules.csv',
        'backend/data/lexile_scoring_rules.csv',
        'backend/data/backend/data/scoring_rules.csv',
        'backend/data/backend/data/lexile_scoring_rules.csv',
    ])

    if not items_path and not rules_path:
        print('No CSVs found. Expected in backend/data/.')
        return

    s = SessionLocal()
    try:
        if items_path:
            created_q = import_reading_items(s, items_path)
            print(f"Imported/updated reading items. Created: {created_q}")
        if rules_path:
            created_r = import_scoring_rules(s, rules_path)
            print(f"Imported/updated scoring rules. Created: {created_r}")
    finally:
        s.close()


if __name__ == '__main__':
    main()


