import json
import csv
from pathlib import Path


def q(id_suffix, cefr, lexile, topic, passage, question, options, answer_key, rationale):
    return {
        "id": f"{cefr}-{id_suffix}",
        "cefr_level": cefr,
        "lexile_level": lexile,
        "topic": topic,
        "passage": passage.strip(),
        "question_type": "MCQ",
        "question": question.strip(),
        "options": options,
        "answer_key": answer_key,
        "rationale": rationale.strip(),
        "word_count": len(passage.split()),
    }


bank = []

# -------- A2 (~200–500L) --------
bank += [
    q(
        "01",
        "A2",
        350,
        "Daily Routines",
        "Mia wakes up at 7 a.m. She eats toast and drinks tea before taking the bus to work. The bus usually arrives at 7:40.",
        "When does Mia usually leave for work?",
        ["Before 7:00 a.m.", "At 7:40 a.m.", "At 8:00 a.m.", "After lunch"],
        "B",
        "She takes the bus that arrives at 7:40 a.m., implying she leaves then.",
    ),
    q(
        "02",
        "A2",
        380,
        "Shopping",
        "The local store closes at 6 p.m. On Fridays, it stays open one hour longer. Ben plans to go there at 6:30 on Friday.",
        "Will Ben find the store open at 6:30 on Friday?",
        ["No, it closes at 6:00.", "Yes, because Friday hours are longer.", "Only on weekends.", "It depends on holidays."],
        "B",
        "On Fridays the store closes at 7 p.m., so 6:30 is open.",
    ),
    q(
        "03",
        "A2",
        320,
        "Weather",
        "Today is rainy and cold. The teacher says the picnic will be tomorrow when it is sunny and warm.",
        "Why was the picnic moved to tomorrow?",
        ["The teacher forgot.", "It will be sunny tomorrow.", "They need more food.", "The park is closed forever."],
        "B",
        "The text says today is rainy, but tomorrow will be sunny and warm.",
    ),
    q(
        "04",
        "A2",
        420,
        "School Notice",
        "Library books are due on Monday. Late returns cost one dollar per day.",
        "If you return a book two days late, how much do you pay?",
        ["$1", "$2", "$3", "$4"],
        "B",
        "Two days late × $1/day = $2.",
    ),
    q(
        "05",
        "A2",
        400,
        "Transport",
        "The train to City Center leaves every 15 minutes. Anna missed the 9:00 train.",
        "When is the next train after 9:00?",
        ["9:05", "9:10", "9:15", "9:20"],
        "C",
        "Every 15 minutes → next after 9:00 is 9:15.",
    ),
]

# -------- B1 (~500–800L) --------
bank += [
    q(
        "01",
        "B1",
        620,
        "Community Event",
        "The community center is organizing a weekend cleanup. Volunteers can choose either Saturday morning or Sunday afternoon. Tools will be provided, but volunteers should bring gloves and water.",
        "What should volunteers bring themselves?",
        ["Tools and water.", "Only tools.", "Gloves and water.", "Nothing at all."],
        "C",
        "Tools are provided; volunteers bring gloves and water.",
    ),
    q(
        "02",
        "B1",
        700,
        "Museum Visit",
        "Tickets for the city museum are free on the first Wednesday of each month. However, special exhibits still require a paid ticket.",
        "On a free Wednesday, which statement is true?",
        ["All exhibits are free.", "Special exhibits still cost money.", "The museum is closed.", "Only children enter for free."],
        "B",
        "Special exhibits require payment even on free days.",
    ),
    q(
        "03",
        "B1",
        680,
        "Work Email",
        "Please submit your draft by Thursday so I can review it on Friday. If you need more time, let me know by Wednesday.",
        "When is the last day to ask for an extension?",
        ["Monday", "Tuesday", "Wednesday", "Thursday"],
        "C",
        "The email says to ask by Wednesday.",
    ),
    q(
        "04",
        "B1",
        560,
        "Product Review",
        "The blender is powerful but noisy. It crushes ice quickly, yet the lid can be difficult to clean.",
        "Which is a drawback mentioned in the review?",
        ["Weak motor.", "Hard-to-clean lid.", "Slow at crushing ice.", "Too small to use."],
        "B",
        "The review mentions the lid is difficult to clean.",
    ),
    q(
        "05",
        "B1",
        740,
        "Local News",
        "After months of construction, the park reopened with new walking paths and lighting. Some residents praised the changes, while others worried about increased evening traffic.",
        "What mixed reaction did residents have?",
        ["Everyone disliked it.", "Some praised it; others had concerns.", "No one noticed.", "Only tourists commented."],
        "B",
        "Text states both praise and concerns.",
    ),
]

