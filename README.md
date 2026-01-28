# FMCSA ELD Trip Planner

Full-stack application for FMCSA Hours of Service compliant route planning and Electronic Logging Device (ELD) log generation.

## Features

- ✅ Route calculation with real-time mapping
- ✅ HOS compliance checking (11-hour driving, 14-hour window, 70-hour/8-day cycle)
- ✅ Automatic break scheduling (30-min after 8 hours)
- ✅ Multi-day trip planning
- ✅ ELD log sheet generation with visual timeline
- ✅ Professional UI/UX

## Tech Stack

**Backend:**
- Django 5.2
- Django REST Framework
- OSRM for routing (OpenStreetMap)
- SQLite database

**Frontend:**
- React 18
- Vite
- Leaflet for maps
- Axios for API calls

## Quick Start

### Backend Setup

```bash
cd backend

# Create virtual environment
python3 -m venv .venv

# Activate virtual environment
source .venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Run migrations (already done)
python manage.py migrate

# Start Django server
python manage.py runserver
```

Backend will run on: `http://localhost:8000`

### Frontend Setup

```bash
cd frontend

# Install dependencies (already done)
npm install

# Start development server
npm run dev
```

Frontend will run on: `http://localhost:5173`

## Usage

1. **Start both servers** (backend on 8000, frontend on 5173)

2. **Fill in trip details:**
   - Current location (e.g., "Richmond, VA")
   - Pickup location (e.g., "Baltimore, MD")
   - Dropoff location (e.g., "Newark, NJ")
   - Current cycle hours used (0-70)

3. **Click "Calculate Trip"**

4. **View results:**
   - Trip summary with distance and hours
   - Route map with markers
   - ELD log sheets with 24-hour timeline graphs

## HOS Regulations Implemented

- **11-Hour Driving Limit**: Maximum driving time per day
- **14-Hour Driving Window**: Total window for driving (includes breaks)
- **30-Minute Rest Break**: Required after 8 cumulative driving hours
- **10-Hour Off-Duty**: Minimum rest before starting new shift
- **70-Hour/8-Day Cycle**: Maximum on-duty hours in 8-day period

## API Endpoints

**POST /api/trips/**
- Create new trip calculation
- Returns route data and log sheets

**GET /api/trips/**
- List all trips

**GET /api/trips/{id}/**
- Get specific trip details

## Environment Variables

Create `.env` file in `frontend/` directory:

```
VITE_API_URL=http://localhost:8000/api
```

## Deployment

### Backend (Railway/Render/Heroku)

```bash
cd backend
pip freeze > requirements.txt
# Add Procfile for deployment
# Set environment variables
```

### Frontend (Vercel)

```bash
cd frontend
npm run build
# Deploy dist folder
# Set VITE_API_URL to production backend URL
```

## Sample Test Cases

**Short Trip (Single Day):**
- Current: Richmond, VA
- Pickup: Baltimore, MD
- Dropoff: Newark, NJ
- Cycle Hours: 15
- Expected: ~6-8 hours driving, 1 log sheet

**Long Trip (Multi-Day):**
- Current: Los Angeles, CA
- Pickup: Phoenix, AZ
- Dropoff: Dallas, TX
- Cycle Hours: 10
- Expected: 2-3 days, multiple log sheets

## Screenshots

(See frontend for live demo)

## License

Created for FMCSA assessment - educational purposes

## Author

Built with Django + React for FMCSA ELD Assessment
