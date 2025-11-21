# 🏥 VieMedChat - Trợ Lý Y Tế AI Thông Minh

![Python](https://img.shields.io/badge/Python-3.9+-blue.svg)
![React](https://img.shields.io/badge/React-18-blue.svg)
![Flask](https://img.shields.io/badge/Flask-2.0+-green.svg)
![PostgreSQL](https://img.shields.io/badge/PostgreSQL-15-blue.svg)
![Docker](https://img.shields.io/badge/Docker-Enabled-blue.svg)

> **Lưu ý:** Dự án này là sản phẩm nghiên cứu và học tập. Các thông tin y tế chỉ mang tính chất tham khảo, không thay thế lời khuyên của bác sĩ chuyên khoa.

## 📖 Giới thiệu

**VieMedChat** là hệ thống chatbot tư vấn y tế sử dụng công nghệ **RAG (Retrieval-Augmented Generation)** và **Agentic AI**. Hệ thống được thiết kế để hỗ trợ người dùng tra cứu thông tin bệnh lý, triệu chứng và thuốc một cách chính xác, nhanh chóng bằng ngôn ngữ tự nhiên (Tiếng Việt).

### ✨ Tính năng nổi bật
- 🤖 **AI Agent thông minh**: Tự động phân loại câu hỏi và chọn công cụ xử lý phù hợp (RAG, Calculator, General Chat).
- 📚 **RAG Knowledge Base**: Truy xuất thông tin từ kho dữ liệu y tế uy tín, giảm thiểu ảo giác (hallucination) của LLM.
- 🧠 **Fine-tuned Model**: Sử dụng mô hình Qwen 2.5 được tinh chỉnh riêng cho tác vụ y tế tiếng Việt.
- 💬 **Giao diện thân thiện**: Chatbot tương tác tự nhiên, hỗ trợ lưu lịch sử trò chuyện.

---

## 🛠️ Tech Stack

### Backend
- **Framework**: Flask (Python)
- **LLM**: Google Gemini 2.0 Flash / Qwen 2.5 (Fine-tuned)
- **Vector DB**: Pinecone
- **Embedding**: BAAI/bge-m3
- **Database**: PostgreSQL (Lưu user, history)

### Frontend
- **Framework**: React.js
- **Styling**: CSS Modules
- **State Management**: React Hooks

---

## 🚀 Cài đặt & Chạy dự án

### Yêu cầu tiên quyết
- Python 3.9+
- Node.js 16+
- PostgreSQL
- Tài khoản Google AI Studio (Gemini API Key)
- Tài khoản Pinecone (Vector DB)

### 1. Clone dự án
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

# Tạo file .env từ .env.example và điền key
cp .env.example .env
```

### 3. Setup Database
```bash
# Đảm bảo PostgreSQL đang chạy
# Chạy script khởi tạo DB
python utils/init_db.py
```

### 4. Setup Frontend
```bash
cd ../frontend
npm install
```

### 5. Chạy ứng dụng
**Backend:**
```bash
cd backend
python app.py
# Server chạy tại: http://localhost:5000
```

**Frontend:**
```bash
cd frontend
npm start
# App chạy tại: http://localhost:3000
```

---

## 📂 Cấu trúc dự án

```
VieMedChat/
├── backend/
│   ├── controllers/     # Xử lý logic API
│   ├── routes/          # Định nghĩa API endpoints
│   ├── utils/           # Các hàm tiện ích (RAG, DB)
│   ├── agents/          # Logic AI Agent
│   └── app.py           # Entry point
├── frontend/
│   ├── src/
│   │   ├── components/  # UI Components
│   │   ├── pages/       # Các màn hình chính
│   │   └── services/    # Gọi API Backend
│   └── public/
└── ...
```

---

## 🤝 Đóng góp
Mọi đóng góp đều được hoan nghênh! Vui lòng tạo Pull Request hoặc mở Issue để thảo luận.

## 📄 License
MIT License
