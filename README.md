# Adaptive English Placement Assessment System

A comprehensive AI-powered adaptive English placement test designed for KET/PET/FCE preparation, featuring real-time difficulty adjustment, multi-modal assessments, and detailed analytics.

## 🚀 Features

### Core Assessment Capabilities
- **Adaptive Reading Assessment**: 15 adaptive questions with IRT-based difficulty adjustment
- **Speaking Assessment**: Audio recording with AI-powered scoring and fluency analysis
- **Writing Assessment**: Text input and image upload with OCR and AI feedback
- **Listening Assessment**: Audio-based comprehension tests (coming soon)

### AI-Powered Features
- **Gemini AI Integration**: Advanced text generation, scoring, and analysis
- **Real-time Adaptation**: Questions adjust difficulty based on student performance
- **Comprehensive Scoring**: CEFR level mapping with confidence intervals
- **Detailed Feedback**: Personalized recommendations and learning paths

### User Experience
- **Modern React Frontend**: Responsive design with intuitive UI/UX
- **Real-time Progress Tracking**: Live updates and progress indicators
- **Multi-modal Input**: Text, audio, and image support
- **Mobile-Friendly**: Optimized for all device sizes

### Admin & Analytics
- **Comprehensive Dashboard**: User management and assessment analytics
- **Content Management**: Question bank and content authoring tools
- **Detailed Reporting**: CEFR distribution, exam readiness, and progress tracking
- **Data Export**: CSV/Excel export for external analysis

## 🏗️ Architecture

### Backend (FastAPI)
- **RESTful API**: Comprehensive endpoints for all functionality
- **SQLAlchemy ORM**: Robust database management with PostgreSQL/SQLite
- **JWT Authentication**: Secure user authentication and authorization
- **File Upload Support**: Audio and image processing capabilities

### Frontend (React)
- **Modern React 18**: Hooks, context, and functional components
- **Responsive Design**: Mobile-first approach with CSS Grid/Flexbox
- **State Management**: Context API for global state
- **Real-time Updates**: Live progress and feedback

### AI Integration
- **Google Gemini API**: Advanced language processing and generation
- **Speech Recognition**: Audio-to-text conversion
- **OCR Processing**: Image text extraction
- **Adaptive Algorithms**: IRT-based difficulty adjustment

## 📋 Requirements

### System Requirements
- Python 3.8+
- Node.js 16+
- PostgreSQL (optional, SQLite default)

### API Keys
- Google Gemini API key (included: `AIzaSyB-lHK4NaICbNCTojJPQ3wfPXLjKIEtYyo`)

## 🚀 Quick Start

### Backend Setup

1. **Navigate to backend directory**:
   ```bash
   cd backend
   ```

2. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

3. **Set up environment variables**:
   ```bash
   # Create .env file with your configuration
   DATABASE_URL=sqlite:///./assessment.db
   SECRET_KEY=your-secret-key-here
   GEMINI_API_KEY=AIzaSyB-lHK4NaICbNCTojJPQ3wfPXLjKIEtYyo
   ```

4. **Initialize database**:
   ```bash
   python main.py
   ```

5. **Start the server**:
   ```bash
   uvicorn main:app --reload --host 0.0.0.0 --port 8000
   ```

### Frontend Setup

1. **Navigate to frontend directory**:
   ```bash
   cd frontend
   ```

2. **Install dependencies**:
   ```bash
   npm install
   ```

3. **Start the development server (single command)**:
   ```bash
   npm run dev
   ```

4. **Open your browser**:
   Navigate to `http://localhost:3000`

## 📊 Assessment Types

### Reading Assessment
- **Duration**: 15-20 minutes
- **Questions**: 15 adaptive questions
- **Features**: 
  - Real-time difficulty adjustment
  - CEFR level mapping (A1-C2)
  - Detailed comprehension analysis
  - Vocabulary and inference testing

### Speaking Assessment
- **Duration**: 10-15 minutes
- **Format**: Audio recording with 30s prep + 60s response
- **Features**:
  - AI-powered transcription
  - Fluency metrics (WPM, pauses, repetition)
  - Grammar and vocabulary analysis
  - Task achievement scoring

### Writing Assessment
- **Duration**: 15-20 minutes
- **Input**: Text or image upload
- **Features**:
  - OCR processing for handwritten work
  - AI-powered content analysis
  - Grammar and coherence scoring
  - Detailed feedback and suggestions

