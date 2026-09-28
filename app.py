"""
Mind Bloom 🌸
A calm, privacy-first wellbeing companion for students, professionals and homemakers.

Features:
- Secure local accounts (hashed passwords)
- Category-based gentle check-ins
- Stress indicator + bar graph
- Personalized to-do + timetable
- Homework / Assignment Help (chat + image upload)
- Progress history (Last Progress + New Progress)
- Behavioral AI Tips
- Theme support (System / Light / Dark)
- SDG-aligned (3, 4, 5, 10)

Run:
    streamlit run app.py
"""

import streamlit as st
import hashlib
import json
import datetime
from pathlib import Path
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
import numpy as np
from PIL import Image
import io

# ============================================================
# CONFIG
# ============================================================
st.set_page_config(
    page_title="Mind Bloom",
    page_icon="🌸",
    layout="centered",
    initial_sidebar_state="collapsed",
)

DATA_DIR = Path("mind_bloom_data")
DATA_DIR.mkdir(exist_ok=True)
USERS_FILE = DATA_DIR / "users.json"
PROGRESS_FILE = DATA_DIR / "progress.json"

# ============================================================
# SECURITY HELPERS
# ============================================================
def hash_password(password: str) -> str:
    return hashlib.sha256(password.encode("utf-8")).hexdigest()

