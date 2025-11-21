# Product Requirements Document (PRD)
# VieMedChat - Trợ Lý Y Tế AI Tiếng Việt

**Version:** 1.0  
**Date:** 2025-11-21  
**Author:** Product Team  
**Status:** Active Development

---

## 📋 Executive Summary

**VieMedChat** là một hệ thống chatbot y tế thông minh sử dụng AI, được thiết kế đặc biệt cho người dùng Việt Nam. Hệ thống kết hợp công nghệ RAG (Retrieval-Augmented Generation), LLM fine-tuning, và agentic AI để cung cấp tư vấn y tế chính xác, nhanh chóng và dễ tiếp cận.

### 🎯 Vision
Trở thành nền tảng tư vấn y tế AI hàng đầu tại Việt Nam, giúp người dân tiếp cận thông tin y tế chính xác, đáng tin cậy 24/7.

### 🚀 Mission
- Cung cấp thông tin y tế chính xác bằng tiếng Việt
- Giảm tải cho hệ thống y tế bằng cách tư vấn sơ bộ
- Nâng cao nhận thức sức khỏe cộng đồng
- Hỗ trợ quyết định khám bệnh thông minh

---

## 🏗️ System Architecture

### Current Technology Stack

#### **Backend**
- **Framework:** Flask (Python)
- **Database:** PostgreSQL + Sequelize ORM
- **Authentication:** JWT (Flask-JWT-Extended)
- **Vector Database:** Pinecone
- **LLM Provider:** Google Gemini 2.0 Flash
- **Embedding Model:** BAAI/bge-m3
- **Reranker:** BAAI/bge-reranker-v2-m3
- **Fine-tuning:** Unsloth + LoRA (Qwen 2.5-1.5B)

#### **Frontend**
- **Framework:** React.js
- **Styling:** CSS
- **Deployment:** Vercel

#### **AI/ML Components**
1. **RAG Pipeline**
   - Hybrid Search (Vector + BM25)
   - Semantic Reranking
   - Context Optimization
   
2. **Agentic System**
   - Tool Calling (Function Calling)
   - Multi-tool Orchestration
   - Chain-of-Thought Reasoning

3. **Fine-tuned Models**
   - Tool Selection Model (Qwen 2.5-1.5B)
   - Trained on custom Vietnamese medical dataset

---

## 🎯 Current Features

### 1. **Intelligent Medical Consultation**
- **Description:** Trả lời câu hỏi y tế dựa trên RAG và LLM
- **Capabilities:**
  - Phân tích triệu chứng
  - Tư vấn bệnh lý
  - Thông tin thuốc
  - Khuyến nghị điều trị
- **Technology:** Gemini 2.0 Flash + Pinecone + BGE-M3

### 2. **Multi-Tool Agent System**
- **Description:** Agent thông minh tự động chọn công cụ phù hợp
- **Tools:**
  - `search_medical_documents` - Tìm kiếm tài liệu y tế
  - `calculator` - Tính toán (BMI, liều lượng, v.v.)
  - `general_chat` - Trò chuyện thông thường
- **Technology:** Function Calling + Chain-of-Thought

### 3. **User Authentication & Management**
- **Features:**
  - Đăng ký/Đăng nhập
  - JWT-based authentication
  - Session management
- **Security:** Encrypted passwords, secure tokens

### 4. **Conversation History**
- **Features:**
  - Lưu trữ lịch sử chat
  - Context-aware responses
  - Multi-session support

### 5. **Hybrid Search Engine**
- **Components:**
  - Vector Search (Semantic)
  - BM25 Search (Keyword)
  - Fusion Ranking
  - Semantic Reranking

---

## 🔧 Core Components

### 1. RAG Service (`backend/utils/rag_service.py`)
```
Features:
- Lazy loading for performance
- Caching mechanism
- Optimized retrieval (top-5 documents)
- Configurable reranking
```

