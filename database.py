import os
from datetime import datetime, date, timedelta
from dotenv import load_dotenv
from supabase import create_client

load_dotenv()

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

if not SUPABASE_URL or not SUPABASE_KEY:
    raise ValueError(
        "SUPABASE_URL e SUPABASE_KEY precisam estar configurados no arquivo .env"
    )

supabase = create_client(SUPABASE_URL, SUPABASE_KEY)


def init_db():

    return True


def create_user(name, email, password_hash, school="", main_subject=""):
    data = {
        "name": name.strip(),
        "email": email.lower().strip(),
        "password_hash": password_hash,
        "school": school.strip(),
        "main_subject": main_subject.strip(),
        "created_at": datetime.now().isoformat()
    }

    supabase.table("users").insert(data).execute()


def get_user_by_email(email):
    response = (
        supabase
        .table("users")
        .select("*")
        .eq("email", (email or "").lower().strip())
        .limit(1)
        .execute()
    )

    if response.data:
        return response.data[0]

    return None


def get_user_by_id(user_id):
    response = (
        supabase
        .table("users")
        .select("*")
        .eq("id", user_id)
        .limit(1)
        .execute()
    )

    if response.data:
        return response.data[0]

    return None


def update_user(user_id, name, school, main_subject):
    data = {
        "name": name,
        "school": school,
        "main_subject": main_subject
    }

    supabase.table("users").update(data).eq("id", user_id).execute()


def update_password(user_id, password_hash):
    data = {
        "password_hash": password_hash,
        "reset_code": None,
        "reset_expires": None
    }

    supabase.table("users").update(data).eq("id", user_id).execute()


def set_reset_code(email, code):
    expires = (datetime.now() + timedelta(minutes=10)).isoformat()

    data = {
        "reset_code": code,
        "reset_expires": expires
    }

    supabase.table("users").update(data).eq(
        "email",
        email.lower().strip()
    ).execute()


def validate_reset_code(email, code):
    user = get_user_by_email(email)

    if not user or user.get("reset_code") != code:
        return False

    try:
        return datetime.now() <= datetime.fromisoformat(user.get("reset_expires"))
    except Exception:
        return False


def is_blocked(email):
    response = (
        supabase
        .table("login_security")
        .select("*")
        .eq("email", (email or "").lower().strip())
        .limit(1)
        .execute()
    )

    if not response.data:
        return False, None

    row = response.data[0]

    if not row.get("blocked_until"):
        return False, None

    until = datetime.fromisoformat(row["blocked_until"])

    if datetime.now() < until:
        return True, until

    reset_login_attempts(email)

    return False, None


def register_failed_login(email):
    email = (email or "").lower().strip()

    response = (
        supabase
        .table("login_security")
        .select("*")
        .eq("email", email)
        .limit(1)
        .execute()
    )

    if response.data:
        attempts = int(response.data[0].get("attempts") or 0) + 1
    else:
        attempts = 1

    blocked_until = None

    if attempts >= 5:
        blocked_until = (datetime.now() + timedelta(minutes=5)).isoformat()

    data = {
        "email": email,
        "attempts": attempts,
        "blocked_until": blocked_until
    }

    supabase.table("login_security").upsert(data).execute()

    return attempts, blocked_until


def reset_login_attempts(email):
    email = (email or "").lower().strip()

    data = {
        "email": email,
        "attempts": 0,
        "blocked_until": None
    }

    supabase.table("login_security").upsert(data).execute()


def count_today_generations(user_id):
    today = date.today().isoformat()

    response = (
        supabase
        .table("generations")
        .select("id")
        .eq("user_id", user_id)
        .gte("created_at", f"{today}T00:00:00")
        .lte("created_at", f"{today}T23:59:59")
        .execute()
    )

    return len(response.data or [])


def save_generation(
    user_id,
    material_type,
    subject,
    grade,
    theme,
    content,
    duration_seconds=0
):
    data = {
        "user_id": user_id,
        "material_type": material_type,
        "subject": subject,
        "grade": grade,
        "theme": theme,
        "content": content,
        "duration_seconds": int(duration_seconds or 0),
        "created_at": datetime.now().isoformat()
    }

    supabase.table("generations").insert(data).execute()


def list_generations(user_id):
    response = (
        supabase
        .table("generations")
        .select("*")
        .eq("user_id", user_id)
        .order("created_at", desc=True)
        .execute()
    )

    return response.data or []


def count_all_generations(user_id):
    response = (
        supabase
        .table("generations")
        .select("id")
        .eq("user_id", user_id)
        .execute()
    )

    return len(response.data or [])


def most_used_subject(user_id):
    response = (
        supabase
        .table("generations")
        .select("subject")
        .eq("user_id", user_id)
        .execute()
    )

    rows = response.data or []

    if not rows:
        return "—"

    counts = {}

    for row in rows:
        subject = row.get("subject") or "—"
        counts[subject] = counts.get(subject, 0) + 1

    return max(counts, key=counts.get)


def weekly_counts(user_id):
    response = (
        supabase
        .table("generations")
        .select("created_at")
        .eq("user_id", user_id)
        .execute()
    )

    rows = response.data or []

    counts = {}

    for row in rows:
        created_at = row.get("created_at")

        if not created_at:
            continue

        day = created_at[:10]

        counts[day] = counts.get(day, 0) + 1

    sorted_days = sorted(counts.items())[-7:]

    return sorted_days


def find_similar_generation(user_id, subject, grade, theme):
    response = (
        supabase
        .table("generations")
        .select("*")
        .eq("user_id", user_id)
        .ilike("subject", subject)
        .ilike("grade", grade)
        .ilike("theme", theme)
        .order("created_at", desc=True)
        .limit(1)
        .execute()
    )

    if response.data:
        return response.data[0]

    return None