"""
TASK 4b — Cross-Platform Chatbot: Console/CLI Simulation
Simulates the chatbot behavior on WhatsApp/Mobile via terminal (rich UI).
Run: python task4b_console_chatbot.py
"""

import time
import sys
import re
import os
from datetime import datetime


# ─────────────────────────────────────────────
# ANSI COLORS & STYLES
# ─────────────────────────────────────────────
class C:
    RESET  = "\033[0m"
    BOLD   = "\033[1m"
    DIM    = "\033[2m"
    GREEN  = "\033[92m"
    BLUE   = "\033[94m"
    YELLOW = "\033[93m"
    RED    = "\033[91m"
    CYAN   = "\033[96m"
    WHITE  = "\033[97m"
    GRAY   = "\033[90m"
    BG_BOT = "\033[48;5;236m"   # dark gray bg for bot messages
    BG_USR = "\033[48;5;27m"    # blue bg for user messages
    BG_WARN= "\033[48;5;130m"   # orange bg for warnings

def clear(): os.system('cls' if os.name == 'nt' else 'clear')

def ts(): return datetime.now().strftime("%I:%M %p")

def cprint(text, color=C.WHITE, end="\n"):
    print(f"{color}{text}{C.RESET}", end=end)


# ─────────────────────────────────────────────
# PLATFORM HEADER
# ─────────────────────────────────────────────

PLATFORMS = {
    "1": ("🌐 Web App",       "Browser-based chatbot simulation"),
    "2": ("📱 Mobile App",    "WhatsApp-style mobile simulation"),
    "3": ("💬 WhatsApp",      "WhatsApp Business bot simulation"),
}


def print_header(platform_name, platform_desc):
    width = 60
    print()
    cprint("─" * width, C.GRAY)
    cprint(f"  🎓  COLLEGE CHATBOT  —  {platform_name}", C.BOLD + C.CYAN)
    cprint(f"  {platform_desc}", C.GRAY)
    cprint("─" * width, C.GRAY)
    cprint(f"  {C.GREEN}● Online{C.RESET}{C.GRAY}  |  College Student Assistant  |  {ts()}", C.GRAY)
    cprint("─" * width, C.GRAY)
    print()


def print_bot_bubble(text, tag=None):
    """Prints a bot message bubble."""
    lines = text.split("\n")
    width = 58

    tag_str = ""
    if tag == "advisor":
        tag_str = f"{C.YELLOW}[→ ADVISOR]{C.RESET} "
    elif tag == "warning":
        tag_str = f"{C.RED}[⚠ OOS]{C.RESET} "

    cprint(f"  {C.GRAY}🎓 Bot  {ts()}{C.RESET}")
    for i, line in enumerate(lines):
        prefix = "  " if i > 0 else "  "
        padded = line[:width]
        if i == 0 and tag_str:
            cprint(f"{prefix}{C.BG_BOT} {tag_str}{padded} {C.RESET}")
        else:
            cprint(f"{prefix}{C.BG_BOT} {C.WHITE}{padded}{C.RESET}{C.BG_BOT} {C.RESET}")
    print()


def print_user_bubble(text):
    """Prints a user message bubble (right-aligned feel)."""
    width = 58
    cprint(f"                        {C.GRAY}You  {ts()}{C.RESET}")
    for line in text.split("\n"):
        cprint(f"        {C.BG_USR} {C.WHITE}{line[:width]} {C.RESET}")
    print()


def typing_animation(duration=1.0):
    frames = ["⠙","⠹","⠸","⠼","⠴","⠦","⠧","⠇","⠏"]
    end_time = time.time() + duration
    i = 0
    while time.time() < end_time:
        sys.stdout.write(f"\r  {C.GRAY}🎓 Bot is typing... {frames[i % len(frames)]}{C.RESET}  ")
        sys.stdout.flush()
        time.sleep(0.1)
        i += 1
    sys.stdout.write("\r" + " " * 40 + "\r")
    sys.stdout.flush()


def print_divider():
    cprint("  " + "─" * 54, C.GRAY)


def print_suggestions(suggestions):
    cprint(f"  {C.GRAY}Suggestions:{C.RESET}", C.GRAY)
    for s in suggestions:
        cprint(f"    {C.CYAN}▸ {s}{C.RESET}")
    print()


def print_advisor_link():
    cprint(f"  {C.YELLOW}┌─────────────────────────────────────┐{C.RESET}")
    cprint(f"  {C.YELLOW}│ 📧  advisor@college.edu             │{C.RESET}")
    cprint(f"  {C.YELLOW}│ 🏢  Room 101, Admin Block, 9AM–5PM  │{C.RESET}")
    cprint(f"  {C.YELLOW}│ 🌐  college.edu/advisor-chat         │{C.RESET}")
    cprint(f"  {C.YELLOW}└─────────────────────────────────────┘{C.RESET}")
    print()


# ─────────────────────────────────────────────
# CORE BOT LOGIC (same as web version)
# ─────────────────────────────────────────────

KB_EXAM = {
    ("CS","5"):"CS Semester 5 exams start on 15th November 2024.",
    ("CS","3"):"CS Semester 3 exams scheduled from 10th November 2024.",
    ("BCA","3"):"BCA 3rd semester exams begin on 12th November 2024.",
    ("IT","5"):"IT Semester 5 exams start on 14th November 2024.",
    ("ECE","4"):"ECE 4th semester exams start on 18th November 2024.",
}
KB_TIMETABLE = {
    ("CS","5"):"CS Sem 5: Mon/Wed/Fri — Theory | Tue/Thu — Labs.",
    ("BCA","3"):"BCA Sem 3: Mon/Wed/Fri theory, Tue/Thu practicals.",
}
KB_RESULT = {
    ("CS","4"):"CS Semester 4 results declared on 20th September 2024.",
    ("BCA","2"):"BCA Sem 2 results are on the university portal.",
}

