# Campus Lost and Found

A professional, full-stack application designed to streamline the lost and found process for university campuses. Built with a modular Python (Flask) backend and a modern React (Vite) frontend.

## 🚀 Features

- **User Reporting**: Easy submission for both lost and found items.
- **Admin Dashboard**: Comprehensive claim verification and item resolution.
- **Security**: Short-lived JWTs, Refresh Token Rotation (RTR), and rate-limiting.
- **Modular Design**: Application factory pattern with a decoupled service layer.
- **Modern UI**: Professional aesthetics with responsive design and interactive elements.

## 📁 Project Structure

```
root/
│
├── frontend/             # React (Vite) Application
│   ├── src/              # Source code
│   ├── public/           # Static assets (logos, backgrounds)
│   └── .env.example      # Frontend environment template
│
├── backend/              # Flask Modular Application
│   ├── app/              # Core logic
│   │   ├── routes/       # API Endpoints
│   │   ├── services/     # Business Logic
│   │   ├── models/       # Database Models
│   │   └── utils/        # Shared Utilities
│   ├── config/           # Configuration management
│   ├── migrations/       # Database migrations
│   └── .env.example      # Backend environment template
│
├── docs/                 # Documentation
│   ├── API.md            # API Specifications
│   └── ARCHITECTURE.md   # System Architecture
│
├── README.md             # Project Overview
└── .gitignore            # Version control exclusions
```

## 🛠️ Getting Started

### Prerequisites
- Python 3.10+
- Node.js 18+
- npm or yarn

### Backend Setup
1. `cd backend`
2. `python -m venv venv`
3. `venv\Scripts\activate` (Windows) or `source venv/bin/activate` (Linux/Mac)
4. `pip install -r requirements.txt`
5. Copy `.env.example` to `.env` and configure your secrets.
6. `python app.py`

### Frontend Setup
1. `cd frontend`
2. `npm install`
3. Copy `.env.example` to `.env`.
4. `npm run dev`

## 📖 Documentation
Detailed technical documentation can be found in the [docs/](docs/) directory.

## ⚖️ License
[Insert License Here] - Professional use recommended.