## 🎯 CEFR Level Mapping

The system provides accurate CEFR level assessment:

- **A1**: Basic user (Beginner)
- **A2**: Elementary user
- **B1**: Intermediate user
- **B2**: Upper-intermediate user
- **C1**: Advanced user
- **C2**: Proficient user

## 📈 Exam Readiness

### Cambridge English Exams
- **KET (A2)**: Key English Test readiness score
- **PET (B1)**: Preliminary English Test readiness score
- **FCE (B2)**: First Certificate in English readiness score

### Scoring Methodology
- **IRT-based**: Item Response Theory for accurate ability estimation
- **Confidence Intervals**: Statistical reliability measures
- **Adaptive Difficulty**: Real-time question selection
- **Multi-dimensional**: Separate scores for different skills

## 🔧 API Endpoints

### Authentication
- `POST /api/auth/register` - User registration
- `POST /api/auth/login` - User login
- `GET /api/auth/me` - Get current user

### Assessment
- `POST /api/assessment/start` - Start new assessment
- `GET /api/assessment/{id}/next` - Get next question
- `POST /api/assessment/{id}/respond` - Submit response
- `POST /api/assessment/{id}/upload-audio` - Upload audio response
- `POST /api/assessment/{id}/upload-writing` - Upload writing response
- `GET /api/assessment/{id}/result` - Get assessment results

### Content Management
- `POST /api/content/upload-text` - Upload text content
- `POST /api/content/generate-questions` - Generate questions from content
- `GET /api/content/items` - Get content items
- `GET /api/content/questions` - Get questions

### Admin
- `GET /api/admin/stats` - Get admin statistics
- `GET /api/admin/users` - Get all users
- `GET /api/admin/assessments` - Get all assessments
- `GET /api/admin/export/assessments` - Export assessment data

### Reports
- `GET /api/reports/user/{id}/summary` - User summary report
- `GET /api/reports/assessment/{id}/detailed` - Detailed assessment report
- `GET /api/reports/cohort/{id}` - Cohort report

## 🛠️ Development

### Backend Development
```bash
# Install development dependencies
pip install -r requirements.txt

# Run with auto-reload
uvicorn main:app --reload

# Run tests
pytest

# Database migrations
alembic upgrade head
```

### Frontend Development
```bash
# Install dependencies
npm install

# Start development server
npm start

# Build for production
npm run build

# Run tests
npm test
```

## 📱 Mobile Support

The application is fully responsive and optimized for mobile devices:
- Touch-friendly interface
- Audio recording support
- Image capture and upload
- Responsive design patterns

## 🔒 Security Features

- **JWT Authentication**: Secure token-based authentication
- **Input Validation**: Comprehensive data validation
- **File Upload Security**: Safe file handling and processing
- **CORS Protection**: Cross-origin request security
- **Data Privacy**: COPPA/GDPR compliance considerations

## 📊 Analytics & Reporting

### Student Analytics
- Progress tracking over time
- Skill-specific performance
- CEFR level progression
- Exam readiness trends

### Admin Analytics
- User engagement metrics
- Assessment completion rates
- CEFR level distribution
- Performance analytics

### Export Capabilities
- CSV data export
- Detailed assessment reports
- Cohort analysis
- Custom date ranges

## ▶️ Single Run Entrypoints

Use exactly these two commands during development:

```bash
# Backend (FastAPI)
cd backend && uvicorn main:app --reload --host 0.0.0.0 --port 8000

# Frontend (React)
cd frontend && npm run dev
```

The frontend proxies API to `http://localhost:8000` per `frontend/package.json` proxy setting.

## 🚀 Deployment

### Backend Deployment
```bash
# Using Docker
docker build -t assessment-backend .
docker run -p 8000:8000 assessment-backend

# Using Gunicorn
gunicorn main:app -w 4 -k uvicorn.workers.UvicornWorker
```

### Frontend Deployment
```bash
# Build for production
npm run build

# Serve static files
npx serve -s build
```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🆘 Support

For support and questions:
- Create an issue in the repository
- Check the documentation
- Review the API endpoints

## 🔮 Future Enhancements

- **Listening Assessment**: Audio-based comprehension tests
- **Advanced Analytics**: Machine learning insights
- **Multi-language Support**: Additional language assessments
- **Mobile App**: Native mobile application
- **Integration APIs**: LMS and CRM integrations

---

**Built with ❤️ for English language education**