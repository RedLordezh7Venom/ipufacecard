import csv
import json
import os
from dotenv import load_dotenv
from extract_student_image import extract_student_image_and_name,ProxyScraper
import time

load_dotenv()
# --------- 1️⃣  Groq client ---------------------------------
# Make sure you have installed: pip install groq
# and set your API key either as an env var or hard‑code it here.
try:
    from groq import Groq
except ImportError:
    raise RuntimeError(
        "The Groq Python library is required. Install it with:\n"
        "    pip install groq"
    )

# Prefer environment variable, but you can also hard‑code for quick testing
GROQ_API_KEY = os.getenv("GROQ_API_KEY")
if not GROQ_API_KEY:
    raise RuntimeError(
        "GROQ_API_KEY not found. Set it in your environment, e.g.:\n"
        "    export GROQ_API_KEY='your‑key-here'"
    )

groq_client = Groq(api_key=GROQ_API_KEY)

# --------- 2️⃣  Helper to detect gender ---------------------
def detect_gender_from_name(name: str) -> str | None:
    """
    Uses Groq’s llama‑8.1‑8b to determine the gender of a name.
    Returns one of: 'male', 'female', or None for ambiguous/unknown.
    """
    # A short prompt that is unlikely to trigger hallucinations
    prompt = (
        f"Given the full name '{name}', answer with only one of the words: "
        "'male', 'female', or 'unknown'. Do not add any additional text."
    )

    try:
        response = groq_client.chat.completions.create(
            model="llama-3.1-8b-instant",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.0,          # deterministic answer
            max_tokens=10,             # we expect a short reply
            stop=None,
        )
        # The response comes back as a list of choices; take the first token
        gender_raw = response.choices[0].message.content.strip().lower()

        # Normalise the output
        if gender_raw in {"male", "female"}:
            return gender_raw
        return None

    except Exception as exc:  # pragma: no cover
        # Log the exception if you have a logger; here we just print
        print(f"[WARN] Gender detection failed for '{name}': {exc}")
        return None

#scraper = ProxyScraper(max_workers = 5)
# --------- 3️⃣  Main loop -------------------------------------
with open("enrollments22MSIT.csv", mode="r", newline="", encoding="utf-8") as file:
    reader = csv.reader(file)
    # Skip header if present (uncomment the next line)
    # next(reader, None)

    for row in reader:
        # Assuming CSV layout: enrollment,course,batch,college,branch
        college = row[3]
        course = row[1]
        batch = row[2]
        branch = row[4]
        enrollment = row[0]

        image, name = extract_student_image_and_name(row[0])

        # Detect gender
        gender = detect_gender_from_name(name)

        data = {
            "name": name,
            "image": image,
            "college": college,
            "course": course,
            "batch": batch,
            "branch": branch,
            "enrollment": enrollment,
            "elo": 1200,
            "matches": 0,
            "gender": gender,
        }

        # Append a JSON line per student
        with open("dataMSIT.json", mode="a", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False)
            f.write("\n")