# -------- B2 (~800–1000L) --------
bank += [
    q(
        "01",
        "B2",
        880,
        "Health Article",
        "Although standing desks are often promoted as healthier, evidence suggests their benefits depend on how they are used. Alternating between sitting and standing, combined with short walks, appears most effective for reducing discomfort.",
        "What practice does the article recommend?",
        ["Standing all day.", "Sitting all day.", "Alternating positions with short walks.", "Avoiding any movement at work."],
        "C",
        "Alternating plus short walks is highlighted as most effective.",
    ),
    q(
        "02",
        "B2",
        900,
        "Technology Column",
        "The new update improves battery life by optimizing background processes. However, older devices may experience slower app launches due to compatibility layers introduced to support legacy hardware.",
        "What trade-off is described?",
        ["Better battery but slower launches on older devices.", "Worse battery and slower launches.", "No change at all.", "Faster launches for all devices."],
        "A",
        "Battery improvements vs. slower launches on older devices.",
    ),
    q(
        "03",
        "B2",
        940,
        "Education Report",
        "Students given timely, specific feedback tend to improve faster than those who receive general comments at the end of a unit. The effect is strongest when learners can immediately revise their work.",
        "When is feedback most effective, according to the report?",
        ["At the end of the unit only.", "When it’s specific and immediate.", "When given yearly.", "When it is anonymous."],
        "B",
        "Specific, timely feedback enabling immediate revision works best.",
    ),
    q(
        "04",
        "B2",
        820,
        "Travel Guide",
        "While the coastal route is scenic, it is vulnerable to sudden fog that can reduce visibility. Drivers should plan extra time and check conditions in the morning before departure.",
        "What precaution is recommended?",
        ["Ignore weather reports.", "Drive faster to beat fog.", "Plan extra time and check conditions.", "Avoid coastal routes entirely."],
        "C",
        "Plan extra time and check conditions is stated.",
    ),
    q(
        "05",
        "B2",
        980,
        "Business Brief",
        "Despite rising material costs, the company maintained its margins by adjusting product mix and negotiating long-term supplier contracts. Revenue grew modestly, reflecting steady demand in core markets.",
        "How did the company preserve margins?",
        ["Raised prices only.", "Cut staff heavily.", "Adjusted product mix and supplier contracts.", "Reduced demand."],
        "C",
        "The passage says product mix + long-term contracts.",
    ),
]

# -------- C1 (~1000–1200L) --------
bank += [
    q(
        "01",
        "C1",
        1080,
        "Science Feature",
        "Although correlation does not imply causation, large-scale longitudinal studies can illuminate patterns that suggest possible causal links. Still, researchers must control for confounding variables to avoid misleading conclusions.",
        "What caution does the passage emphasize?",
        ["Correlation proves causation.", "Small samples are always better.", "Confounders must be controlled.", "Longitudinal studies are useless."],
        "C",
        "It highlights controlling confounders to avoid misleading conclusions.",
    ),
    q(
        "02",
        "C1",
        1120,
        "Policy Analysis",
        "Expanding public transit can reduce congestion, yet benefits hinge on integration with housing policy. Without affordable housing near transit, low-income residents may not experience improved access to jobs.",
        "Which condition strengthens transit benefits?",
        ["Ignoring housing policy.", "Affordable housing near transit.", "Raising fares.", "Limiting service hours."],
        "B",
        "Integration with affordable housing near transit strengthens benefits.",
    ),
    q(
        "03",
        "C1",
        1100,
        "Arts Critique",
        "The exhibition juxtaposes minimalist sculpture with immersive installations, inviting viewers to reconsider how negative space shapes perception. The curatorial choice underscores the dialogue between restraint and sensory overload.",
        "What contrast does the curator highlight?",
        ["Chaos vs. order in music.", "Restraint vs. sensory overload.", "Color vs. texture.", "History vs. modernity."],
        "B",
        "The text mentions restraint and sensory overload in dialogue.",
    ),
    q(
        "04",
        "C1",
        1040,
        "Economics Op-Ed",
        "Short-term price controls may temporarily ease consumer pain, but they risk distorting supply signals. A more durable approach combines targeted subsidies with measures that foster competition.",
        "What risk is associated with price controls?",
        ["They always lower costs permanently.", "They distort supply signals.", "They end competition entirely.", "They raise wages automatically."],
        "B",
        "The passage says controls risk distorting supply signals.",
    ),
    q(
        "05",
        "C1",
        1180,
        "History Essay",
        "Interpreting primary sources demands attention to authorship and context; journals, letters, and official records carry different biases. Triangulating among them can mitigate errors while revealing how narratives were constructed.",
        "What method helps reduce errors?",
        ["Relying on one record.", "Ignoring context.", "Triangulating among sources.", "Avoiding primary sources."],
        "C",
        "Triangulation across sources mitigates errors.",
    ),
]

