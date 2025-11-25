import os
import google.generativeai as genai
from flask import Flask, request, jsonify, render_template
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

# ==========================================
# 🔑 API KEY SETUP
# ==========================================
# Retrieve API Key from environment variable
MY_API_KEY = os.environ.get("GOOGLE_API_KEY")

if not MY_API_KEY:
    print("⚠️ WARNING: GOOGLE_API_KEY environment variable not set. The app might crash if it tries to generate content.")

genai.configure(api_key=MY_API_KEY)

# ==========================================
# 🧠 CODEMATE SYSTEM INTELLIGENCE
# ==========================================
# ==========================================
# 🧠 CODEMATE SYSTEM INTELLIGENCE (UPDATED)
# ==========================================
SYSTEM_INSTRUCTION = r"""
**IDENTITY:** You are CodeMate — a specialized Data Structures & Algorithms (DSA) and Programming Assistant.

**STRICT SCOPE:** You are designed to ONLY answer questions related to:
1. Data Structures (Arrays, Linked Lists, Trees, Graphs, Stacks, Queues, etc.)
2. Algorithms (Sorting, Searching, Dynamic Programming, Greedy, Recursion, etc.)
3. Code Debugging & Optimization.
4. Computer Science Core concepts (relevant to coding interviews).
5. Programming Language Syntax, Semantics, and Tutorials (C++, Python, Java, JavaScript, etc.).  <-- ADDED THIS

**BEHAVIORAL GUIDELINES:**
1. **Language:** Respond in the language used by the user (default to English). If the user speaks Hindi, reply in Hindi (or Hinglish).
2. **Refusal Policy:** - If the user asks non-coding questions (e.g., "What is the weather?", "Cooking recipes", "Politics"), politely REFUSE.
   - Refusal message: "I am CodeMate, a specialized DSA assistant. I can only help you with programming and algorithm problems."
   - **EXCEPTION:** If the request is about learning a programming language (e.g., "Teach me C++"), DO NOT refuse. Start a structured tutorial.
3. **Teaching Style:** - Explain concepts step-by-step.
   - **ALWAYS** provide Time and Space complexity for algorithms.
   - Use `mermaid` diagram code blocks for visual topics (Trees, Graphs, Linked Lists).
   - Use LaTeX for mathematical notation (e.g., $O(n \log n)$).

**CODE GENERATION:**
- Default language: **C++** (unless the user requests Python, Java, or JS).
- Write clean, commented, and efficient code.
"""

model = genai.GenerativeModel(
    model_name="gemini-2.0-flash", 
    system_instruction=SYSTEM_INSTRUCTION
)

@app.route('/')
def index():
    # Renders the frontend HTML file
    return render_template('index.html')

@app.route('/chat', methods=['POST'])
def chat():
    try:
        # --- DEBUG LOGGING (Visible in Terminal) ---
        print("\n📩 --- NEW MESSAGE RECEIVED ---")
        user_message = request.form.get('message', '')
        file = request.files.get('file')
        
        print(f"User Text: {user_message[:50]}..." if user_message else "User Text: [Empty]")
        if file:
            print(f"File Attached: {file.filename} ({file.content_type})")

        # Validate Input
        if not user_message and not file:
            return jsonify({"error": "Please provide a message or a file."}), 400

        content_parts = []
        
        # 1. Add Text to Prompt
        if user_message: 
            content_parts.append(user_message)
        
        # 2. Add File Data to Prompt (Safe Handling)
        if file:
            mime_type = file.content_type
            file_data = file.read()
            
            # Category A: Text-based files (Code, JSON, TXT)
            if mime_type.startswith("text/") or mime_type in ["application/json", "application/javascript", "application/xml"]:
                try:
                    text_content = file_data.decode('utf-8', errors='ignore')
                    content_parts.append(f"\n[Attached File Content - {file.filename}]:\n{text_content}")
                except Exception as e:
                    print(f"❌ File Decode Error: {e}")
            
            # Category B: Images (Diagrams, Screenshots)
            elif mime_type.startswith("image/"):
                content_parts.append({"mime_type": mime_type, "data": file_data})
            
            # Category C: Unsupported binary files (PDFs, ZIPs) - Prevent crash
            else:
                print(f"⚠️ Unsupported file type: {mime_type}")
                content_parts.append(f"[System Note]: User attached '{file.filename}' but it is a {mime_type} file which I cannot read directly. Please ask the user to paste the code text instead.")

        # 3. Generate Response from Gemini
        print("🤖 Generating AI Response...")
        response = model.generate_content(content_parts)
        print("✅ Response Sent Successfully!")

        return jsonify({"response": response.text})

    except Exception as e:
        print(f"🔥 CRITICAL SERVER ERROR: {e}")
        return jsonify({"error": f"Server Error: {str(e)}"}), 500

if __name__ == '__main__':
    app.run(debug=True, port=5000)