### 2. Medical Agent (`backend/routes/agents/medical_agent_with_toolcall.py`)
```
Features:
- Direct tool calling (50-70% API savings vs ReAct)
- Chain-of-Thought reasoning
- Multi-tool orchestration
- Fallback mechanisms
```

### 3. Tool Selection Model (`kaggle_qwen_toolselection.py`)
```
Features:
- Fine-tuned Qwen 2.5-1.5B
- LoRA adapters
- Custom Vietnamese dataset (1000+ examples)
- 4-bit quantization for efficiency
```

### 4. Embedding & Search (`backend/routes/rag/`)
```
Components:
- embedding.py - BGE-M3 embeddings
- search.py - Hybrid search engine
- reranker.py - BGE reranker v2-m3
- llms.py - LLM integration
```

---

## 👥 User Personas

### Persona 1: **Người dùng thông thường**
- **Age:** 25-50
- **Tech Savvy:** Medium
- **Needs:**
  - Tư vấn triệu chứng nhanh
  - Thông tin thuốc
  - Khuyến nghị khám bệnh
- **Pain Points:**
  - Khó tiếp cận bác sĩ ngoài giờ
  - Không biết triệu chứng có nghiêm trọng không
  - Cần thông tin y tế đáng tin cậy

### Persona 2: **Bệnh nhân mãn tính**
- **Age:** 40-70
- **Conditions:** Tiểu đường, cao huyết áp, suy thận
- **Needs:**
  - Theo dõi sức khỏe định kỳ
  - Nhắc nhở uống thuốc
  - Tư vấn chế độ ăn
- **Pain Points:**
  - Quên lịch uống thuốc
  - Không biết chế độ ăn phù hợp
  - Cần giám sát liên tục

### Persona 3: **Phụ huynh**
- **Age:** 28-45
- **Needs:**
  - Tư vấn sức khỏe trẻ em
  - Lịch tiêm chủng
  - Xử lý cấp cứu cơ bản
- **Pain Points:**
  - Lo lắng về sức khỏe con
  - Không biết khi nào cần đưa con đi khám
  - Cần thông tin nhanh về bệnh trẻ em

---

## 📊 Success Metrics (KPIs)

### User Engagement
- **Daily Active Users (DAU):** Target 1,000+ users/day
- **Monthly Active Users (MAU):** Target 10,000+ users/month
- **Average Session Duration:** Target 5-10 minutes
- **Messages per Session:** Target 8-15 messages

### Quality Metrics
- **Response Accuracy:** Target 90%+
- **User Satisfaction (CSAT):** Target 4.5/5
- **Response Time:** Target < 3 seconds
- **Tool Selection Accuracy:** Target 95%+

### Business Metrics
- **User Retention (30-day):** Target 40%+
- **Conversion to Premium:** Target 5%+
- **Referral Rate:** Target 20%+

### Technical Metrics
- **API Uptime:** Target 99.9%
- **Average API Calls per Query:** Target < 3 calls
- **Context Retrieval Accuracy:** Target 85%+

---

## 🚧 Current Limitations

### Technical Limitations
1. **No real-time monitoring** - Thiếu dashboard theo dõi
2. **Limited medical knowledge base** - Cần mở rộng corpus
3. **No image analysis** - Chưa hỗ trợ phân tích hình ảnh y tế
4. **Single language** - Chỉ hỗ trợ tiếng Việt
5. **No voice interface** - Chưa có voice input/output

### Functional Limitations
1. **No appointment booking** - Chưa tích hợp đặt lịch khám
2. **No medication reminders** - Chưa có nhắc nhở uống thuốc
3. **No health tracking** - Chưa theo dõi chỉ số sức khỏe
4. **No emergency detection** - Chưa phát hiện tình huống khẩn cấp
5. **No doctor connection** - Chưa kết nối với bác sĩ thật

