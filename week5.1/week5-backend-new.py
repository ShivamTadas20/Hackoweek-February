# ============================================================
# TASK 5 — Logging, Analysis & Improvement Proposals (Backend)
# Symbiosis College of Technology, Nagpur
# B.Tech CS 4th Sem | AI/ML & Data Science
# Time estimate: ~2 hours (final task — ties everything together)
# ============================================================
#
# WHAT IS HAPPENING:
#   All previous tasks write logs to queries_log.json.
#   Task 5 is the ANALYSIS layer — it reads those logs,
#   labels them, finds patterns, and proposes improvements.
#
#   This is what you'd present to your professor:
#   "Based on observed interactions, here are improvements."
#
# WHAT WE ARE DOING:
#   1. Read all logs from tasks 1-4
#   2. Compute: strategy stats, platform stats, top unanswered queries
#   3. Auto-label unknown queries into categories
#   4. Generate improvement proposals (new intents, new FAQs)
#   5. Export as CSV + JSON report
#
# HOW TO RUN:
#   pip install flask flask-cors
#   python task5_backend.py
#   (This is the FINAL unified backend — runs all tasks)
# ============================================================

from flask import Flask, request, jsonify, Response
from flask_cors import CORS
import re, json, os, csv, io
from datetime import datetime
from collections import Counter

app = Flask(__name__)
CORS(app)

LOG_FILE = "queries_log.json"

COLLEGE_INFO = {
    "name": "Symbiosis College of Technology, Nagpur",
    "fees": 290000, "specialization_fees": 25000,
    "courses": {
        "CS301": "Data Structures & Algorithms", "AI201": "Introduction to AI",
        "DS301": "Data Science Fundamentals", "ML401": "Machine Learning",
        "CS401": "Operating Systems"
    }
}

# ---- Log reader ----

def load_logs():
    if not os.path.exists(LOG_FILE):
        return []
    with open(LOG_FILE) as f:
        try: return json.load(f)
        except: return []


def save_log(entry):
    logs = load_logs()
    logs.append(entry)
    with open(LOG_FILE, "w") as f:
        json.dump(logs, f, indent=2)


# ---- Labeling Engine ----

LABEL_PATTERNS = {
    "exam_query":    r'\b(exam|test|paper|schedule)\b',
    "fee_query":     r'\b(fee|fees|cost|charges|payment)\b',
    "course_query":  r'\b(course|subject|syllabus|what is)\b',
    "document_req":  r'\b(bonafide|certificate|id card|receipt|admit card)\b',
    "spec_query":    r'\b(spec(?:ialization)?|ai|ml|data science)\b',
    "out_of_scope":  r'\b(weather|cricket|restaurant|movie|recipe|joke)\b',
    "general":       r'.*'
}

def label_query(text):
    for label, pattern in LABEL_PATTERNS.items():
        if re.search(pattern, text, re.IGNORECASE):
            return label
    return "uncategorized"


# ---- Analysis Engine ----

def analyze_logs(logs):
    if not logs:
        return {}

    total = len(logs)
    strategy_counts = Counter(l.get("strategy", "answered") for l in logs)
    platform_counts = Counter(l.get("platform", "web") for l in logs)
    label_counts = Counter(label_query(l.get("question", "")) for l in logs)

    # Find most common unanswered / escalation questions
    unclear_qs = [l["question"] for l in logs if l.get("strategy") in ("clarify", "suggest", "escalate")]
    escalated_qs = [l["question"] for l in logs if l.get("strategy") == "escalate"]

    # Top 5 most common question types
    top_labels = label_counts.most_common(5)

    return {
        "total": total,
        "strategy_counts": dict(strategy_counts),
        "platform_counts": dict(platform_counts),
        "label_counts": dict(label_counts),
        "top_labels": top_labels,
        "unclear_count": len(unclear_qs),
        "escalated_count": len(escalated_qs),
        "sample_unclear": unclear_qs[:5],
        "sample_escalated": escalated_qs[:3]
    }


