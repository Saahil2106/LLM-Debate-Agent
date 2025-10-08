# AI Debate Agent

An intelligent debate system powered by OpenAI that simulates strategic arguments between two AI agents with real-time judging and scoring.

<img width="1918" height="1064" alt="image" src="https://github.com/user-attachments/assets/023d66d1-c936-43a0-9d43-06370dd5f93b" />


## Features

- **Dual AI Agents**: PRO and CON positions argue with strategic, evidence-based arguments
- **Intelligent Judging**: Impartial AI judge scores each round (1-10 scale)
- **Live Scoreboard**: Real-time score tracking with round-by-round breakdown
- **Beautiful UI**: Modern, responsive web interface with chat-like design
- **Custom Prompts**: Add and manage custom debate prompt templates
- **Infinite Rounds**: Continue debates as long as you want
- **Progressive Intensity**: Each round gets strategically stronger and more aggressive
- **Responsive Design**: Works on desktop, tablet, and mobile

## Demo



*AI agents debating with real-time judging and scoring*

## 🚀 Quick Start

### Prerequisites

- Python 3.7 or higher
- OpenAI API key ([Get one here](https://platform.openai.com/api-keys))

### Installation

1. **Clone the repository**
```bash
git clone https://github.com/yourusername/ai-debate-agent.git
cd ai-debate-agent
```

2. **Install dependencies**
```bash
pip install flask flask-cors openai python-dotenv
```

3. **Set up your API key**

Create a `.env` file in the project root:
```env
OPENAI_API_KEY=your_api_key_here
```

Or edit line 18 in `final_test.py`:
```python
api_key = "sk-proj-your-api-key-here"
```

4. **Start the backend server**
```bash
python final_test.py
```` file in the project root:
```env
OPENAI_API_KEY=your_api_key_here
```

Or edit line 18 in `debate_server.py`:
```python
api_key = "sk-proj-your-api-key-here"
```

4. **Start the backend server**
```bash
python debate_server.py
```

5. **Open the frontend**

Simply open `debate_agent.html` in your web browser.

## 📖 Usage

### Starting a Debate

1. Click **"Start New Debate"**
2. Enter your debate topic (e.g., "Is nuclear energy safer than coal?")
3. Watch AI agents argue in real-time
4. Click **"Next Round"** to continue the debate

### Managing Prompts

- **Add Prompt**: Create custom debate templates with variables
- **View Prompts**: See all available prompt templates
- Available variables: `{topic}`, `{position}`, `{round_num}`, `{context}`

### Example Topics

- "Should AI replace human judges?"
- "Is remote work more productive than office work?"
- "Are electric cars better for the environment?"
- "Should social media be regulated by government?"

## 🏗️ Architecture

```
┌─────────────────────┐         HTTP/REST API        ┌─────────────────────┐
│  debate_agent.html  │ ◄─────────────────────────► │   final_test.py     │
│   (Frontend/UI)     │      JSON Requests/          │   (Backend API)     │
│   JavaScript        │      Responses               │   Flask + OpenAI    │
└─────────────────────┘                               └─────────────────────┘
```

### Tech Stack

**Frontend:**
- Pure HTML/CSS/JavaScript
- No frameworks required
- Modern ES6+ features

**Backend:**
- Flask (Python web framework)
- OpenAI API (GPT-3.5-turbo)
- Flask-CORS (Cross-origin support)

## 📂 Project Structure

```
ai-debate-agent/
├── debate_agent.html      # Frontend web interface
├── final_test.py          # Backend API server
├── .env                   # Environment variables (API key)
├── README.md             # This file
└── screenshot.png        # Demo screenshot
```

## 🔧 Configuration

### Change AI Model

Edit `final_test.py` (lines 157, 199, 234):
```python
model="gpt-3.5-turbo"  # Fast and affordable
# or
model="gpt-4"          # Smarter, slower, more expensive
```

### Adjust Argument Length

Edit `final_test.py` prompts section:
```python
"1. Keep it BRIEF: 100-150 words MAX"  # Modify as needed
```

### Custom Port

Edit `final_test.py` (last line):
```python
app.run(port=5000)  # Change to any available port
```

Then update `debate_agent.html` (line ~200):
```javascript
const API_URL = 'http://localhost:5000';  // Match your port
```

## 📊 API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/health` | GET | Health check |
| `/debate/argument` | POST | Generate debate argument |
| `/debate/judge` | POST | Judge a round |
| `/prompts` | GET | Get all prompts |
| `/prompts` | POST | Add new prompt |
| `/prompts/<name>` | DELETE | Delete prompt |

### Example API Request

```bash
curl -X POST http://localhost:5000/debate/argument \
  -H "Content-Type: application/json" \
  -d '{
    "topic": "Are cats better than dogs?",
    "position": "pro",
    "round": 1,
    "context": "No previous arguments."
  }'
```

## 🎨 Customization

### Modify Debate Style

Edit prompt templates in `final_test.py`:

```python
DEFAULT_PROMPTS = {
    "strategic_debate": """Your custom prompt here...""",
    "opening_statement": """Your custom opening...""",
    "judge_round": """Your custom judging criteria..."""
}
```

### Change UI Colors

Edit `debate_agent.html` CSS section (around line 15-500):

```css
.pro-badge {
    background: #d1fae5;  /* Change PRO color */
    color: #065f46;
}

.con-badge {
    background: #fee2e2;  /* Change CON color */
    color: #991b1b;
}
```

## 🐛 Troubleshooting

### Issue: "Backend not connected"

**Solution:** Make sure `final_test.py` is running:
```bash
python final_test.py
```

### Issue: CORS errors in browser

**Solution:** Ensure `flask-cors` is installed:
```bash
pip install flask-cors
```

### Issue: API key errors

**Solution:** 
1. Check your `.env` file exists and has the correct key
2. Or hardcode the key in `final_test.py` line 18

### Issue: Slow responses

**Normal!** AI takes 10-20 seconds per argument. This is expected behavior.

To speed up (with lower quality):
- Use GPT-3.5-turbo instead of GPT-4
- Reduce `max_tokens` in `final_test.py`

## 💰 Cost Estimation

Using GPT-3.5-turbo:
- ~$0.002 per debate round (3 API calls)
- ~$0.006 for a 3-round debate
- Very affordable for personal use

Using GPT-4:
- ~$0.06 per debate round
- ~$0.18 for a 3-round debate
- Higher quality but more expensive

## 🤝 Contributing

Contributions are welcome! Here's how you can help:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

### Ideas for Contributions

- [ ] Add user authentication
- [ ] Save debate history to database
- [ ] Export debates as PDF/Markdown
- [ ] Add more AI models (Claude, Gemini, etc.)
- [ ] Implement real-time streaming responses
- [ ] Add debate templates/presets
- [ ] Multi-language support
- [ ] Voice synthesis for arguments

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- OpenAI for the GPT API
- Flask team for the excellent web framework
- The open-source community

## 📧 Contact

Your Name - [@yourtwitter](https://twitter.com/yourtwitter)

Project Link: [https://github.com/yourusername/ai-debate-agent](https://github.com/yourusername/ai-debate-agent)

---

⭐ **Star this repo** if you find it useful!

🐛 **Found a bug?** [Open an issue](https://github.com/yourusername/ai-debate-agent/issues)

💡 **Have an idea?** [Start a discussion](https://github.com/yourusername/ai-debate-agent/discussions)