### UX Limitations
1. **Basic UI** - Giao diện đơn giản
2. **No mobile app** - Chỉ có web app
3. **No offline mode** - Cần internet để hoạt động
4. **No personalization** - Chưa cá nhân hóa theo user

---

## 🎯 Target Audience

### Primary Audience
- **Demographics:** Người Việt Nam, 18-60 tuổi
- **Location:** Thành thị và nông thôn
- **Income:** Trung bình trở lên
- **Education:** Trung học trở lên

### Secondary Audience
- Người nước ngoài sống tại Việt Nam (future expansion)
- Nhân viên y tế (công cụ hỗ trợ)
- Sinh viên y khoa (học tập)

---

## 🔐 Security & Compliance

### Current Security Measures
- JWT authentication
- Password encryption
- HTTPS/TLS encryption
- CORS protection
- SQL injection prevention

### Required Compliance (Future)
- **HIPAA** (if expanding to US)
- **GDPR** (if expanding to EU)
- **Vietnamese Personal Data Protection Law**
- Medical device regulations (if applicable)

### Privacy Considerations
- User data anonymization
- Secure data storage
- Clear privacy policy
- User consent management
- Data deletion rights

---

## 💰 Business Model (Proposed)

### Freemium Model

#### **Free Tier**
- 20 queries/day
- Basic medical consultation
- General health information
- Standard response time

#### **Premium Tier** ($4.99/month)
- Unlimited queries
- Priority response time
- Advanced features:
  - Health tracking
  - Medication reminders
  - Personalized recommendations
  - Export health reports
  - Doctor consultation booking

#### **Family Plan** ($9.99/month)
- Up to 5 family members
- All Premium features
- Family health dashboard
- Shared medication tracking

#### **Enterprise/Clinic** (Custom pricing)
- White-label solution
- Custom knowledge base
- Integration with clinic systems
- Analytics dashboard
- Dedicated support

---

## 🗓️ Development Roadmap

### Phase 1: MVP (Current) ✅
- [x] Basic RAG pipeline
- [x] Multi-tool agent
- [x] User authentication
- [x] Conversation history
- [x] Tool selection fine-tuning

### Phase 2: Enhancement (Q1 2026)
- [ ] Improved UI/UX
- [ ] Mobile responsive design
- [ ] Advanced analytics
- [ ] Performance optimization
- [ ] Extended knowledge base

### Phase 3: Advanced Features (Q2 2026)
- [ ] Image analysis (X-rays, skin conditions)
- [ ] Voice interface
- [ ] Health tracking
- [ ] Medication reminders
- [ ] Appointment booking

### Phase 4: Ecosystem (Q3-Q4 2026)
- [ ] Mobile apps (iOS/Android)
- [ ] Doctor portal
- [ ] Clinic integration
- [ ] Telemedicine features
- [ ] Multi-language support

---

## 🔄 Integration Points

### Current Integrations
- Pinecone (Vector DB)
- Google Gemini API
- PostgreSQL

### Planned Integrations
- Hospital/Clinic Management Systems
- Pharmacy systems
- Health insurance providers
- Wearable devices (Fitbit, Apple Watch)
- Telemedicine platforms
- Payment gateways (VNPay, Momo)

---

## 📝 User Stories

### Epic 1: Medical Consultation
- **US-001:** As a user, I want to describe my symptoms and get possible diagnoses
- **US-002:** As a user, I want to know when I should see a doctor
- **US-003:** As a user, I want to learn about medications and their side effects
- **US-004:** As a user, I want to understand my medical test results

### Epic 2: Health Management
- **US-005:** As a chronic patient, I want to track my daily health metrics
- **US-006:** As a user, I want reminders to take my medications
- **US-007:** As a user, I want to see my health trends over time
- **US-008:** As a user, I want personalized health recommendations

### Epic 3: Emergency Support
- **US-009:** As a user, I want to know if my symptoms are an emergency
- **US-010:** As a user, I want quick access to emergency contacts
- **US-011:** As a user, I want first aid instructions

