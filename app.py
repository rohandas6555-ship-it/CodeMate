import os
import google.generativeai as genai
from flask import Flask, request, jsonify, render_template
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

# ==========================================
# 🔑 API KEY SETUP
# ==========================================
# Make sure your .env or environment variable is set
MY_API_KEY = os.environ.get("GOOGLE_API_KEY")

if not MY_API_KEY:
    print("⚠️ WARNING: GOOGLE_API_KEY environment variable not set.")

genai.configure(api_key=MY_API_KEY)

# ==========================================
# 🧠 CODEMATE SYSTEM INTELLIGENCE (Optimized for New UI)
# ==========================================
SYSTEM_INSTRUCTION = """
**IDENTITY:** You are CodeMate, an expert universal coding assistant.

**CAPABILITIES:**
1.  **Expertise:** Web Dev, Mobile, AI/ML, DSA, DevOps, CyberSecurity, IoT, and Legacy Systems.
2.  **Tone:** Professional, clear, concise, and helpful. Guide the user like a Senior Engineer.

**RESPONSE FORMATTING RULES (CRITICAL):**
1.  **Markdown:** Use standard GitHub Flavored Markdown. Use bolding for emphasis.
2.  **Code:** ALWAYS use code blocks with language tags (e.g., ```python, ```javascript).
3.  **Diagrams:** If a concept is complex (like System Design, Flowcharts, Database Relations), YOU MUST generate a Mermaid diagram.
    - Use code blocks tagged with `mermaid`.
    - Example:
      ```mermaid
      graph TD;
      A[Start] --> B{Is Valid?};
      B -- Yes --> C[Process];
      B -- No --> D[Error];
      ```
4.  **Math:** Use LaTeX formatting for math equations enclosed in double dollar signs (e.g., $$ E = mc^2 $$) or single for inline (e.g., $ x^2 $).
5.  **Directness:** Do not use conversational filler ("Here is the code you asked for"). Go straight to the solution unless explanation is needed.
"""

# Note: If 'gemini-2.0-flash' gives errors, switch to 'gemini-1.5-flash' or 'gemini-1.5-pro'
model = genai.GenerativeModel(
    model_name="gemini-2.0-flash", 
    system_instruction=SYSTEM_INSTRUCTION
)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/chat', methods=['POST'])
def chat():
    try:
        user_message = request.form.get('message', '')
        file = request.files.get('file')

        content_parts = []

        # 1. Add Text Message
        if user_message:
            content_parts.append(user_message)

        # 2. Smart File Handling
        if file:
            mime_type = file.content_type
            file_data = file.read()
            filename = file.filename

            # CASE A: Images (Pass directly to Vision Model)
            if mime_type.startswith("image/"):
                content_parts.append({"mime_type": mime_type, "data": file_data})
                content_parts.append("\n[System: User attached an image. Analyze it.]")
            
            # CASE B: Code/Text Files (Try to decode as text)
            else:
                try:
                    # Try decoding as UTF-8 (covers .py, .js, .html, .txt, .md, etc.)
                    text_content = file_data.decode('utf-8')
                    prompt_augmentation = f"\n\n--- ATTACHED FILE: {filename} ---\n{text_content}\n--- END FILE ---\n"
                    content_parts.append(prompt_augmentation)
                except UnicodeDecodeError:
                    # Fallback for binary files we can't read
                    return jsonify({"error": f"Cannot read binary file '{filename}'. Please upload code or images only."}), 400

        # Validate that we have something to send
        if not content_parts:
            return jsonify({"error": "Empty message."}), 400

        # 3. Generate Response
        response = model.generate_content(content_parts)
        
        return jsonify({"response": response.text})

    except Exception as e:
        print(f"Server Error: {e}")
        return jsonify({"error": f"Internal Server Error: {str(e)}"}), 500

if __name__ == '__main__':
    # Ensure 'templates' folder exists for index.html
    if not os.path.exists('templates'):
        os.makedirs('templates')
        print("📁 Created 'templates' folder. Please move index.html inside it.")
    
    app.run(debug=True, port=5000)
