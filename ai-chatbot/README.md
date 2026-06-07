# 🤖 AI Chatbot — Python + LLM API

A **modular, production-ready AI Chatbot** built with Python and the Anthropic Claude API. Designed with clean architecture principles — fully extensible and easy to understand.

---

## ✨ Features

| Feature | Description |
|---|---|
| 🧠 **Multi-turn Conversations** | Maintains full conversation history across turns |
| 🎭 **Multiple Personas** | Switch between Assistant, Teacher, Debugger, and more |
| 📝 **Auto Summarization** | Summarizes long conversations to stay within token limits |
| 💬 **Sentiment Analysis** | Detects user sentiment on every message |
| 💾 **Chat Export** | Save conversations to JSON or plain text |
| 🪵 **Structured Logging** | Full rotating logs for debugging and audit |
| 🧪 **Unit Tests** | Core modules covered with `unittest` |
| 🖥️ **Rich CLI** | Colorful, formatted terminal interface |

---

## 🗂️ Project Structure

```
ai-chatbot/
├── main.py                  # Entry point — run this
├── config/
│   └── settings.py          # Centralized configuration
├── core/
│   ├── llm_client.py        # Anthropic API wrapper
│   ├── conversation.py      # Conversation orchestrator
│   └── memory.py            # Message history manager
├── features/
│   ├── persona.py           # System persona definitions
│   ├── summarizer.py        # Auto conversation summarizer
│   └── sentiment.py         # Sentiment analysis module
├── cli/
│   └── interface.py         # Terminal UI (Rich library)
├── utils/
│   ├── logger.py            # Rotating file logger
│   └── helpers.py           # Shared utilities
├── tests/
│   ├── test_conversation.py
│   └── test_llm_client.py
└── exports/                 # Saved chat histories
```

---

## 🚀 Getting Started

### 1. Clone the repo
```bash
git clone https://github.com/YOUR_USERNAME/ai-chatbot.git
cd ai-chatbot
```

### 2. Create a virtual environment
```bash
python -m venv venv
source venv/bin/activate        # macOS/Linux
venv\Scripts\activate           # Windows
```

### 3. Install dependencies
```bash
pip install -r requirements.txt
```

### 4. Set up environment variables
```bash
cp .env.example .env
# Edit .env and add your Anthropic API key
```

### 5. Run the chatbot
```bash
python main.py
```

---

## 🎮 CLI Commands

While chatting, type any of these special commands:

| Command | Action |
|---|---|
| `/help` | Show all commands |
| `/persona <name>` | Switch persona (assistant, teacher, debugger, chef) |
| `/summary` | Summarize the current conversation |
| `/sentiment` | Show last detected sentiment |
| `/history` | Print full chat history |
| `/export` | Save conversation to file |
| `/clear` | Clear conversation history |
| `/quit` | Exit the chatbot |

---

## 🧪 Running Tests
```bash
python -m pytest tests/ -v
```

---

## 🛠️ Tech Stack

- **Python 3.10+**
- **Anthropic SDK** — Claude claude-sonnet-4-20250514 LLM
- **Rich** — Terminal formatting
- **python-dotenv** — Environment variable management
- **pytest** — Testing framework

---

## 📸 Demo

```
╔══════════════════════════════════════════════╗
║           🤖 AI Chatbot v1.0.0               ║
║         Powered by Claude claude-sonnet-4-20250514              ║
╚══════════════════════════════════════════════╝

[Persona: Assistant] Type /help for commands

You: Explain recursion simply
🤖 Bot: Recursion is when a function calls itself...

You: /persona teacher
✅ Switched to persona: Teacher

You: /export
✅ Conversation saved to exports/chat_2024-01-15_10-30.json
```

---

## 📄 License

MIT License — free to use and modify.

---

## 🙋 Author

Built by **[Your Name]** — B.Tech CS (AI & Data Science), 4th Year  
📧 your.email@example.com | 🔗 [LinkedIn](https://linkedin.com)
