# 🏥 VieMedChat - Intelligent Medical AI Assistant

![Python](https://img.shields.io/badge/Python-3.9+-blue.svg)
![React](https://img.shields.io/badge/React-18-blue.svg)
![Flask](https://img.shields.io/badge/Flask-2.0+-green.svg)
![PostgreSQL](https://img.shields.io/badge/PostgreSQL-15-blue.svg)
![Docker](https://img.shields.io/badge/Docker-Enabled-blue.svg)

> **Disclaimer:** This project is for research and educational purposes only. The medical information provided is for reference only and does not substitute for professional medical advice, diagnosis, or treatment.

## 📖 Introduction

**VieMedChat** is an advanced medical chatbot system leveraging **RAG (Retrieval-Augmented Generation)** and **Agentic AI** technologies. The system is designed to assist users in looking up medical information, symptoms, and medications accurately and quickly using natural language (Vietnamese).

### ✨ Key Features
- 🤖 **Intelligent AI Agent**: Automatically classifies user queries and selects the appropriate tool (RAG, Calculator, General Chat).
- 📚 **RAG Knowledge Base**: Retrieves information from trusted medical data sources, minimizing LLM hallucinations.
- 🧠 **Fine-tuned Model**: Utilizes a Qwen 2.5 model specifically fine-tuned for Vietnamese medical tasks.
- 💬 **User-Friendly Interface**: Natural chat interaction with conversation history support.

---

## 🛠️ Tech Stack

### Backend
- **Framework**: Flask (Python)
- **LLM**: Google Gemini 2.0 Flash / Qwen 2.5 (Fine-tuned)
- **Vector DB**: Pinecone
- **Embedding**: BAAI/bge-m3
- **Database**: PostgreSQL (User management, Chat history)

### Frontend
- **Framework**: React.js
- **Styling**: CSS Modules
- **State Management**: React Hooks

---

## 🚀 Installation & Setup

### Prerequisites
- Python 3.9+
- Node.js 16+
- PostgreSQL
- Google AI Studio Account (Gemini API Key)
- Pinecone Account (Vector DB)

### 1. Clone the repository
```bash
git clone https://github.com/yourusername/VieMedChat.git
cd VieMedChat
```

### 2. Setup Backend
```bash
cd backend
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements.txt

# Create .env file from example and fill in your keys
cp .env.example .env
```

### 3. Setup Database
```bash
# Ensure PostgreSQL is running
# Run database initialization script
python utils/init_db.py
```

### 4. Setup Frontend
```bash
cd ../frontend
npm install
```

### 5. Run the Application
**Backend:**
```bash
cd backend
python app.py
# Server runs at: http://localhost:5000
```

**Frontend:**
```bash
cd frontend
npm start
# App runs at: http://localhost:3000
```

---

## 📂 Project Structure

```
VieMedChat/
├── backend/
│   ├── controllers/     # API Logic
│   ├── routes/          # API Endpoints
│   ├── utils/           # Utilities (RAG, DB)
│   ├── agents/          # AI Agent Logic
│   └── app.py           # Entry point
├── frontend/
│   ├── src/
│   │   ├── components/  # UI Components
│   │   ├── pages/       # Main Pages
│   │   └── services/    # API Calls
│   └── public/
└── ...
```

---

## 🤝 Contribution
Contributions are welcome! Please feel free to submit a Pull Request or open an Issue for discussion.

## 📄 License
MIT License
