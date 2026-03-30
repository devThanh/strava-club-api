import re
from datetime import datetime

def parse_activity(text: str):
    data = {}

    distance = re.search(r"(\d+(\.\d+)?)\s?km", text)
    if distance:
        data["distance"] = float(distance.group(1))

    pace = re.search(r"(\d{1,2}:\d{2})/km", text)
    if pace:
        data["pace"] = pace.group(1)

    duration = re.search(r"(\d{1,2}:\d{2}(:\d{2})?)", text)
    if duration:
        data["duration"] = duration.group(1)

    date = re.search(r"\w+\s\d{1,2},\s\d{4}", text)
    if date:
        data["date"] = datetime.strptime(date.group(), "%b %d, %Y")

    lines = text.split("\n")
    if len(lines) > 1:
        data["name"] = lines[1]

    return data

def extract(text, pattern):
    match = re.search(pattern, text, re.IGNORECASE)
    if not match:
        return None
    return match.group(1) if match.lastindex else match.group(0)


def parse_strava_text(text: str):
    lines = clean_ocr_text(text)

    data = {
        "full_name": None,
        "activity_name": None,
        "distance": None,
        "pace": None,
        "duration": None,
        "activity_date": None,
    }

    for i, line in enumerate(lines):
        lower = line.lower()

        if not data["full_name"] and re.match(r"^[A-Z][a-zA-Z]+\s[A-Z][a-zA-Z]+", line):
            data["full_name"] = line
            continue

        if "run" in lower:
            data["activity_name"] = line
            continue

        if re.search(r"\d+(\.\d+)?\s*km", lower):
            data["distance"] = parse_float(line)
            continue

        if re.search(r"\d{1,2}:\d{2}\s*/\s*km", lower):
            data["pace"] = parse_pace(line)
            continue

        if "time" in lower:
            duration = extract_duration(line)

            if not duration and i + 1 < len(lines):
                duration = extract_duration(lines[i + 1])

            if duration:
                data["duration"] = duration

    return data

def parse_float(value):
    if not value:
        return None

    try:
        match = re.search(r"\d+\.\d+|\d{2,}", str(value))
        return float(match.group()) if match else None
    except:
        return None


def parse_pace(value):
    if not value:
        return None

    match = re.search(r"(\d{1,2}:\d{2})", str(value))
    return match.group(1) if match else None


def parse_duration(value):
    if not value:
        return None

    match = re.search(r"(\d{1,2}:\d{2}:\d{2})", str(value))
    return match.group(1) if match else None


def parse_date(value):
    if not value:
        return None

    try:
        return datetime.strptime(value.strip(), "%d %B %Y")
    except:
        return None
    

def normalize_ocr_data(data):
    return {
        "full_name": data.get("full_name"),
        "activity_name": data.get("activity_name"),
        "distance": parse_float(data.get("distance")),
        "pace": parse_pace(data.get("pace")),
        "duration": parse_duration(data.get("time")),
        "activity_date": parse_date(data.get("activity_date")),
    }

def extract_duration(text: str):
    text = text.lower().replace("lh", "1h")

    match = re.search(r"(\d+)h\s*(\d+)m", text)
    if match:
        h = int(match.group(1))
        m = int(match.group(2))
        return f"{h:02d}:{m:02d}:00"

    match = re.search(r"(\d+)m", text)
    if match:
        return f"00:{int(match.group(1)):02d}:00"

    match = re.search(r"(\d{1,2}:\d{2}:\d{2})", text)
    if match:
        return match.group(1)

    return None

def clean_ocr_text(text: str):
    lines = text.splitlines()

    cleaned = []
    for line in lines:
        line = line.strip()

        if not line:
            continue

        if any(x in line.lower() for x in [
            "upgrade", "unlock", "trial",
            "map", "record", "groups",
            "home", "openstreetmap", "garmin"
        ]):
            continue

        cleaned.append(line)

    return cleaned

def normalize_duration_text(text: str):
    text = text.lower().strip()

    text = text.replace("lh", "1h")
    text = text.replace("ih", "1h")

    text = re.sub(r"(\d+)h(\d+)m", r"\1h \2m", text)

    return text


def extract_duration(text: str):
    text = normalize_duration_text(text)

    match = re.search(r"(\d+)h\s*(\d+)m", text)
    if match:
        h = int(match.group(1))
        m = int(match.group(2))
        return f"{h:02d}:{m:02d}:00"

    match = re.search(r"(\d+)m", text)
    if match:
        return f"00:{int(match.group(1)):02d}:00"

    match = re.search(r"(\d{1,2}:\d{2}:\d{2})", text)
    if match:
        return match.group(1)

    return None

def extract_duration(text: str):
    text = normalize_duration_text(text)

    match = re.search(r"(\d+)h\s*(\d+)m", text)
    if match:
        h = int(match.group(1))
        m = int(match.group(2))
        return f"{h:02d}:{m:02d}:00"

    match = re.search(r"(\d+)m", text)
    if match:
        return f"00:{int(match.group(1)):02d}:00"

    match = re.search(r"(\d{1,2}:\d{2}:\d{2})", text)
    if match:
        return match.group(1)

    return None