def generate_improvement_proposals(analysis):
    """Based on log analysis, suggest improvements."""
    proposals = []

    # High escalation rate → add document FAQ
    if analysis.get("escalated_count", 0) >= 2:
        proposals.append({
            "type": "new_intent",
            "priority": "HIGH",
            "title": "Document Request Handler",
            "description": (
                "Multiple escalations for bonafide/certificate/ID card. "
                "Add a dedicated intent with direct links to the admin portal."
            )
        })

    # High clarify rate → improve entity extraction
    strats = analysis.get("strategy_counts", {})
    if strats.get("clarify", 0) > strats.get("answered", 0) * 0.3:
        proposals.append({
            "type": "better_patterns",
            "priority": "MEDIUM",
            "title": "Improve Vague Question Handling",
            "description": (
                "Many clarify-strategy triggers could be pre-answered "
                "if we map semester numbers to exam schedules directly."
            )
        })

    # High spec queries → expand knowledge base
    labels = analysis.get("label_counts", {})
    if labels.get("spec_query", 0) >= 1:
        proposals.append({
            "type": "new_faq",
            "priority": "MEDIUM",
            "title": "Expand Specialization FAQ",
            "description": (
                "Students ask about AI/ML & Data Science subjects frequently. "
                "Add full semester-wise subject list for specialization tracks."
            )
        })

    # General fallback
    proposals.append({
        "type": "log_quality",
        "priority": "LOW",
        "title": "Label All Unknown Queries",
        "description": (
            "Unrecognized queries should be tagged for future intent training. "
            "Build a simple labeling UI for weekly review."
        )
    })

    return proposals


# ---- Routes ----

@app.route("/api/logs", methods=["GET"])
def get_logs():
    logs = load_logs()
    # Add labels to each log entry
    for log in logs:
        if "label" not in log:
            log["label"] = label_query(log.get("question", ""))
    return jsonify(logs)


@app.route("/api/analysis", methods=["GET"])
def analysis():
    """Full analysis report of all interactions."""
    logs = load_logs()
    result = analyze_logs(logs)
    proposals = generate_improvement_proposals(result)
    return jsonify({
        "analysis": result,
        "improvement_proposals": proposals,
        "generated_at": datetime.now().isoformat()
    })


@app.route("/api/strategies", methods=["GET"])
def strategies():
    logs = load_logs()
    counts = Counter(l.get("strategy", "answered") for l in logs)
    return jsonify(dict(counts))


@app.route("/api/platform-stats", methods=["GET"])
def platform_stats():
    logs = load_logs()
    counts = Counter(l.get("platform", "web") for l in logs)
    return jsonify(dict(counts))


@app.route("/api/export/csv", methods=["GET"])
def export_csv():
    """Export all logs as CSV file — download from browser."""
    logs = load_logs()
    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(["timestamp", "platform", "session_id", "question", "strategy", "label", "response"])
    for log in logs:
        writer.writerow([
            log.get("timestamp", ""),
            log.get("platform", "web"),
            log.get("session_id", ""),
            log.get("question", ""),
            log.get("strategy", "answered"),
            label_query(log.get("question", "")),
            log.get("response", "")
        ])
    return Response(
        output.getvalue(),
        mimetype="text/csv",
        headers={"Content-Disposition": "attachment; filename=scot_chatbot_logs.csv"}
    )


@app.route("/api/log", methods=["POST"])
def add_log():
    """Frontend can post a log entry directly."""
    data = request.get_json()
    if not data:
        return jsonify({"error": "No data"}), 400
    data["timestamp"] = datetime.now().isoformat()
    data["label"] = label_query(data.get("question", ""))
    save_log(data)
    return jsonify({"status": "saved"})


@app.route("/", methods=["GET"])
def health():
    logs = load_logs()
    return jsonify({
        "status": "running",
        "task": 5,
        "total_logs": len(logs),
        "routes": [
            "GET  /api/logs",
            "GET  /api/analysis",
            "GET  /api/strategies",
            "GET  /api/platform-stats",
            "GET  /api/export/csv",
            "POST /api/log"
        ]
    })


if __name__ == "__main__":
    print("=" * 55)
    print("TASK 5 — Final Backend: http://localhost:5000")
    print("This backend ties together ALL 5 tasks.")
    print()
    print("GET  /api/logs           -> all interaction logs")
    print("GET  /api/analysis       -> full log analysis + proposals")
    print("GET  /api/strategies     -> strategy distribution")
    print("GET  /api/platform-stats -> platform distribution")
    print("GET  /api/export/csv     -> download CSV report")
    print("POST /api/log            -> add new log entry")
    print("=" * 55)
    app.run(debug=True, port=5000)  