# -------- C2 (≥1200L) --------
bank += [
    q(
        "01",
        "C2",
        1280,
        "Philosophy",
        "If moral realism posits objective moral truths, then its critics often argue that cross-cultural disagreement undermines claims to universality. Yet persistent disagreement may reflect divergent epistemic frameworks rather than the non-existence of truth.",
        "What alternative explanation does the passage offer for moral disagreement?",
        ["There are no moral truths.", "Disagreement proves subjectivism.", "Different epistemic frameworks cause disagreement.", "Everyone shares the same framework."],
        "C",
        "It attributes disagreement to divergent epistemic frameworks.",
    ),
    q(
        "02",
        "C2",
        1320,
        "Literary Theory",
        "By foregrounding intertextuality, the novel invites readers to decode references that destabilize a singular interpretation. Meaning emerges through a network of echoes rather than a linear narrative authority.",
        "How does meaning emerge, according to the passage?",
        ["From a single authority.", "Through intertextual echoes.", "Only via author interviews.", "By ignoring references."],
        "B",
        "Meaning arises via a network of intertextual echoes.",
    ),
    q(
        "03",
        "C2",
        1400,
        "Neuroscience",
        "While neural correlates of consciousness can be mapped, equating correlation with identity risks a category error. Empirical progress requires clarifying whether measurements capture necessary, sufficient, or merely concomitant activity.",
        "What conceptual risk is highlighted?",
        ["Category error in equating correlation with identity.", "Too few experiments are run.", "Ethics are irrelevant.", "All activity is sufficient."],
        "A",
        "It warns against a category error: correlation ≠ identity.",
    ),
    q(
        "04",
        "C2",
        1250,
        "Law & Society",
        "Constitutional doctrines evolve through jurisprudence that balances precedent with contemporary norms. Overreliance on original meaning may neglect societal transformations that render rigid interpretations untenable.",
        "What critique is made of strict originalism?",
        ["It perfectly fits modern norms.", "It may ignore social change.", "It abolishes precedent.", "It mandates new rights."],
        "B",
        "Strict originalism may neglect evolving societal norms.",
    ),
    q(
        "05",
        "C2",
        1350,
        "Climate Policy",
        "Carbon pricing aligns private incentives with social costs, yet distributional effects remain contentious. Without compensatory measures, regressivity could erode public support and undermine long-term policy stability.",
        "Why might carbon pricing face public resistance?",
        ["It has no costs.", "It is always progressive.", "It can be regressive without compensation.", "It guarantees stability."],
        "C",
        "Regressive effects can reduce support if not offset.",
    ),
]


def main():
    out_dir = Path("data")
    out_dir.mkdir(parents=True, exist_ok=True)

    jsonl_path = out_dir / "reading_bank_cefr_a2_c2.jsonl"
    with open(jsonl_path, "w", encoding="utf-8") as f:
        for item in bank:
            f.write(json.dumps(item, ensure_ascii=False) + "\n")

    csv_path = out_dir / "reading_bank_cefr_a2_c2.csv"
    with open(csv_path, "w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=list(bank[0].keys()))
        writer.writeheader()
        writer.writerows(bank)

    print(
        f"Wrote {len(bank)} items to:\n- {jsonl_path}\n- {csv_path}"
    )


if __name__ == "__main__":
    main()