### Epic 4: Appointment & Services
- **US-012:** As a user, I want to book doctor appointments
- **US-013:** As a user, I want to find nearby clinics/hospitals
- **US-014:** As a user, I want to connect with a real doctor when needed

---

## 🎨 Design Principles

### 1. **User-Centric**
- Simple, intuitive interface
- Clear, easy-to-understand language
- Minimal clicks to get answers

### 2. **Trustworthy**
- Cite medical sources
- Clear disclaimers
- Transparent AI limitations
- Professional tone

### 3. **Accessible**
- Works on all devices
- Fast loading times
- Offline capabilities (future)
- Voice support (future)

### 4. **Empathetic**
- Understanding tone
- Supportive responses
- Culturally appropriate
- Privacy-focused

---

## 🧪 Testing Strategy

### Current Testing
- Manual testing
- Basic integration tests
- Tool selection accuracy testing

### Required Testing
1. **Unit Tests** - Individual components
2. **Integration Tests** - API endpoints
3. **E2E Tests** - User flows
4. **Performance Tests** - Load testing
5. **Security Tests** - Penetration testing
6. **Medical Accuracy Tests** - Expert validation
7. **User Acceptance Tests** - Beta testing

---

## 📚 Documentation Requirements

### Technical Documentation
- [x] API documentation
- [ ] Architecture diagrams
- [ ] Database schema
- [ ] Deployment guide
- [ ] Contributing guidelines

### User Documentation
- [ ] User guide
- [ ] FAQ
- [ ] Video tutorials
- [ ] Privacy policy
- [ ] Terms of service

### Medical Documentation
- [ ] Knowledge base sources
- [ ] Medical disclaimer
- [ ] Accuracy validation reports
- [ ] Expert review process

---

## 🌟 Competitive Advantage

### Unique Selling Points (USPs)
1. **Vietnamese-First** - Tối ưu cho người Việt
2. **Advanced AI** - RAG + Fine-tuning + Agentic AI
3. **Multi-Tool Intelligence** - Tự động chọn công cụ phù hợp
4. **Fast & Efficient** - < 3 giây response time
5. **Cost-Effective** - 50-70% tiết kiệm API calls
6. **Accurate** - Semantic search + Reranking
7. **24/7 Availability** - Luôn sẵn sàng hỗ trợ

### Competitive Landscape
- **Ada Health** - Global, không tối ưu tiếng Việt
- **Babylon Health** - Đắt, không có ở VN
- **WebMD** - Chỉ thông tin, không tư vấn
- **Local clinics** - Giờ làm việc hạn chế
- **VieMedChat** - Tối ưu cho VN, AI tiên tiến, giá rẻ

---

## 🚀 Go-to-Market Strategy

### Launch Strategy
1. **Beta Testing** (1-2 months)
   - 100-500 beta users
   - Collect feedback
   - Iterate on features

2. **Soft Launch** (Month 3)
   - Launch in Ho Chi Minh City
   - Social media marketing
   - Influencer partnerships

3. **National Launch** (Month 6)
   - Expand to all Vietnam
   - PR campaigns
   - Partnership with clinics

### Marketing Channels
- **Digital Marketing**
  - Facebook Ads
  - Google Ads
  - TikTok
  - Zalo
  
- **Content Marketing**
  - Health blog
  - YouTube videos
  - Infographics
  
- **Partnerships**
  - Clinics & hospitals
  - Pharmacies
  - Health insurance companies
  - Corporate wellness programs

---

## 💡 Risk Assessment

### Technical Risks
| Risk | Impact | Probability | Mitigation |
|------|--------|-------------|------------|
| API downtime | High | Medium | Fallback LLM, caching |
| Inaccurate responses | High | Medium | Expert validation, disclaimers |
| Data breach | High | Low | Strong security, encryption |
| Scalability issues | Medium | Medium | Cloud infrastructure, load balancing |

