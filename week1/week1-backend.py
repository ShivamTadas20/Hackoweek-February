from flask import Flask, request, jsonify
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

college_info = {
    "college_name": "Symbiosis College of Technology, Nagpur",
    "degree": "BTech Computer Science",
    "semester": "4th Sem",
    "fees": "2 lakh 90 thousand",
    "specialization": "AI ML and Data Science",
    "specialization_fee": "25 thousand"
}

@app.route('/chat', methods=['POST'])
def chat():
    user_question = request.json['question'].lower()

    if "college" in user_question or "sct" in user_question:
        reply = f"You are studying in {college_info['college_name']}."
    elif "semester" in user_question or "sem" in user_question:
        reply = f"You are currently in {college_info['semester']}."
    elif "fee" in user_question:
        reply = f"The college fees is {college_info['fees']}."
    elif "specialization" in user_question:
        reply = f"Your specialization is {college_info['specialization']} and extra fees is {college_info['specialization_fee']}."
    elif "degree" in user_question or "course" in user_question:
        reply = f"You are studying {college_info['degree']}."
    else:
        reply = "Sorry, I could not understand your question."

    return jsonify({"reply": reply})

if __name__ == '__main__':
    app.run(debug=True)