# ============================================
# AI DEBATE SERVER - GPT-5 MINI COMPATIBLE
# ============================================

from flask import Flask, request, jsonify
from flask_cors import CORS
from openai import OpenAI
import os
from dotenv import load_dotenv
import re
import time

# ============================================
# SETUP
# ============================================
load_dotenv()

app = Flask(__name__)
CORS(app)  # Allow requests from HTML file

# ============================================
# MODEL CONFIGURATION
# ============================================
# Available GPT-5 models:
# - gpt-5-nano (fastest)
# - gpt-5-mini (balanced)  ← we’re using this one
# - gpt-5 (standard)
# - gpt-5-pro (most capable)

DEBATE_MODEL = "gpt-5-mini"
MAX_TOKENS = 1200
RETRIES = 3

# Load API key
api_key = os.getenv("OPENAI_API_KEY")

if not api_key:
    api_key = "insert your api key here"  # temporary fallback

if not api_key or api_key == "sk-proj-YOUR-KEY-HERE":
    print("=" * 60)
    print("❌ ERROR: Missing or placeholder API key!")
    print("Fix: Add it to .env as OPENAI_API_KEY or directly above.")
    print("=" * 60)
    exit(1)
else:
    print(f"✅ API Key loaded (starts with: {api_key[:10]}...)")

client = OpenAI(api_key=api_key)

# ============================================
# FIXED MODEL CALL FUNCTION
# ============================================
def call_model(prompt: str) -> str:
    """Call GPT-5-mini (no temperature param allowed)."""
    last_err = None
    for attempt in range(1, RETRIES + 1):
        try:
            resp = client.responses.create(
                model=DEBATE_MODEL,
                input=prompt,
                #max_output_tokens=MAX_TOKENS
            )

            if hasattr(resp, "output_text") and resp.output_text:
                return resp.output_text.strip()
            elif hasattr(resp, "output") and len(resp.output) > 0:
                out = resp.output[0]
                if hasattr(out, "content") and out.content:
                    return out.content[0].text.strip()
            return str(resp)

        except Exception as e:
            last_err = e
            print(f"⚠️ Attempt {attempt} failed: {e}")
            time.sleep(min(2 ** (attempt - 1), 5))
    raise RuntimeError(f"OpenAI call failed after {RETRIES} attempts: {last_err}")

# ============================================
# PROMPTS
# ============================================
DEFAULT_PROMPTS = {
    "strategic_debate": """You are debating the {position} position on: "{topic}"

This is Round {round_num}. Previous arguments:
{context}

RULES:
1. Keep it BRIEF: 100-150 words MAX.
2. Each round must be STRONGER than the previous.
3. Use 1-2 POWERFUL, SPECIFIC pieces of evidence.
4. Be PUNCHY and IMPACTFUL.
5. Round 1: Establish position with strong facts.
6. Round 2+: DIRECTLY attack opponent’s weaknesses.
7. Later rounds: Go for the knockout — your strongest points.

Format: Start with your most powerful argument, back it with data, end with impact.
""",

    "opening_statement": """Opening statement for {position} on: "{topic}"

RULES:
1. 100-150 words MAX.
2. Start with your STRONGEST point.
3. Use 2-3 concrete pieces of evidence.
4. No fluff — every sentence must deliver impact.

Format:
- Opening punch (claim + evidence)
- Supporting strike (more data)
- Closing impact (why it matters)
""",

    "judge_round": """Evaluate these arguments on: "{topic}"

PRO: {pro_arg}

CON: {con_arg}

Rate 1–10 based on:
- Brevity + impact
- Evidence quality
- Engagement with opponent
- Strategic strength

Output format:
PRO: X/10
CON: X/10
Winner: [PRO/CON/TIE]
Reason: [short, specific explanation]
"""
}

prompts = DEFAULT_PROMPTS.copy()

# ============================================
# ROUTES
# ============================================

@app.route('/health', methods=['GET'])
def health():
    return jsonify({"status": "healthy", "message": "Debate server running"})