### Business Risks
| Risk | Impact | Probability | Mitigation |
|------|--------|-------------|------------|
| Low user adoption | High | Medium | Marketing, user testing |
| Regulatory issues | High | Low | Legal consultation, compliance |
| Competition | Medium | High | Continuous innovation |
| Funding shortage | High | Low | Revenue model, investors |

### Medical/Legal Risks
| Risk | Impact | Probability | Mitigation |
|------|--------|-------------|------------|
| Misdiagnosis | Critical | Medium | Clear disclaimers, expert review |
| Liability claims | High | Low | Insurance, legal terms |
| Regulatory non-compliance | High | Low | Legal consultation |

---

## 📞 Support & Maintenance

### Support Channels
- In-app chat support
- Email support
- FAQ/Help center
- Community forum (future)

### Maintenance Plan
- **Daily:** Monitoring, bug fixes
- **Weekly:** Performance optimization
- **Monthly:** Feature updates, knowledge base updates
- **Quarterly:** Major releases, security audits

---

## 🎓 Training & Onboarding

### User Onboarding
1. Welcome tutorial
2. Sample questions
3. Feature highlights
4. Privacy & terms

### Medical Expert Onboarding (Future)
1. Platform training
2. Quality guidelines
3. Review process
4. Feedback mechanisms

---

## 📈 Analytics & Monitoring

### Current Analytics
- Basic logging
- Error tracking

### Required Analytics
1. **User Analytics**
   - User behavior
   - Feature usage
   - Conversion funnels
   
2. **Performance Analytics**
   - Response times
   - API usage
   - Error rates
   
3. **Medical Analytics**
   - Common symptoms
   - Popular topics
   - Accuracy metrics
   
4. **Business Analytics**
   - Revenue
   - User acquisition cost
   - Lifetime value

---

## 🔮 Future Vision (2027+)

### Long-term Goals
1. **AI Doctor Assistant** - Hỗ trợ bác sĩ chẩn đoán
2. **Predictive Health** - Dự đoán bệnh sớm
3. **Personalized Medicine** - Điều trị cá nhân hóa
4. **Regional Expansion** - Mở rộng Đông Nam Á
5. **Research Platform** - Nền tảng nghiên cứu y tế

### Emerging Technologies
- **Multimodal AI** - Text + Image + Voice + Video
- **Federated Learning** - Privacy-preserving ML
- **Blockchain** - Secure health records
- **IoT Integration** - Smart health devices
- **AR/VR** - Virtual consultations

---

## ✅ Acceptance Criteria

### MVP Acceptance
- [x] User can register and login
- [x] User can ask medical questions
- [x] System provides accurate responses (>85%)
- [x] Response time < 5 seconds
- [x] Agent selects correct tool (>90%)
- [x] Conversation history is saved

### Production Ready
- [ ] 99.9% uptime
- [ ] < 3 second response time
- [ ] >90% accuracy
- [ ] >95% tool selection accuracy
- [ ] Security audit passed
- [ ] Legal compliance verified
- [ ] User testing completed (>4.0/5 satisfaction)

---

## 📋 Appendix

### A. Glossary
- **RAG:** Retrieval-Augmented Generation
- **LLM:** Large Language Model
- **LoRA:** Low-Rank Adaptation
- **BMI:** Body Mass Index
- **CSAT:** Customer Satisfaction Score
- **DAU/MAU:** Daily/Monthly Active Users

### B. References
- Gemini API Documentation
- Pinecone Documentation
- LangChain Documentation
- Unsloth Documentation
- Medical knowledge sources

### C. Contact Information
- **Product Owner:** [TBD]
- **Tech Lead:** [TBD]
- **Medical Advisor:** [TBD]

---

**Document Version History**
- v1.0 (2025-11-21): Initial PRD creation
