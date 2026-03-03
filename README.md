# Vector Space - Digital Creator Ecosystem

A comprehensive platform for gamers, 3D artists, game developers, VFX creators, recruiters, and mentors.

## 🚀 Features

### Core Features
- **3D Marketplace** - Buy and sell 3D assets with secure payment processing
- **Game Publishing** - Showcase and distribute indie games with reviews and ratings
- **Job Board** - Connect recruiters with talented creators
- **Mentorship System** - Learn from experts or share your knowledge with paid sessions
- **Competitions** - Compete in challenges with leaderboards and submissions
- **Community Hub** - Social feed with voting, messaging, and networking
- **AI Assistant** - Get help with code, art, and career advice
- **Workspaces** - Collaborate on projects with teams

### New Features (v2.0)
- ✅ **Post Voting System** - Upvote/downvote community posts
- ✅ **Game Reviews** - Rate and review games with star ratings
- ✅ **Payment Integration** - Stripe payment processing for marketplace and mentorship
- ✅ **Analytics Dashboard** - Track revenue, downloads, and performance
- ✅ **Moderation Tools** - Content reporting and admin moderation dashboard
- ✅ **Transaction Management** - Wallet system for sellers and buyers
- ✅ **Secure Downloads** - Purchase verification for asset downloads

## 📋 Tech Stack

- **Backend**: Django 4.2+, Django REST Framework
- **Database**: PostgreSQL (Production), SQLite (Development)
- **Payments**: Stripe
- **Cache**: Redis
- **Task Queue**: Celery
- **Frontend**: Django Templates (Phase 1), React/Mobile (Phase 2)
- **Deployment**: Docker, Docker Compose

## 🛠️ Installation

### Prerequisites

- Python 3.12+
- PostgreSQL (for production)
- Redis (for caching and Celery)

### Quick Start

1. **Clone the repository**
```bash
git clone <repository-url>
cd vector_space
```

2. **Create virtual environment**
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. **Install dependencies**
```bash
pip install -r requirements.txt
```

4. **Configure environment**
```bash
cp .env.example .env
# Edit .env with your settings (Stripe keys, email, etc.)
```

5. **Setup database**
```bash
# Option 1: Use the automated script
python update_database.py

# Option 2: Manual setup
python manage.py makemigrations
python manage.py migrate
python manage.py createsuperuser
```

6. **Run development server**
```bash
python manage.py runserver
```

Visit http://localhost:8000

## 💳 Payment Setup (Optional)

To enable payment features:

1. Create a Stripe account at https://stripe.com
2. Get your API keys from the Stripe dashboard
3. Add to `.env`:
```env
STRIPE_SECRET_KEY=sk_test_your_key
STRIPE_PUBLIC_KEY=pk_test_your_key
STRIPE_WEBHOOK_SECRET=whsec_your_secret
```

Test card: `4242 4242 4242 4242` (any future date, any CVC)

## 📊 New Features Guide

### Analytics Dashboard
- Access: `/core/analytics/` or from user dashboard
- View revenue, downloads, and performance metrics
- Track top performing assets and games

### Moderation Tools (Staff Only)
- Access: `/core/moderation/` or from user dashboard
- Review content reports
- Take moderation actions
- Track moderation history

### Post Voting
- Upvote/downvote posts in community feed
- Vote score displayed on each post
- Click again to remove vote

### Game Reviews
- Rate games 1-5 stars
- Write detailed reviews
- Comment on games with nested replies

### Payment Processing
- Secure Stripe integration
- Automatic wallet management
- Transaction tracking
- Purchase verification

4. **Setup environment variables**
```bash
cp .env.example .env
# Edit .env with your configuration
```

5. **Setup database**
```bash
python setup_db.py
python manage.py makemigrations
python manage.py migrate
```

6. **Create superuser**
```bash
python manage.py createsuperuser
```

7. **Run development server**
```bash
python manage.py runserver
```

Visit: http://localhost:8000

## 🐳 Docker Setup

