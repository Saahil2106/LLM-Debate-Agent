from flask import Flask, request, jsonify
from flask_cors import CORS
from openai import OpenAI
import os
from dotenv import load_dotenv
import re

# Load environment variables
load_dotenv()

app = Flask(__name__)
CORS(app)  # Allow requests from HTML file

# ============================================
# API KEY CONFIGURATION - EDIT THIS SECTION
# ============================================
# Method 1: Try to load from .env file
api_key = os.getenv("OPENAI_API_KEY")

# Method 2: Hardcoded API key (TEMPORARY - After testing, move to .env file!)
if not api_key:
    api_key = "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"

# Validation
if not api_key:
    print("=" * 60)
    print("❌ ERROR: No API key found!")
    print("=" * 60)
    print("Fix options:")
    print("1. Create a .env file in D:\\Capstone\\ with:")
    print("   OPENAI_API_KEY=sk-proj-your-key-here")
    print("")
    print("2. OR edit this file (line 20) and uncomment:")
    print('   api_key = "sk-proj-your-key-here"')
    print("=" * 60)
    exit(1)
elif api_key == "sk-proj-YOUR-ACTUAL-API-KEY-HERE":
    print("=" * 60)
    print("❌ ERROR: Please replace the placeholder API key!")
    print("=" * 60)
    print("Edit line 20 in debate_server.py with your real key")
    print("=" * 60)
    exit(1)
else:
    print(f"✅ API Key loaded successfully (starts with: {api_key[:10]}...)")

client = OpenAI(api_key=api_key)

# Default prompts
DEFAULT_PROMPTS = {
    "strategic_debate": """You are debating the {position} position on: "{topic}"

This is Round {round_num}. Previous arguments:
{context}

CRITICAL RULES:
1. Keep it BRIEF: 100-150 words MAX (about 2-3 short paragraphs)
2. Each round must be STRONGER than the previous - escalate intensity
3. Use 1-2 POWERFUL, SPECIFIC pieces of evidence (real statistics, studies, or examples)
4. Be PUNCHY and IMPACTFUL - every sentence must hit hard
5. Round 1: Establish position with strong facts
6. Round 2+: DIRECTLY attack opponent's weaknesses + add new devastating evidence
7. Later rounds: Go for the knockout - use your strongest, most irrefutable points

Format: Lead with your strongest point. Back it with concrete evidence. End with impact.

{position} position, Round {round_num} - make it count!""",

    "opening_statement": """Opening statement for {position} on: "{topic}"

RULES:
1. 100-150 words MAX (2-3 short paragraphs)
2. Start with your STRONGEST point immediately
3. Use 2-3 specific, concrete pieces of evidence (real data/statistics)
4. Make every sentence powerful and direct
5. No fluff - only impact

Format:
- Opening punch (your strongest claim with evidence)
- Supporting strike (1-2 more concrete facts)
- Closing impact (why this matters)

Be brief, brutal, and backed by data.""",

    "judge_round": """Evaluate these arguments on: "{topic}"

PRO: {pro_arg}

CON: {con_arg}

Rate 1-10 based on:
- Brevity and impact (shorter + more powerful = higher score)
- Specific evidence quality (real data, not vague claims)
- Direct engagement with opponent's points
- Strategic strength for this round number

Format:
PRO: X/10
CON: X/10
Winner: [PRO/CON/TIE]
Reason: [One sentence explaining why - be specific about what made the winner stronger]"""
}

# Store prompts in memory (resets when server restarts)
prompts = DEFAULT_PROMPTS.copy()

@app.route('/health', methods=['GET'])
def health():
    """Health check endpoint"""
    return jsonify({"status": "healthy", "message": "Debate server is running"})

@app.route('/generate', methods=['POST'])
def generate():
    """Generate AI response using OpenAI"""
    try:
        data = request.json
        prompt = data.get('prompt')
        
        if not prompt:
            return jsonify({"error": "No prompt provided"}), 400
        
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are a skilled debater and evaluator. Provide well-reasoned, strategic arguments."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.7,
            max_tokens=1000
        )
        
        return jsonify({
            'response': response.choices[0].message.content.strip()
        })
    
    except Exception as e:
        print(f"❌ Error in generate: {str(e)}")
        return jsonify({"error": str(e)}), 500