ORDINALS={"first":"1","second":"2","third":"3","fourth":"4","fifth":"5","sixth":"6",
           "1st":"1","2nd":"2","3rd":"3","4th":"4","5th":"5","6th":"6"}
DEPT_MAP={"cs":"CS","cse":"CS","it":"IT","bca":"BCA","ece":"ECE","eee":"EEE","me":"ME","ai":"AI"}

class ConvState:
    def __init__(self): self.dept=None; self.sem=None; self.intent=None; self.turns=0

def detect_intent(t):
    t=t.lower()
    if re.search(r'exam|test|examination|when is',t): return "exam"
    if re.search(r'timetable|schedule|class time',t): return "timetable"
    if re.search(r'result|marks|grade|score',t): return "result"
    if re.search(r'syllabus|topics|curriculum',t): return "syllabus"
    if re.search(r'fee|payment',t): return "fee"
    if re.search(r'hi|hello|hey',t): return "greet"
    if re.search(r'advisor|contact|human',t): return "advisor"
    return None

def extract_dept(t):
    l=t.lower()
    for k,v in DEPT_MAP.items():
        if k in l: return v
    return None

def extract_sem(t):
    l=t.lower()
    for w,n in ORDINALS.items():
        if w in l: return n
    m=re.search(r'sem(?:ester)?\s*(\d)',l)
    if m: return m.group(1)
    return None

def process(text, state):
    intent = detect_intent(text) or state.intent
    dept   = extract_dept(text)   or state.dept
    sem    = extract_sem(text)    or state.sem
    state.turns += 1

    if intent: state.intent = intent
    if dept:   state.dept   = dept
    if sem:    state.sem    = sem

    sensitive = re.search(r'ragging|harassment|mental|counselor|abuse',text,re.I)
    oos       = re.search(r'weather|cricket|movie|joke|bitcoin|ipl|netflix',text,re.I)

    if sensitive:
        return "This seems like a sensitive matter. Please reach out to our student welfare advisor directly.", "advisor", ["📧 Email Advisor", "🏢 Visit Office"]
    if oos:
        return "That's outside my scope. I can help with college queries.", "warning", ["📅 Exams","📋 Timetable","📊 Results"]
    if state.intent == "greet":
        return "Hello! 👋 I'm your college assistant. Ask about exams, timetables, results, or fees.", None, ["📅 Exams","📋 Timetable"]
    if state.intent == "advisor":
        return "Let me connect you with a human advisor.", "advisor", []
    if state.intent == "fee":
        return "Visit the Accounts Department or check the student portal for fee details.", None, []
    if not state.dept:
        return "Which department? (e.g., CS, BCA, IT, ECE)", None, ["CS","BCA","IT","ECE"]
    if not state.sem:
        return "Which semester? (e.g., 3rd sem, sem 5)", None, ["Sem 3","Sem 5","Sem 7"]

    key = (state.dept, state.sem)
    db = {"exam": KB_EXAM, "timetable": KB_TIMETABLE, "result": KB_RESULT}
    ans = db.get(state.intent, {}).get(key)
    if ans:
        return ans, None, []
    return f"No data for {state.dept} Sem {state.sem}. Check the notice board.", "warning", []


# ─────────────────────────────────────────────
# PLATFORM RUNNER
# ─────────────────────────────────────────────

def run_chatbot(platform_key):
    pname, pdesc = PLATFORMS[platform_key]
    clear()
    print_header(pname, pdesc)

    state = ConvState()

    # Welcome
    typing_animation(0.8)
    print_bot_bubble("Hello! 👋 I'm your college assistant bot.\nI can help with exams, timetables, results, syllabus & fees.")
    print_suggestions(["📅 Exam Schedule", "📋 Timetable", "📊 Results", "📚 Syllabus"])

    while True:
        try:
            cprint(f"  {C.GRAY}You ▸ {C.RESET}", end="")
            user_input = input().strip()
        except (EOFError, KeyboardInterrupt):
            print()
            cprint("\n  [Session ended]", C.GRAY)
            break

        if not user_input: continue
        if user_input.lower() in ("quit","exit","bye"):
            typing_animation(0.5)
            print_bot_bubble("Goodbye! Have a great day! 👋")
            break
        if user_input.lower() == "reset":
            state = ConvState()
            cprint("  [Conversation reset ✓]", C.YELLOW)
            continue

        print_user_bubble(user_input)

        typing_animation(0.7 + len(user_input) * 0.005)

        response, tag, suggestions = process(user_input, state)
        print_bot_bubble(response, tag)

        if tag == "advisor":
            print_advisor_link()
        if suggestions:
            print_suggestions(suggestions)

        print_divider()


# ─────────────────────────────────────────────
# ENTRY POINT
# ─────────────────────────────────────────────

def main():
    clear()
    cprint("\n  ╔══════════════════════════════════════════╗", C.CYAN)
    cprint("  ║   TASK 4 — CROSS-PLATFORM CHATBOT SIM   ║", C.CYAN + C.BOLD)
    cprint("  ╚══════════════════════════════════════════╝\n", C.CYAN)

    cprint("  Choose platform to simulate:", C.WHITE)
    for k, (name, desc) in PLATFORMS.items():
        cprint(f"    [{k}] {name}  —  {desc}", C.GRAY)
    print()

    choice = input("  Enter choice (1/2/3): ").strip()
    if choice not in PLATFORMS:
        cprint("  Invalid choice. Defaulting to Web.", C.YELLOW)
        choice = "1"

    run_chatbot(choice)


if __name__ == "__main__":
    main()
