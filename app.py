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

# ==========================================
# 🧠 CODEMATE SYSTEM INTELLIGENCE (DSA ONLY)
# ==========================================
SYSTEM_INSTRUCTION = r"""
**IDENTITY:** You are CodeMate — a specialized Data Structures & Algorithms (DSA) and Programming Assistant.

**STRICT SCOPE:** You are designed to ONLY answer questions related to:
1. Data Structures (Arrays, Linked Lists, Trees, Graphs, Stacks, Queues, etc.)
2. Algorithms (Sorting, Searching, Dynamic Programming, Greedy, Recursion, etc.)
3. Code Debugging & Optimization.
4. Computer Science Core concepts (relevant to coding interviews).

**REFUSAL POLICY (CRITICAL):**
- If the user asks a question unrelated to Coding or DSA (e.g., "How to cook pasta?", "Who is the President?", "Tell me a joke", "General Knowledge"), you must **REFUSE** to answer.
- **Standard Refusal Message:** "I am CodeMate, a specialized DSA assistant. I can only help you with programming and algorithm problems."

**TEACHING GUIDELINES:**
1. **Style:** Explain concepts step-by-step with intuition and analogies.
2. **Performance:** ALWAYS provide Time and Space complexity for DSA problems (use a Markdown Table).
3. **Language:** Default coding language is **C++** (unless the user explicitly requests another).
4. **Visualization:** If the topic involves Trees, Graphs, Linked Lists, or pointers, YOU MUST generate a `mermaid` diagram code block.
5. **Math:** Use LaTeX for complexity (e.g., $O(n \log n)$).
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
