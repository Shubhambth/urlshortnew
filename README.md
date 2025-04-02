# URL Shortener

A modern URL shortening service built with Django and Tailwind CSS.

## Features

- URL shortening with custom aliases
- Link analytics (clicks, geolocation, device type)
- User dashboard
- Security features (malware detection, click limits)
- Modern UI with Tailwind CSS

## Setup Instructions

1. Create a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Run migrations:
```bash
python manage.py migrate
```

4. Create a superuser:
```bash
python manage.py createsuperuser
```

5. Run the development server:
```bash
python manage.py runserver
```

6. Visit http://127.0.0.1:8000/ in your browser

## Environment Variables

Create a `.env` file in the root directory with the following variables:
```
SECRET_KEY=your-secret-key
GOOGLE_SAFE_BROWSING_API_KEY=your-api-key
```

## Security Features

- Daily click limit: 15 clicks per user
- Malware detection using Google Safe Browsing API
- Rate limiting on API endpoints
- Secure password hashing
- CSRF protection 