@app.route('/generate', methods=['POST'])
def generate():
    try:
        data = request.json
        prompt = data.get('prompt')
        if not prompt:
            return jsonify({"error": "No prompt provided"}), 400

        resp_text = call_model(prompt)
        return jsonify({'response': resp_text})
    except Exception as e:
        print(f"❌ Error in /generate: {e}")
        return jsonify({"error": str(e)}), 500


@app.route('/debate/argument', methods=['POST'])
def generate_argument():
    try:
        data = request.json
        topic = data.get('topic')
        position = data.get('position')
        round_num = data.get('round', 1)
        context = data.get('context', 'No previous arguments.')

        if round_num == 1:
            prompt_template = prompts['opening_statement']
            formatted_prompt = prompt_template.format(topic=topic, position=position)
        else:
            prompt_template = prompts['strategic_debate']
            formatted_prompt = prompt_template.format(
                topic=topic, position=position, round_num=round_num, context=context
            )

        full_prompt = f"""You are a master debater.
Be concise (100–150 words), aggressive, and factual.
Every line should be impactful.

{formatted_prompt}"""

        print(f"🧠 Generating {position.upper()} argument for round {round_num}...")
        argument = call_model(full_prompt)

        if not argument:
            argument = "[Error: Empty response from model]"

        print(f"✅ Generated {position.upper()} argument ({len(argument)} chars)")
        return jsonify({'argument': argument})

    except Exception as e:
        print(f"❌ Error in /debate/argument: {e}")
        return jsonify({"error": str(e)}), 500


@app.route('/debate/judge', methods=['POST'])
def judge_round():
    try:
        data = request.json
        topic = data.get('topic')
        pro_arg = data.get('pro_argument')
        con_arg = data.get('con_argument')

        formatted_prompt = prompts['judge_round'].format(
            topic=topic, pro_arg=pro_arg, con_arg=con_arg
        )

        full_prompt = f"""You are a concise debate judge.
Use clear 1-sentence reasoning.
{formatted_prompt}"""

        print("⚖️ Judging round...")
        judgment_text = call_model(full_prompt)

        pro_match = re.search(r'PRO[:\s]+(\d+)', judgment_text, re.IGNORECASE)
        con_match = re.search(r'CON[:\s]+(\d+)', judgment_text, re.IGNORECASE)

        pro_score = int(pro_match.group(1)) if pro_match else 5
        con_score = int(con_match.group(1)) if con_match else 5

        print(f"✅ Judged: PRO {pro_score}/10 | CON {con_score}/10")
        return jsonify({
            'pro_score': pro_score,
            'con_score': con_score,
            'feedback': judgment_text
        })

    except Exception as e:
        print(f"❌ Error in /debate/judge: {e}")
        return jsonify({"error": str(e)}), 500


@app.route('/prompts', methods=['GET'])
def get_prompts():
    return jsonify(prompts)

@app.route('/prompts', methods=['POST'])
def add_prompt():
    try:
        data = request.json
        name = data.get('name')
        template = data.get('template')
        if not name or not template:
            return jsonify({"error": "Name and template required"}), 400

        prompts[name] = template
        print(f"✅ Added new prompt: {name}")
        return jsonify({"message": f"Prompt '{name}' added", "prompts": prompts})

    except Exception as e:
        print(f"❌ Error in /prompts POST: {e}")
        return jsonify({"error": str(e)}), 500

@app.route('/prompts/<name>', methods=['DELETE'])
def delete_prompt(name):
    if name in prompts:
        del prompts[name]
        print(f"🗑️ Deleted prompt: {name}")
        return jsonify({"message": f"Prompt '{name}' deleted"})
    return jsonify({"error": "Prompt not found"}), 404


# ============================================
# MAIN
# ============================================
if __name__ == '__main__':
    print("\n" + "=" * 60)
    print("🤖 AI DEBATE SERVER (GPT-5-MINI MODE)")
    print("=" * 60)
    print(f"Model: {DEBATE_MODEL}")
    print(f"Server URL: http://localhost:5000")
    print("Status: Ready to accept debate requests!")
    print("=" * 60 + "\n")

    app.run(port=5000, debug=True)