@app.route('/debate/argument', methods=['POST'])
def generate_argument():
    """Generate a debate argument"""
    try:
        data = request.json
        topic = data.get('topic')
        position = data.get('position')
        round_num = data.get('round', 1)
        context = data.get('context', 'No previous arguments.')
        
        print(f"🎯 Generating {position.upper()} argument for round {round_num}...")
        
        # Choose appropriate prompt
        if round_num == 1 and 'opening_statement' in prompts:
            prompt_template = prompts['opening_statement']
            formatted_prompt = prompt_template.format(
                topic=topic,
                position=position
            )
        elif 'strategic_debate' in prompts:
            prompt_template = prompts['strategic_debate']
            formatted_prompt = prompt_template.format(
                topic=topic,
                position=position,
                round_num=round_num,
                context=context
            )
        else:
            formatted_prompt = f"Argue the {position} position on: {topic}"
        
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are an expert debater with deep knowledge across many domains. You MUST provide specific, evidence-based arguments with concrete examples, statistics, and real-world cases. Avoid generic or vague statements. Be precise and detailed."},
                {"role": "user", "content": formatted_prompt}
            ],
            temperature=0.7,
            max_tokens=1000
        )
        
        argument = response.choices[0].message.content.strip()
        print(f"✅ Generated {position.upper()} argument ({len(argument)} chars)")
        
        return jsonify({
            'argument': argument
        })
    
    except Exception as e:
        print(f"❌ Error in generate_argument: {str(e)}")
        return jsonify({"error": str(e)}), 500

@app.route('/debate/judge', methods=['POST'])
def judge_round():
    """Judge a debate round"""
    try:
        data = request.json
        topic = data.get('topic')
        pro_arg = data.get('pro_argument')
        con_arg = data.get('con_argument')
        
        print(f"⚖️ Judging round...")
        
        if 'judge_round' not in prompts:
            return jsonify({"error": "Judge prompt not found"}), 400
        
        formatted_prompt = prompts['judge_round'].format(
            topic=topic,
            pro_arg=pro_arg,
            con_arg=con_arg
        )
        
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are an expert debate judge with deep analytical skills. Evaluate arguments based on specificity, evidence quality, and direct relevance to the topic. Penalize vague or generic statements."},
                {"role": "user", "content": formatted_prompt}
            ],
            temperature=0.7,
            max_tokens=800
        )
        
        judgment_text = response.choices[0].message.content.strip()
        
        # Extract scores
        pro_match = re.search(r'PRO[:\s]+(\d+)(?:\s*\/\s*10)?', judgment_text, re.IGNORECASE)
        con_match = re.search(r'CON[:\s]+(\d+)(?:\s*\/\s*10)?', judgment_text, re.IGNORECASE)
        
        pro_score = int(pro_match.group(1)) if pro_match else 5
        con_score = int(con_match.group(1)) if con_match else 5
        
        print(f"✅ Judgment complete: PRO {pro_score}/10, CON {con_score}/10")
        
        return jsonify({
            'pro_score': pro_score,
            'con_score': con_score,
            'feedback': judgment_text
        })
    
    except Exception as e:
        print(f"❌ Error in judge_round: {str(e)}")
        return jsonify({"error": str(e)}), 500

@app.route('/prompts', methods=['GET'])
def get_prompts():
    """Get all available prompts"""
    return jsonify(prompts)

@app.route('/prompts', methods=['POST'])
def add_prompt():
    """Add a new prompt"""
    try:
        data = request.json
        name = data.get('name')
        template = data.get('template')
        
        if not name or not template:
            return jsonify({"error": "Name and template required"}), 400
        
        prompts[name] = template
        print(f"✅ Added prompt: {name}")
        
        return jsonify({
            "message": f"Prompt '{name}' added successfully",
            "prompts": prompts
        })
    
    except Exception as e:
        print(f"❌ Error in add_prompt: {str(e)}")
        return jsonify({"error": str(e)}), 500

@app.route('/prompts/<name>', methods=['DELETE'])
def delete_prompt(name):
    """Delete a prompt"""
    if name in prompts:
        del prompts[name]
        print(f"🗑️ Deleted prompt: {name}")
        return jsonify({"message": f"Prompt '{name}' deleted"})
    return jsonify({"error": "Prompt not found"}), 404

if __name__ == '__main__':
    print("\n" + "=" * 60)
    print("🚀 AI DEBATE SERVER")
    print("=" * 60)
    print(f"📁 Working Directory: {os.getcwd()}")
    print(f"📡 Server URL: http://localhost:5000")
    print(f"✅ Status: Ready to accept debate requests!")
    print("=" * 60)
    print("\n💡 Next step: Open debate_agent.html in your browser")
    print("⚠️ Keep this terminal window open!\n")
    
    app.run(port=5000, debug=True)