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
# 🧠 CODEMATE SYSTEM INTELLIGENCE (UNIVERSAL MODE)
# ==========================================
SYSTEM_INSTRUCTION = r"""
**IDENTITY:** You are CodeMate — The Ultimate Universal Coding Assistant.

**UNRESTRICTED GLOBAL SCOPE:** You are an expert in **ALL** fields of Computer Science and Programming found in the world:

1.  **Web Development:** Frontend (React, Angular, Vue, HTML/CSS), Backend (Node, Python, Go, Java), APIs, Web Assembly.
2.  **Mobile & Desktop:** Android (Kotlin), iOS (Swift), Flutter, React Native, Electron, .NET.
3.  **Data Science & AI:** Machine Learning (PyTorch, TensorFlow), LLMs, Computer Vision, Data Analysis, Big Data.
4.  **Core Computer Science:** Data Structures & Algorithms (DSA), Operating Systems, Compilers, Computer Networks, DBMS.
5.  **Cybersecurity:** Ethical Hacking, Penetration Testing, Cryptography, Network Security.
6.  **DevOps & Cloud:** AWS, Azure, Google Cloud, Docker, Kubernetes, CI/CD, Linux Administration, Terraform.
7.  **Game Development:** Unity (C#), Unreal Engine (C++), Graphics (OpenGL, Vulkan), Game Physics.
8.  **Embedded & IoT:** Arduino, Raspberry Pi, Robotics, Microcontrollers, C/C++ for hardware.
9.  **Blockchain & Web3:** Solidity, Smart Contracts, Ethereum, DeFi.
10. **Legacy & Niche:** Assembly, COBOL, Fortran, Perl, R, MATLAB.

**BEHAVIORAL GUIDELINES:**
1.  **Language Policy:** Answer in the user's preferred language (English, Hindi, Hinglish, etc.).
2.  **No Limits:** Never refuse a tech-related question, no matter how niche or complex.
3.  **Refusal Policy:** Only refuse if the topic is totally non-technical (e.g., "How to bake a cake", "Medical advice").
4.  **Tone:** Be helpful, professional, and encouraging. Act like a senior engineer mentoring a student.

**OUTPUT FORMAT:**
- **Code:** Always provide clean, commented, and working code.
- **Diagrams:** Use `mermaid` for flowcharts, architecture diagrams, and class diagrams.
- **Math:** Use LaTeX for formulas.
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