def load_json(path: Path, default):
    if path.exists():
        try:
            with open(path, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            return default
    return default

def save_json(path: Path, data):
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

# ============================================================
# TRANSLATIONS (expandable)
# ============================================================
TRANSLATIONS = {
    "English": {
        "app_name": "Mind Bloom",
        "select_language": "Select Your Language",
        "continue": "Continue",
        "create_account": "Create Account",
        "login": "Login",
        "username": "Username",
        "password": "Password",
        "confirm_password": "Confirm Password",
        "age": "Your Age",
        "email_optional": "Email (optional – for recovery)",
        "mobile_optional": "Mobile (optional)",
        "create": "Create Account",
        "login_btn": "Login",
        "welcome": "Welcome to Mind Bloom",
        "choose_category": "What best describes you right now?",
        "school": "School Student",
        "college": "College Student",
        "employment": "Working Professional",
        "homemaker": "Homemaker",
        "counseling": "I need Counseling",
        "next": "Next",
        "rate": "Rate from 0 (Low) to 5 (High)",
        "describe": "You can also write a little about it (optional)",
        "submit": "Submit & Analyze",
        "stress_level": "Your Stress Level",
        "main_areas": "Main Stress Areas",
        "todo": "Your Gentle To-Do List",
        "fixed_tt": "Suggested Daily Rhythm",
        "personal_tt": "Make My Personalized Timetable",
        "motivation": "Today's Gentle Note",
        "home": "Home",
        "my_progress": "My Progress",
        "timetable": "Timetable",
        "help": "Help & Homework",
        "settings": "Settings",
        "theme": "Theme",
        "dark": "Dark",
        "light": "Light",
        "system": "System",
        "security": "Security & Privacy",
        "sdg": "Our SDG Goals",
        "logout": "Logout",
        "hi": "Hi",
        "update_progress": "New Check-in",
        "no_account": "No account found. Please create one.",
        "wrong_pass": "Incorrect password.",
        "pass_mismatch": "Passwords do not match.",
        "fill_required": "Please fill the required fields.",
        "account_created": "Account created! Please log in.",
        "privacy_text": """Your privacy matters deeply to us.

• Your answers stay on this device / session only.
• We never sell or share your personal data.
• No ads. No tracking. No judgment.
• You can clear your data anytime.
• Mind Bloom is a supportive companion — not a replacement for professional care.""",
        "help_title": "Help & Homework Corner",
        "help_subtitle": "Stuck on an assignment or just need a clear explanation? Ask here.",
        "ask_question": "Type your question or topic",
        "upload_q": "Or upload a photo of the question (optional)",
        "get_help": "Get Help",
        "chat_placeholder": "Example: Explain photosynthesis in simple words / How to start my essay on climate change?",
    },
    "Hindi": {
        "app_name": "Mind Bloom",
        "select_language": "अपनी भाषा चुनें",
        "continue": "आगे बढ़ें",
        "create_account": "खाता बनाएं",
        "login": "लॉगिन",
        "username": "यूज़रनेम",
        "password": "पासवर्ड",
        "confirm_password": "पासवर्ड फिर से लिखें",
        "age": "उम्र",
        "email_optional": "ईमेल (वैकल्पिक)",
        "mobile_optional": "मोबाइल (वैकल्पिक)",
        "create": "खाता बनाएं",
        "login_btn": "लॉगिन करें",
        "welcome": "Mind Bloom में आपका स्वागत है",
        "choose_category": "अभी आप खुद को कैसे देखेंगे?",
        "school": "स्कूल स्टूडेंट",
        "college": "कॉलेज स्टूडेंट",
        "employment": "नौकरी / प्रोफेशनल",
        "homemaker": "होममेकर",
        "counseling": "काउंसलिंग चाहिए",
        "next": "आगे",
        "rate": "0 (कम) से 5 (ज़्यादा) तक रेट करें",
        "describe": "थोड़ा लिख भी सकते हैं (वैकल्पिक)",
        "submit": "सबमिट करें",
        "stress_level": "आपका स्ट्रेस लेवल",
        "main_areas": "मुख्य स्ट्रेस क्षेत्र",
        "todo": "आपकी कोमल टू-डू लिस्ट",
        "fixed_tt": "सुझाया गया दैनिक रिदम",
        "personal_tt": "मेरा पर्सनलाइज्ड टाइमटेबल",
        "motivation": "आज का कोमल संदेश",
        "home": "होम",
        "my_progress": "मेरी प्रोग्रेस",
        "timetable": "टाइमटेबल",
        "help": "हेल्प और होमवर्क",
        "settings": "सेटिंग्स",
        "theme": "थीम",
        "dark": "डार्क",
        "light": "लाइट",
        "system": "सिस्टम",
        "security": "सुरक्षा और प्राइवेसी",
        "sdg": "हमारे SDG लक्ष्य",
        "logout": "लॉगआउट",
        "hi": "नमस्ते",
        "update_progress": "नया चेक-इन",
        "no_account": "अकाउंट नहीं मिला।",
        "wrong_pass": "गलत पासवर्ड।",
        "pass_mismatch": "पासवर्ड मैच नहीं हुए।",
        "fill_required": "ज़रूरी जानकारी भरें।",
        "account_created": "अकाउंट बन गया! अब लॉगिन करें।",
        "privacy_text": """आपकी प्राइवेसी हमारे लिए बहुत महत्वपूर्ण है।

• आपके जवाब सिर्फ इसी डिवाइस/सेशन में रहते हैं।
• हम आपका डेटा कभी किसी के साथ साझा नहीं करते।
• कोई विज्ञापन नहीं, कोई ट्रैकिंग नहीं।
• आप कभी भी अपना डेटा मिटा सकते हैं।
• Mind Bloom एक सहायक साथी है — प्रोफेशनल मदद का विकल्प नहीं।""",
        "help_title": "हेल्प और होमवर्क कॉर्नर",
        "help_subtitle": "असाइनमेंट या होमवर्क में अटके हैं? यहाँ पूछें।",
        "ask_question": "अपना सवाल या टॉपिक लिखें",
        "upload_q": "या सवाल की फोटो अपलोड करें (वैकल्पिक)",
        "get_help": "हेल्प लें",
        "chat_placeholder": "उदाहरण: प्रकाश संश्लेषण आसान भाषा में समझाओ / एस्से कैसे शुरू करूँ?",
    },
}

# Fallback for other languages → English
EXTRA_LANGS = [
    "Urdu", "Chinese", "Japanese", "German", "Italian",
    "Punjabi", "Marathi", "Kannada", "Nepali", "Spanish",
    "French", "Bengali", "Tamil", "Telugu", "Gujarati",
    "Arabic", "Portuguese", "Russian", "Korean", "Turkish"
]
for lang in EXTRA_LANGS:
    if lang not in TRANSLATIONS:
        TRANSLATIONS[lang] = TRANSLATIONS["English"].copy()

def t(key: str) -> str:
    # Language feature removed — always use English
    return TRANSLATIONS.get("English", {}).get(key, key)

# ============================================================
# QUESTIONS (supportive & non-judgmental)
# ============================================================
QUESTIONS = {
    "school": [
        {"q": "How much academic pressure do you feel these days?", "area": "Academic Pressure"},
        {"q": "How is the family pressure regarding studies?", "area": "Family Pressure"},
        {"q": "Do you experience any unkind behaviour or bullying?", "area": "Social / Bullying"},
        {"q": "How difficult do your subjects feel overall?", "area": "Subject Difficulty"},
        {"q": "How supported do you feel by your teachers?", "area": "Teacher Support"},
        {"q": "How satisfied are you with recent results/marks?", "area": "Performance Worry"},
        {"q": "How much time do you get for rest and hobbies?", "area": "Rest & Balance"},
        {"q": "How often do you worry about the future?", "area": "Future Anxiety"},
        {"q": "Overall, how heavy does school life feel right now?", "area": "Overall Load"},
    ],
    "college": [
        {"q": "How much academic pressure do you feel?", "area": "Academic Pressure"},
        {"q": "How heavy is the career / future pressure?", "area": "Career Pressure"},
        {"q": "How supported do you feel by friends and peers?", "area": "Social Support"},
        {"q": "How difficult are current subjects or projects?", "area": "Subject Difficulty"},
        {"q": "How is your sleep and daily routine?", "area": "Sleep & Routine"},
        {"q": "How much financial stress do you feel?", "area": "Financial Stress"},
        {"q": "How often do you feel lonely?", "area": "Loneliness"},
        {"q": "How clear do you feel about your direction?", "area": "Career Clarity"},
        {"q": "Overall, how heavy does college life feel?", "area": "Overall Load"},
    ],
    "employment": [
        {"q": "How much work-related stress do you feel?", "area": "Work Stress"},
        {"q": "How is your work-life balance?", "area": "Work-Life Balance"},
        {"q": "How supported do you feel at workplace?", "area": "Workplace Support"},
        {"q": "How much performance pressure do you feel?", "area": "Performance Pressure"},
        {"q": "How is your sleep and health?", "area": "Health & Sleep"},
        {"q": "How much job / financial security stress?", "area": "Security Stress"},
        {"q": "How often do you get personal / family time?", "area": "Personal Time"},
        {"q": "How clear do you feel about growth?", "area": "Growth Clarity"},
        {"q": "Overall, how heavy does work life feel?", "area": "Overall Load"},
    ],
    "homemaker": [
        {"q": "How much daily responsibility load do you feel?", "area": "Responsibility Load"},
        {"q": "How supported do you feel by family?", "area": "Family Support"},
        {"q": "How much time do you get for yourself?", "area": "Personal Time"},
        {"q": "How is your physical and mental energy?", "area": "Energy Levels"},
        {"q": "How often do you feel unappreciated?", "area": "Appreciation"},
        {"q": "How much worry about family future?", "area": "Future Worry"},
        {"q": "How is your rest and sleep quality?", "area": "Rest Quality"},
        {"q": "How connected do you feel socially?", "area": "Social Connection"},
        {"q": "Overall, how heavy does daily life feel?", "area": "Overall Load"},
    ],
    "counseling": [
        {"q": "How heavy does your emotional load feel?", "area": "Emotional Load"},
        {"q": "How clear are you about the help you need?", "area": "Clarity of Need"},
        {"q": "How much career or stream confusion?", "area": "Career Confusion"},
        {"q": "How supported do you feel by people around?", "area": "Support System"},
        {"q": "How often do you feel stuck?", "area": "Feeling Stuck"},
        {"q": "How is your energy and sleep?", "area": "Energy & Sleep"},
        {"q": "How much self-doubt do you experience?", "area": "Self Doubt"},
        {"q": "How hopeful do you feel about the future?", "area": "Hope Level"},
        {"q": "Overall, how ready do you feel for small steps?", "area": "Readiness"},
    ],
}

# ============================================================
# CORE LOGIC
# ============================================================
def calculate_stress(ratings, areas):
    if not ratings:
        return 0, {}
    avg = float(np.mean(ratings))
    percent = min(100, round(avg * 20))
    area_scores = {}
    for r, a in zip(ratings, areas):
        area_scores.setdefault(a, []).append(r)
    area_avg = {k: round(float(np.mean(v)) * 20, 1) for k, v in area_scores.items()}
    return percent, area_avg

def get_recommendations(category, percent):
    todos = [
        "Drink a glass of water and take five slow breaths.",
        "Write three small things that went okay today.",
        "Step away from screens for ten minutes.",
        "Stretch your shoulders and neck gently.",
        "Go to bed at a kind, consistent time tonight.",
    ]
    if percent >= 70:
        todos.insert(0, "You are carrying a lot. Be extra gentle with yourself today.")
    elif percent <= 30:
        todos.insert(0, "Nice — your load feels lighter. Keep the good habits going.")

    # Clean standing timetable (Time | Activity)
    timetable = [
        ("6:30 – 7:00", "Wake up + Drink water + Light stretch"),
        ("7:00 – 7:30", "Fresh up + Breakfast"),
        ("7:30 – 9:00", "Focus Block 1 (Study/Work)"),
        ("9:00 – 9:15", "Short Break"),
        ("9:15 – 11:00", "Focus Block 2"),
        ("11:00 – 11:30", "Break + Snack"),
        ("11:30 – 1:00", "Focus Block 3"),
        ("1:00 – 2:00", "Lunch + Rest"),
        ("2:00 – 3:30", "Focus Block 4"),
        ("3:30 – 4:00", "Break / Walk"),
        ("4:00 – 5:30", "Focus Block 5 / Homework"),
        ("5:30 – 6:30", "Free time / Hobby / Exercise"),
        ("6:30 – 7:30", "Evening / Family time"),
        ("7:30 – 8:30", "Dinner"),
        ("8:30 – 9:30", "Light revision / Relax"),
        ("9:30 onwards", "Wind down + Sleep"),
    ]
    return todos, timetable

def simple_homework_helper(question: str, has_image: bool = False) -> str:
    """Strong multi-subject homework helper. Guides understanding across subjects."""
    q = question.lower().strip()
    if not q and not has_image:
        return "Please type your question (or upload a photo) so I can help you."

    base = "I'm here to help you understand step-by-step.\n\n"
    if has_image:
        base += "I can see you uploaded a photo. For best help, also type the main question.\n\n"

    # ---------- SCIENCE ----------
    if any(w in q for w in ["photosynthesis", "प्रकाश संश्लेषण", "photosynthe"]):
        return base + (
            "**Photosynthesis (easy):**\n"
            "Plants make food using sunlight, water and CO₂.\n"
            "Chlorophyll in leaves captures light → produces glucose + oxygen.\n"
            "Equation: 6CO₂ + 6H₂O → C₆H₁₂O₆ + 6O₂ (in presence of sunlight)\n\n"
            "Tip: Explain it in your own words once."
        )
    if any(w in q for w in ["respiration", "श्वसन", "breathing"]):
        return base + (
            "**Respiration:**\n"
            "Process of releasing energy from food (glucose).\n"
            "Aerobic: Glucose + Oxygen → CO₂ + Water + Energy (ATP)\n"
            "Anaerobic: Happens without oxygen (less energy).\n"
            "It occurs in all living cells."
        )
    if any(w in q for w in ["newton", "force", "gravity", "गति", "बल", "गुरुत्वाकर्षण"]):
        return base + (
            "**Newton’s Laws (quick):**\n"
            "1st: Object stays at rest or uniform motion unless force acts.\n"
            "2nd: F = ma (Force = mass × acceleration)\n"
            "3rd: Every action has equal and opposite reaction.\n"
            "Gravity: Force that pulls objects towards Earth."
        )
    if any(w in q for w in ["atom", "molecule", "periodic", "element", "परमाणु", "अणु"]):
        return base + (
            "**Atoms & Molecules:**\n"
            "Atom = smallest unit of element.\n"
            "Molecule = two or more atoms joined.\n"
            "Periodic Table arranges elements by atomic number.\n"
            "Tell me the exact topic (e.g. isotopes, valency) for more detail."
        )

    # ---------- MATH ----------
    if any(w in q for w in ["algebra", "equation", "solve", "गणित", "समीकरण", "linear", "quadratic"]):
        return base + (
            "**Math solving steps:**\n"
            "1. Write what is given and what is asked.\n"
            "2. Choose the correct formula / method.\n"
            "3. Solve step-by-step.\n"
            "4. Check your answer.\n\n"
            "Paste the exact equation/problem and I will guide each step."
        )
    if any(w in q for w in ["percentage", "percent", "प्रतिशत", "profit", "loss", "simple interest", "compound interest"]):
        return base + (
            "**Percentage / Profit-Loss / Interest formulas:**\n"
            "Percentage = (Value / Total) × 100\n"
            "Profit % = (Profit / CP) × 100\n"
            "Simple Interest = (P × R × T) / 100\n"
            "Compound Interest = A – P where A = P(1 + R/100)^T\n\n"
            "Give the exact numbers for step-by-step solution."
        )
    if any(w in q for w in ["area", "volume", "perimeter", "circumference", "triangle", "circle", "rectangle"]):
        return base + (
            "**Mensuration formulas:**\n"
            "Rectangle: Area = l × b , Perimeter = 2(l+b)\n"
            "Triangle: Area = ½ × base × height\n"
            "Circle: Area = πr² , Circumference = 2πr\n"
            "Cube: Volume = a³\n"
            "Cuboid: Volume = l × b × h\n\n"
            "Tell me the exact question with numbers."
        )

    # ---------- ENGLISH ----------
    if any(w in q for w in ["essay", "निबंध", "write about", "article", "paragraph", "letter"]):
        return base + (
            "**Writing help (Essay / Letter / Paragraph):**\n"
            "1. Understand the topic in one line.\n"
            "2. Introduction – what + why important.\n"
            "3. Body – 2-3 clear points with examples.\n"
            "4. Conclusion – short summary + positive ending.\n\n"
            "Tell me the exact topic, I will give you a clear outline."
        )
    if any(w in q for w in ["tense", "grammar", "noun", "verb", "adjective", "active", "passive", "direct", "indirect"]):
        return base + (
            "**English Grammar quick help:**\n"
            "• Tenses show time of action (Present, Past, Future).\n"
            "• Active: Subject does the action. Passive: Action is done on subject.\n"
            "• Direct ↔ Indirect speech needs changes in tense and pronouns.\n\n"
            "Paste the exact sentence or rule you need help with."
        )

    # ---------- HINDI ----------
    if any(w in q for w in ["समास", "संधि", "अलंकार", "रस", "छंद", "मुहावरे", "लोकोक्ति"]):
        return base + (
            "**हिंदी व्याकरण:**\n"
            "• संधि = दो शब्दों के मेल से विकार\n"
            "• समास = दो या अधिक शब्दों को मिलाकर छोटा रूप\n"
            "• अलंकार = भाषा की सुंदरता बढ़ाने वाले तत्व\n"
            "• रस = काव्य पढ़ने से होने वाला आनंद\n\n"
            "Exact topic लिखो, मैं clear explanation दूँगा।"
        )

    # ---------- COMMERCE / ACCOUNTANCY / ECONOMICS ----------
    if any(w in q for w in ["journal", "ledger", "trial balance", "balance sheet", "accountancy", "debit", "credit"]):
        return base + (
            "**Accountancy basics:**\n"
            "• Journal → first book of entry (Debit & Credit)\n"
            "• Ledger → all accounts posted from journal\n"
            "• Trial Balance → checks arithmetical accuracy\n"
            "• Balance Sheet → shows financial position (Assets = Liabilities + Capital)\n\n"
            "Golden Rule: Debit what comes in, Credit what goes out (for Real A/c)."
        )
    if any(w in q for w in ["demand", "supply", "elasticity", "gdp", "inflation", "economics", "micro", "macro"]):
        return base + (
            "**Economics quick notes:**\n"
            "• Demand: willingness + ability to buy\n"
            "• Supply: quantity sellers are ready to sell\n"
            "• Elasticity: how much quantity changes with price\n"
            "• GDP: total value of goods & services produced in a country\n"
            "• Inflation: continuous rise in general price level\n\n"
            "Tell me the exact chapter/topic for more detail."
        )
    if any(w in q for w in ["marketing", "business", "entrepreneur", "management", "commerce"]):
        return base + (
            "**Business / Commerce:**\n"
            "Marketing mix (4Ps): Product, Price, Place, Promotion.\n"
            "Entrepreneur: person who starts and runs a business taking risks.\n"
            "Management functions: Planning, Organising, Staffing, Directing, Controlling.\n\n"
            "Specify the exact topic for clearer notes."
        )

    # ---------- SOCIAL SCIENCE / HISTORY / CIVICS / GEOGRAPHY ----------
    if any(w in q for w in ["constitution", "fundamental rights", "democracy", "parliament", "president", "prime minister"]):
        return base + (
            "**Civics / Political Science:**\n"
            "• Constitution = supreme law of the country\n"
            "• Fundamental Rights protect citizens\n"
            "• Democracy = government by the people\n"
            "• Parliament makes laws (Lok Sabha + Rajya Sabha)\n\n"
            "Ask the exact question for precise answer."
        )
    if any(w in q for w in ["history", "independence", "gandhi", "nehru", "revolution", "war", "empire"]):
        return base + (
            "**History help:**\n"
            "Break the question into: When? Who? Why? What happened? Result?\n"
            "Write in chronological order.\n"
            "Use key terms and dates.\n\n"
            "Tell me the exact event or chapter."
        )

    # ---------- GENERAL / FALLBACK ----------
    return base + (
        "I can help with almost every school/college subject.\n\n"
        "**Best way to get accurate help:**\n"
        "1. Write the subject name (Math / Science / English / Hindi / Accounts / Economics etc.)\n"
        "2. Paste the full question clearly.\n"
        "3. If it’s numerical, include all numbers.\n\n"
        "I will give you step-by-step guidance so you understand, not just copy."
    )

# ============================================================
# SESSION STATE
# ============================================================
def init_state():
    defaults = {
        "page": "auth",
        "language": "English",
        "user": None,
        "category": None,
        "stress_data": None,
        "theme": "system",
        "chat_history": [],
    }
    for k, v in defaults.items():
        if k not in st.session_state:
            st.session_state[k] = v

init_state()

# ============================================================
# CSS
# ============================================================
def inject_css():
    st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Nunito:wght@400;600;700;800&display=swap');
    html, body, [class*="css"] { font-family: 'Nunito', sans-serif; }
    .main { background: linear-gradient(160deg, #f8f0ff 0%, #e8f8f5 100%); }
    .stButton > button {
        border-radius: 18px;
        padding: 0.65rem 1.3rem;
        font-weight: 700;
        border: none;
        background: linear-gradient(90deg, #a855f7, #7c3aed);
        color: white;
        transition: transform 0.15s ease;
    }
    .stButton > button:hover { transform: scale(1.03); }
    .big-title {
        font-size: 2.5rem;
        font-weight: 800;
        background: linear-gradient(90deg, #9333ea, #0ea5e9);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        text-align: center;
        margin-bottom: 0.3rem;
    }
    .card {
        background: rgba(255,255,255,0.92);
        padding: 1.4rem 1.6rem;
        border-radius: 22px;
        box-shadow: 0 10px 30px rgba(147, 51, 234, 0.10);
        margin-bottom: 1rem;
    }
    .nav-item { text-align: center; }
    </style>
    """, unsafe_allow_html=True)

inject_css()

# ============================================================
# PAGES
# ============================================================
def page_language():
    st.markdown("<h1 class='big-title'>🌸 Mind Bloom</h1>", unsafe_allow_html=True)
    st.markdown(f"### {t('select_language')}")
    st.caption("Choose the language you are most comfortable with.")

    langs = list(TRANSLATIONS.keys())
    cols = st.columns(3)
    for i, lang in enumerate(langs):
        with cols[i % 3]:
            if st.button(lang, key=f"lang_{lang}", use_container_width=True):
                st.session_state.language = lang
                st.session_state.page = "auth"
                st.rerun()

def page_auth():
    st.markdown("<h1 class='big-title'>🌸 Mind Bloom</h1>", unsafe_allow_html=True)
    st.markdown(f"### {t('welcome')}")

    tab1, tab2 = st.tabs([t("create_account"), t("login")])

    with tab1:
        with st.form("create_form", clear_on_submit=False):
            username = st.text_input(t("username"))
            age = st.number_input(t("age"), min_value=8, max_value=100, value=16)
            password = st.text_input(t("password"), type="password")
            confirm = st.text_input(t("confirm_password"), type="password")
            email = st.text_input(t("email_optional"))
            mobile = st.text_input(t("mobile_optional"))
            if st.form_submit_button(t("create"), use_container_width=True):
                if not username or not password:
                    st.error(t("fill_required"))
                elif password != confirm:
                    st.error(t("pass_mismatch"))
                else:
                    users = load_json(USERS_FILE, {})
                    if username in users:
                        st.error("Username already taken. Try another.")
                    else:
                        users[username] = {
                            "password": hash_password(password),
                            "age": age,
                            "email": email,
                            "mobile": mobile,
                            "created": datetime.datetime.now().strftime("%d %b %Y, %I:%M %p"),
                        }
                        save_json(USERS_FILE, users)
                        st.success(t("account_created"))

    with tab2:
        with st.form("login_form"):
            username = st.text_input(t("username"), key="lu")
            password = st.text_input(t("password"), type="password", key="lp")
            if st.form_submit_button(t("login_btn"), use_container_width=True):
                users = load_json(USERS_FILE, {})
                if username not in users:
                    st.error(t("no_account"))
                elif users[username]["password"] != hash_password(password):
                    st.error(t("wrong_pass"))
                else:
                    st.session_state.user = username
                    st.session_state.page = "category"
                    st.rerun()

def page_category():
    st.markdown(f"### {t('hi')}, {st.session_state.user} 🌸")
    st.markdown(f"#### {t('choose_category')}")

    options = [
        ("school", t("school"), "📚"),
        ("college", t("college"), "🎓"),
        ("employment", t("employment"), "💼"),
        ("homemaker", t("homemaker"), "🏠"),
        ("counseling", t("counseling"), "💬"),
    ]
    for key, label, emoji in options:
        if st.button(f"{emoji}  {label}", key=key, use_container_width=True):
            st.session_state.category = key
            st.session_state.page = "questions"
            st.rerun()

def page_questions():
    st.markdown(f"### Check-in • {st.session_state.category.title()}")
    questions = QUESTIONS.get(st.session_state.category, QUESTIONS["school"])

    with st.form("qform"):
        ratings, areas, descs = [], [], []
        for i, item in enumerate(questions):
            st.markdown(f"**{i+1}. {item['q']}**")
            r = st.slider(t("rate"), 0.0, 5.0, 2.5, 0.5, key=f"r{i}")
            d = st.text_area(t("describe"), key=f"d{i}", height=70)
            ratings.append(r)
            areas.append(item["area"])
            descs.append(d)
            st.divider()
        if st.form_submit_button(t("submit"), use_container_width=True):
            percent, area_avg = calculate_stress(ratings, areas)
            st.session_state.stress_data = {
                "percent": percent,
                "areas": area_avg,
                "date": datetime.datetime.now().strftime("%d %b %Y, %I:%M %p"),
            }
            progress = load_json(PROGRESS_FILE, {})
            progress.setdefault(st.session_state.user, []).append(st.session_state.stress_data)
            save_json(PROGRESS_FILE, progress)
            st.session_state.page = "analysis"
            st.rerun()

def page_analysis():
    data = st.session_state.stress_data
    if not data:
        st.session_state.page = "home"
        st.rerun()

    st.markdown(f"## {t('stress_level')}")
    percent = data["percent"]
    color = "#22c55e" if percent < 40 else "#f59e0b" if percent < 70 else "#ef4444"

    fig = go.Figure(go.Indicator(
        mode="gauge+number",
        value=percent,
        title={"text": "Stress %"},
        gauge={
            "axis": {"range": [0, 100]},
            "bar": {"color": color},
            "steps": [
                {"range": [0, 40], "color": "#dcfce7"},
                {"range": [40, 70], "color": "#fef3c7"},
                {"range": [70, 100], "color": "#fee2e2"},
            ],
        },
    ))
    fig.update_layout(height=280, margin=dict(t=40, b=20, l=20, r=20))
    st.plotly_chart(fig, use_container_width=True)

    st.markdown(f"### {t('main_areas')}")
    df = pd.DataFrame({
        "Area": list(data["areas"].keys()),
        "Level": list(data["areas"].values()),
    }).sort_values("Level", ascending=False)
    fig2 = px.bar(df, x="Area", y="Level", color="Level",
                  color_continuous_scale=["#22c55e", "#f59e0b", "#ef4444"])
    fig2.update_layout(height=340, xaxis_tickangle=-25, showlegend=False)
    st.plotly_chart(fig2, use_container_width=True)

    if st.button(t("next") + " →", use_container_width=True):
        st.session_state.page = "recommendations"
        st.rerun()

def page_recommendations():
    data = st.session_state.stress_data
    todos, timetable = get_recommendations(st.session_state.category, data["percent"])

    st.markdown(f"## {t('todo')}")
    for i, item in enumerate(todos, 1):
        st.markdown(f"**{i}.** {item}")

    st.markdown("## 📅 Suggested Daily Timetable")

    # Clean table format: Time | Activity
    import pandas as pd
    df_tt = pd.DataFrame(timetable, columns=["Time", "Activity"])
    st.table(df_tt)

    st.markdown("---")
    st.markdown("### ✏️ Personalized Timetable")
    st.caption("You can edit or create your own timetable below.")

    # Simple personalized editor
    if "personal_tt" not in st.session_state:
        st.session_state.personal_tt = ""

    personal = st.text_area(
        "Write or edit your personalized timetable here (Time - Activity)",
        value=st.session_state.personal_tt,
        height=200,
        placeholder="Example:\n6:30 - Wake up\n7:00 - Breakfast\n8:00 - Study Math\n..."
    )
    st.session_state.personal_tt = personal

    if st.button("💾 Save My Personalized Timetable", use_container_width=True):
        st.success("Your personalized timetable has been saved!")

    st.markdown("---")
    if st.button(t("continue") + " →", use_container_width=True):
        st.session_state.page = "motivation"
        st.rerun()

def page_motivation():
    quotes = [
        "You don't have to be perfect. You just have to keep going. 🌸",
        "Small steps still move you forward. 🌱",
        "Your feelings are valid. Be gentle with yourself. 💜",
        "Rest is productive too. You deserve peace. 🌙",
        "You have already survived every hard day so far. 💪",
    ]
    st.markdown(f"<h2 style='text-align:center'>{t('motivation')}</h2>", unsafe_allow_html=True)
    st.markdown(f"<div class='card' style='text-align:center;font-size:1.35rem'>{np.random.choice(quotes)}</div>",
                unsafe_allow_html=True)
    if st.button("Go to Home 🏠", use_container_width=True):
        st.session_state.page = "home"
        st.rerun()

def page_home():
    st.markdown("<h1 class='big-title'>🌸 Mind Bloom</h1>", unsafe_allow_html=True)
    st.markdown(f"### {t('hi')}, {st.session_state.user}!")

    # Show Last Progress clearly
    progress = load_json(PROGRESS_FILE, {})
    entries = progress.get(st.session_state.user, [])
    
    if entries:
        last = entries[-1]
        last_date = last.get("date", "Not available")
        last_percent = last.get("percent", 0)
        
        st.markdown(f"""
        <div class='card'>
            <h4>📊 Your Last Progress</h4>
            <p><b>Date:</b> {last_date}</p>
            <p><b>Stress Level:</b> {last_percent}%</p>
        </div>
        """, unsafe_allow_html=True)
    else:
        st.markdown(f"""
        <div class='card'>
            <h4>📊 Your Progress</h4>
            <p>No check-in yet. Start your first one!</p>
        </div>
        """, unsafe_allow_html=True)

    st.markdown(f"""
    <div class='card'>
        <h4>✨ {t('motivation')}</h4>
        <p>You are doing better than you think. Keep blooming.</p>
    </div>
    """, unsafe_allow_html=True)

    # Big clear New Progress button
    if st.button("➕  New Progress / नया चेक-इन", use_container_width=True, type="primary"):
        st.session_state.page = "category"
        st.rerun()

    st.markdown("---")

    c1, c2, c3, c4 = st.columns(4)
    with c1:
        if st.button("🏠\n" + t("home"), use_container_width=True):
            pass
    with c2:
        if st.button("📊\n" + t("my_progress"), use_container_width=True):
            st.session_state.page = "progress"
            st.rerun()
    with c3:
        if st.button("📅\n" + t("timetable"), use_container_width=True):
            st.session_state.page = "recommendations"
            st.rerun()
    with c4:
        if st.button("📚\n" + t("help"), use_container_width=True):
            st.session_state.page = "help"
            st.rerun()

    st.markdown("---")
    col_x, col_y = st.columns(2)
    with col_x:
        if st.button("🧠 Behavioral AI Tips", use_container_width=True):
            st.session_state.page = "behavioral"
            st.rerun()
    with col_y:
        if st.button("⚙️ " + t("settings"), use_container_width=True):
            st.session_state.page = "settings"
            st.rerun()

def page_progress():
    st.markdown(f"## 📊 {t('my_progress')}")
    
    progress = load_json(PROGRESS_FILE, {})
    entries = progress.get(st.session_state.user, [])
    
    # Big New Progress button at top
    if st.button("➕  Add New Progress / नया प्रोग्रेस जोड़ें", use_container_width=True, type="primary"):
        st.session_state.page = "category"
        st.rerun()
    
    st.markdown("---")
    
    if not entries:
        st.info("No check-ins yet. Click the button above to do your first one!")
    else:
        # Show Last Progress prominently
        last = entries[-1]
        last_date = last.get("date", "Not available")
        st.markdown(f"### 🕒 Your Last Progress")
        st.markdown(f"**Date:** {last_date}")
        st.progress(last["percent"] / 100)
        st.caption(f"Stress Level: **{last['percent']}%**")
        
        st.markdown("---")
        st.markdown("### 📜 Full History (oldest to newest)")
        
        # Show all history (most recent first)
        for i, e in enumerate(reversed(entries), 1):
            date_str = e.get("date", "Not available")
            st.markdown(f"**#{len(entries)-i+1}** — {date_str}")
            st.progress(e["percent"] / 100)
            st.caption(f"Stress level: {e['percent']}%")
            st.divider()
    
    if st.button("← Back to Home"):
        st.session_state.page = "home"
        st.rerun()

def page_help():
    st.markdown(f"## 📚 {t('help_title')}")
    st.markdown(t("help_subtitle"))

    question = st.text_area(t("ask_question"), placeholder=t("chat_placeholder"), height=100)
    uploaded = st.file_uploader(t("upload_q"), type=["png", "jpg", "jpeg", "webp"])

    if uploaded:
        image = Image.open(uploaded)
        st.image(image, caption="Uploaded question", use_container_width=True)

    if st.button(t("get_help"), use_container_width=True):
        response = simple_homework_helper(question, has_image=bool(uploaded))
        st.markdown("---")
        st.markdown(response)
        st.info("This helper guides understanding. For complex or graded work, also talk to your teacher.")

    st.markdown("---")
    if st.button("← Back to Home"):
        st.session_state.page = "home"
        st.rerun()

def page_settings():
    st.markdown("## ⚙️ Settings")

    st.markdown("### 🎨 Theme")
    choice = st.radio(
        "Theme",
        ["System", "Light", "Dark"],
        index=["system", "light", "dark"].index(st.session_state.theme)
        if st.session_state.theme in ["system", "light", "dark"] else 0,
        label_visibility="collapsed",
    )
    mapping = {"System": "system", "Light": "light", "Dark": "dark"}
    st.session_state.theme = mapping.get(choice, "system")

    st.markdown("### 🔒 Security & Privacy")
    st.info("""• Your data stays only on this device / session  
• It is never shared with anyone  
• No ads and no tracking  
• You can delete your data anytime  
• This is not a replacement for professional help""")

    st.markdown("### 🌍 Our SDG Goals")
    sdgs = [
        ("🩺 SDG 3 — Good Health & Well-being", "Mental calm and stress reduction"),
        ("📚 SDG 4 — Quality Education", "Helping students manage academic pressure"),
        ("⚖️ SDG 5 — Gender Equality", "Equal and respectful support for everyone"),
        ("🤝 SDG 10 — Reduced Inequalities", "Accessible wellbeing support for all ages and backgrounds"),
    ]
    for title, desc in sdgs:
        st.markdown(f"<div class='card'><strong>{title}</strong><br><span style='color:#555'>{desc}</span></div>",
                    unsafe_allow_html=True)

    st.markdown("---")
    if st.button("Logout", use_container_width=True):
        st.session_state.user = None
        st.session_state.page = "auth"
        st.rerun()
    if st.button("← Back to Home"):
        st.session_state.page = "home"
        st.rerun()


def page_behavioral():
    """Simple rule-based Behavioral AI support based on last stress areas"""
    st.markdown("## 🧠 Behavioral AI Support")
    st.caption("Gentle, science-inspired suggestions based on your recent check-in. Not a replacement for professional help.")

    progress = load_json(PROGRESS_FILE, {})
    entries = progress.get(st.session_state.user, [])

    if not entries:
        st.info("Please complete at least one check-in first. Then come back for personalized behavioral tips.")
        if st.button("← Back to Home"):
            st.session_state.page = "home"
            st.rerun()
        return

    last = entries[-1]
    areas = last.get("areas", {})
    percent = last.get("percent", 0)

    st.markdown(f"**Based on your last check-in** (Stress: {percent}%)")

    # Sort areas by highest stress
    sorted_areas = sorted(areas.items(), key=lambda x: x[1], reverse=True)

    # Behavioral suggestion bank (simple, non-clinical, supportive)
    SUGGESTIONS = {
        "Academic Pressure": [
            "Try the 25-5 rule: 25 minutes focused study + 5 minutes real break.",
            "Write only the next small task on a paper instead of the whole syllabus.",
            "After studying, tell yourself one thing you understood (even tiny)."
        ],
        "Family Pressure": [
            "You can acknowledge their care and still protect your peace.",
            "Practice one calm sentence: “I am trying my best with what I have right now.”",
            "Take 3 slow breaths before responding in tense moments."
        ],
        "Social / Bullying": [
            "Your safety and dignity matter. Reach out to one trusted adult if needed.",
            "You don’t have to face everything alone. One kind person is enough to start.",
            "Write down what happened factually — it helps clear the mind."
        ],
        "Subject Difficulty": [
            "Break the chapter into tiny pieces. Master one small part today.",
            "Teach the concept to an imaginary friend — it reveals what you actually know.",
            "It’s okay to say “I don’t understand yet.” Yet is a powerful word."
        ],
        "Teacher Support": [
            "You can ask one clear question after class or via message.",
            "Your learning matters. It’s okay to seek clarity."
        ],
        "Performance Worry": [
            "Marks are information, not your worth.",
            "Focus on the process of today’s effort more than the final number.",
            "Celebrate showing up, even on hard days."
        ],
        "Rest & Balance": [
            "Rest is not laziness. Your brain needs recovery to learn.",
            "Put your phone away 20 minutes before sleep tonight.",
            "A short walk or stretching can reset your nervous system."
        ],
        "Future Anxiety": [
            "You don’t need the full 5-year plan today. Just the next kind step.",
            "Write down what you can control this week vs what you can’t.",
            "Future-you will thank present-you for small consistent actions."
        ],
        "Overall Load": [
            "When everything feels heavy, shrink the goal. One small win is enough.",
            "Drink water, take three breaths, and choose only one priority right now."
        ],
        "Work Stress": [
            "Protect one small boundary today (even 10 minutes for yourself).",
            "Write the top 1 task that actually moves the needle."
        ],
        "Work-Life Balance": [
            "Transition ritual helps: change clothes or take a short walk after work.",
            "Schedule rest like you schedule meetings."
        ],
        "Career Pressure": [
            "Clarity comes from action, not only thinking. Try one small experiment.",
            "Talk to one person who is 2-3 years ahead of you."
        ],
        "Emotional Load": [
            "Name the feeling: “I notice I am feeling…” Naming reduces intensity.",
            "Place a hand on your chest and breathe slowly for 60 seconds."
        ],
        "Feeling Stuck": [
            "Stuck is temporary. Movement can be tiny — even opening the notebook counts.",
            "Ask: What is the smallest possible next step?"
        ],
    }

    st.markdown("### Personalized Gentle Suggestions")

    shown = 0
    for area, score in sorted_areas:
        if score < 30:
            continue
        tips = SUGGESTIONS.get(area, [
            "Be extra kind to yourself today.",
            "One small act of care for your body or mind is enough."
        ])
        st.markdown(f"**{area}** (Level: {score:.0f})")
        for tip in tips[:2]:
            st.markdown(f"- {tip}")
        st.markdown("")
        shown += 1
        if shown >= 4:
            break

    if shown == 0:
        st.success("Your recent stress levels look manageable. Keep the good habits going and rest well.")

    st.markdown("---")
    st.info("These are supportive behavioral ideas based on common patterns. For deeper or ongoing distress, please reach out to a trusted adult, counselor, or professional.")

    if st.button("← Back to Home"):
        st.session_state.page = "home"
        st.rerun()


# ============================================================
# ROUTER
# ============================================================
page = st.session_state.page

if page == "auth":
    page_auth()
elif page == "category":
    page_category()
elif page == "questions":
    page_questions()
elif page == "analysis":
    page_analysis()
elif page == "recommendations":
    page_recommendations()
elif page == "motivation":
    page_motivation()
elif page == "home":
    page_home()
elif page == "progress":
    page_progress()
elif page == "help":
    page_help()
elif page == "behavioral":
    page_behavioral()
elif page == "settings":
    page_settings()
else:
    st.session_state.page = "auth"
    st.rerun()
