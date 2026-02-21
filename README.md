# ChatGPTLike

A ChatGPT-like application with Excel file analysis capabilities, built with React, FastAPI, and PostgreSQL.

## Features

- **Multi-user authentication** with JWT tokens
- **Chat sessions** with conversation history
- **Streaming responses** from OpenAI
- **File upload** for Excel analysis (max 50MB)
- **Data visualizations** (Pie, Bar, Line, Scatter charts)
- **User-provided OpenAI API keys** (no server-side costs)
- **Dark mode** interface matching ChatGPT design
- **Docker Compose** for easy deployment

## Tech Stack

### Backend
- FastAPI - Python web framework
- PostgreSQL - Database
- SQLAlchemy - ORM
- Alembic - Database migrations
- OpenAI API - AI responses
- pandas & openpyxl - Excel processing

### Frontend
- React - UI framework
- Vite - Build tool
- Redux Toolkit - State management
- Tailwind CSS - Styling
- Recharts - Charting
- React Router - Navigation

## Quick Start

### Using Docker Compose (Recommended)

1. Clone the repository:
```bash
git clone <repository-url>
cd chatgptLike
```

2. Create environment file:
```bash
cp .env.example .env
```

3. Start the application:
```bash
docker-compose up --build
```

4. Access the application:
- Frontend: http://localhost:3000
- Backend API: http://localhost:8000
- API Docs: http://localhost:8000/docs

### Development Setup

#### Backend

1. Navigate to backend directory:
```bash
cd backend
```

2. Create virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Set up environment variables:
```bash
cp .env.example .env
# Edit .env with your values
```

5. Run migrations:
```bash
alembic upgrade head
```

6. Start the server:
```bash
uvicorn app.main:app --reload
```

#### Frontend

1. Navigate to frontend directory:
```bash
cd frontend
```

2. Install dependencies:
```bash
npm install
```

3. Start the development server:
```bash
npm run dev
```

4. Access at http://localhost:3000

## Configuration

### Environment Variables

Create a `.env` file in the root directory:

```env
# Database
POSTGRES_USER=chatuser
POSTGRES_PASSWORD=chatpass
POSTGRES_DB=chatdb

# Security
SECRET_KEY=your-secret-key-change-in-production

# OpenAI
OPENAI_DEFAULT_MODEL=gpt-4
```

### OpenAI API Key

Each user must provide their own OpenAI API key:
1. Sign up at [OpenAI Platform](https://platform.openai.com/)
2. Navigate to API Keys section
3. Create a new API key
4. Add it in the application settings

## API Documentation

Once the backend is running, visit http://localhost:8000/docs for interactive API documentation.

### Main Endpoints

- `POST /api/auth/register` - Register a new user
- `POST /api/auth/login` - Login and get JWT token
- `GET /api/auth/me` - Get current user info
- `GET /api/chat/sessions` - List user's chat sessions
- `POST /api/chat/sessions` - Create a new session
- `POST /api/chat/sessions/{id}/messages` - Send a message (streaming)
- `POST /api/files/upload` - Upload an Excel file

## File Upload

Supported formats: `.xlsx`, `.xls`
Maximum file size: 50MB

Files are automatically deleted when their associated chat session is deleted.

## Visualizations

The AI can suggest and generate the following chart types:
- Pie Chart
- Bar Chart
- Line Chart
- Scatter Plot

Charts are rendered using Recharts with a dark theme to match the application.

## Project Structure

```
chatgptLike/
├── backend/
│   ├── app/
│   │   ├── auth/          # Authentication endpoints
│   │   ├── chat/          # Chat endpoints & OpenAI integration
│   │   ├── files/         # File upload handling
│   │   ├── main.py        # FastAPI app
│   │   ├── models.py      # Database models
│   │   └── ...
│   ├── alembic/           # Database migrations
│   └── requirements.txt
├── frontend/
│   ├── src/
│   │   ├── components/    # React components
│   │   ├── store/         # Redux store
│   │   ├── services/      # API client
│   │   └── ...
│   └── package.json
└── docker-compose.yml
```

## License

MIT
