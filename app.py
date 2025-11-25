import os
import google.generativeai as genai
from flask import Flask, request, jsonify, render_template
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

# ==========================================
# 🔑 API KEY SETUP (Secure way)
# ==========================================
# API Key ab environment variable se aayegi
MY_API_KEY = os.environ.get("GOOGLE_API_KEY")

if not MY_API_KEY:
    print("Warning: GOOGLE_API_KEY not set!")

genai.configure(api_key=MY_API_KEY)

# SYSTEM_INSTRUCTION wahi rahega jo aapne diya tha...
SYSTEM_INSTRUCTION = r"""
**IDENTITY:** You are CodeMate — a friendly, intelligent, highly reliable programming and DSA assistant.
... (baaki instruction same rakhein) ...
"""

model = genai.GenerativeModel(
    model_name="gemini-2.0-flash", 
    system_instruction=SYSTEM_INSTRUCTION
)

# 👇 Ye naya route hai Frontend serve karne ke liye
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/chat', methods=['POST'])
def chat():
    # ... (Baaki code same rahega) ...
    try:
        user_message = request.form.get('message', '')
        file = request.files.get('file')

        if not user_message and not file:
            return jsonify({"error": "Empty input"}), 400

        content_parts = []
        if user_message: content_parts.append(user_message)
        
        if file:
            mime_type = file.content_type
            file_data = file.read()
            if "text" in mime_type or "json" in mime_type:
                content_parts.append(f"\n[Attached File]:\n{file_data.decode('utf-8')}")
            elif "image" in mime_type:
                content_parts.append({"mime_type": mime_type, "data": file_data})

        response = model.generate_content(content_parts)
        return jsonify({"response": response.text})

    except Exception as e:
        print(f"❌ Error: {e}")
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True, port=5000)