```bash
# Build and run with Docker Compose
docker-compose up --build

# Run migrations
docker-compose exec web python manage.py migrate

# Create superuser
docker-compose exec web python manage.py createsuperuser
```

## 📁 Project Structure

```
vector_space/
├── apps/
│   ├── api/              # REST API endpoints
│   ├── core/             # Core utilities and mixins
│   ├── users/            # User authentication
│   ├── marketplace/      # 3D asset marketplace
│   ├── games/            # Game publishing
│   ├── jobs/             # Job board
│   ├── mentorship/       # Mentorship system
│   ├── competitions/     # Competitions & leaderboards
│   ├── social/           # Community & messaging
│   ├── workspace/        # Team collaboration
│   └── ai_assistant/     # AI chat assistant
├── config/               # Django settings
├── templates/            # HTML templates
├── static/               # CSS, JS, images
├── media/                # User uploads
├── tests/                # Test suite
├── logs/                 # Application logs
├── docker-compose.yml    # Docker configuration
├── Dockerfile            # Docker image
├── requirements.txt      # Python dependencies
└── README.md            # This file
```

## 🔌 API Endpoints

Base URL: `/api/v1/`

### Authentication
- `POST /api/v1/auth/login/` - Login
- `POST /api/v1/auth/logout/` - Logout

### Resources
- `/api/v1/assets/` - 3D Assets
- `/api/v1/games/` - Games
- `/api/v1/jobs/` - Jobs
- `/api/v1/applications/` - Job Applications
- `/api/v1/mentors/` - Mentor Profiles
- `/api/v1/posts/` - Social Posts
- `/api/v1/messages/` - Direct Messages
- `/api/v1/competitions/` - Competitions
- `/api/v1/submissions/` - Competition Submissions

All endpoints support:
- Filtering: `?field=value`
- Search: `?search=query`
- Ordering: `?ordering=field`
- Pagination: `?page=1`

## 🧪 Testing

```bash
# Install dev dependencies
pip install -r requirements-dev.txt

# Run tests
pytest

# Run with coverage
pytest --cov=apps --cov-report=html

# View coverage report
open htmlcov/index.html
```

## 📝 Development

### Code Quality

```bash
# Format code
black .

# Sort imports
isort .

# Lint code
flake8

# Type checking
pylint apps/
```

### Database Migrations

```bash
# Create migrations
python manage.py makemigrations

# Apply migrations
python manage.py migrate

# Show migrations
python manage.py showmigrations
```

## 🚀 Deployment

### Production Checklist

- [ ] Set `DEBUG=False` in .env
- [ ] Configure PostgreSQL database
- [ ] Setup Redis for caching
- [ ] Configure email backend
- [ ] Setup AWS S3 for media files
- [ ] Configure HTTPS/SSL
- [ ] Setup domain and DNS
- [ ] Configure CORS settings
- [ ] Setup monitoring and logging
- [ ] Configure backup strategy

### Environment Variables

See `.env.example` for all required environment variables.

## 📚 Documentation

- **API Documentation**: `/api/v1/` (when running)
- **Admin Panel**: `/admin/`
- **User Guide**: Coming soon
- **Developer Guide**: Coming soon

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Write tests
5. Submit a pull request

## 📄 License

[Your License Here]

## 👥 Team

Vector Space Development Team

## 📧 Contact

- Website: [Your Website]
- Email: [Your Email]
- Discord: [Your Discord]

## 🗺️ Roadmap

### Phase 1 (Current) - Web Platform
- ✅ Core features implementation
- ✅ REST API
- ✅ User authentication
- ✅ All main modules

### Phase 2 - Mobile Apps
- [ ] React Native mobile app
- [ ] iOS app
- [ ] Android app
- [ ] Push notifications
- [ ] Offline mode

### Phase 3 - Advanced Features
- [ ] Real-time collaboration
- [ ] Video calls for mentorship
- [ ] Advanced AI features
- [ ] Payment processing
- [ ] Analytics dashboard

## 🙏 Acknowledgments

Built with Django, Django REST Framework, and modern web technologies.
