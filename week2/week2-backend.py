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

last_topic = ""

@app.route('/chat', methods=['POST'])
def chat():
    global last_topic
    user_question = request.json['question'].lower()

    if "specialization" in user_question:
        last_topic = "specialization"
        reply = f"Your specialization is {college_info['specialization']}."
    elif "fee" in user_question and "specialization" in user_question:
        last_topic = "specialization_fee"
        reply = f"Additional fee for specialization is {college_info['specialization_fee']}."
    elif "its fee" in user_question or "its extra fee" in user_question:
        if last_topic == "specialization":
            reply = f"Additional fee for specialization is {college_info['specialization_fee']}."
        else:
            reply = "Please specify what you are asking about."
    elif "semester" in user_question or "sem" in user_question:
        last_topic = "semester"
        reply = f"You are in {college_info['semester']}."
    elif "college" in user_question:
        last_topic = "college"
        reply = f"You are studying in {college_info['college_name']}."
    elif "fee" in user_question:
        last_topic = "fees"
        reply = f"Your college fee is {college_info['fees']}."
    else:
        reply = "Sorry, I could not understand your question."

    return jsonify({"reply": reply})

if __name__ == '__main__':
    app.run(debug=True)