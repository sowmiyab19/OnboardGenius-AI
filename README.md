# 🚀 OnboardGenius AI – Employee Onboarding Management System

## 📌 Overview
OnboardGenius AI is a full-stack Employee Onboarding Management System that streamlines the onboarding process by enabling HR teams to manage employees, assign onboarding tasks, share documents, publish announcements, and provide AI-powered assistance through a secure and user-friendly platform.

---

## ✨ Features

- 👤 Employee Registration & Management
- 🔐 Secure JWT Authentication
- 📋 Task Assignment & Tracking
- 📄 Document Upload & Management
- 📢 Company Announcements
- 🤖 AI-Powered Chatbot Assistance
- 👥 Employee Profile Management
- 📊 RESTful APIs with Swagger Documentation
- 💾 MySQL Database Integration

---

## 🛠️ Tech Stack

### Frontend
- HTML5
- CSS3
- JavaScript

### Backend
- Python
- FastAPI

### Database
- MySQL
- SQLAlchemy ORM

### Authentication
- JWT Authentication
- Passlib (Password Hashing)

### AI Integration
- OpenAI API

### Tools
- Git
- GitHub
- Swagger UI
- Uvicorn

---

## 📂 Project Structure

```
OnboardGenius AI/
│
├── backend/
│   ├── auth/
│   ├── database/
│   ├── models/
│   ├── routers/
│   ├── services/
│   ├── ai/
│   ├── schemas.py
│   └── main.py
│
├── frontend/
│   ├── css/
│   ├── js/
│   ├── images/
│   └── index.html
│
└── README.md
```

---

## ⚙️ Installation

### 1. Clone Repository

```bash
git clone https://github.com/yourusername/OnboardGenius-AI.git
cd OnboardGenius-AI
```

### 2. Install Dependencies

```bash
pip install -r requirements.txt
```

### 3. Configure Database

Create a MySQL database:

```sql
CREATE DATABASE onboardgenius;
```

Update your database credentials in the configuration file.

### 4. Run Backend

```bash
python -m uvicorn backend.main:app --reload
```

Backend:

```
http://127.0.0.1:8000
```

Swagger API:

```
http://127.0.0.1:8000/docs
```

### 5. Run Frontend

Open `index.html` using Live Server or serve the frontend with your preferred web server.

---

## 📸 Screenshots

- Login Page
- Admin Dashboard
- Employee Dashboard
- Employee Management
- Task Management
- Announcements
- AI Chatbot

---

## 📌 Future Enhancements

- Email Notifications
- File Storage on Cloud
- Attendance Management
- Analytics Dashboard
- Mobile Responsive Design

---

## 👨‍💻 Author

**Sowmiya**

GitHub: https://github.com/sowmiyab19

LinkedIn: https://linkedin.com/in/sowmiya-b-1235b7358

Email: sowmib9@gmail.com

---

## 📄 License

This project is developed for educational and portfolio purposes.
