# YouTube Digital Personality Analyzer

YouTube Digital Personality Analyzer is a modern, full-stack web application that securely parses a user's YouTube activity (subscriptions, liked videos, or offline watch histories) to generate detailed cognitive interest scores, learning vs. entertainment splits, and a personalized AI Digital Personality Report.

---

## Technical Architecture

### Frontend
- **React (Vite)**: Fast, modern SPA framework.
- **Tailwind CSS v4**: Modern CSS-first utility classes and dark-theme configurations.
- **Recharts**: Responsive data visualization (Donut chart for interest shares, Bar chart for monthly comparison, Line chart for interest evolution).
- **jsPDF & html2canvas**: High-fidelity client-side PDF export of generated profiles.

### Backend
- **Flask (Python 3.13+)**: Lightweight REST API.
- **Pandas & NumPy**: High-performance categorizations and statistical score generators.
- **google-api-python-client**: Live integration with the YouTube Data API v3.
- **SQLAlchemy (SQLite)**: Datastore for persisting user profiles and analysis runs over months.
- **Google Generative AI**: Gemini 1.5 Flash integrations for advanced personality summaries.

---

## Directory Structure

```
youtube-analyzer/
│
├── backend/
│   ├── app.py             # Flask application & routing entry point
│   ├── config.py          # Configuration loading (.env)
│   ├── database.py        # SQLAlchemy models (User, Analysis)
│   ├── youtube_service.py # Google API wrapper for YouTube read lists
│   ├── analyzer.py        # Heuristic classifier, scores, & AI report compiler
│   ├── .env.template      # Environment parameters template
│   ├── .env               # Local environment configuration file
│   ├── requirements.txt   # Python dependencies list
│   └── tests/
│       └── test_analyzer.py # Python test suite
│
├── frontend/
│   ├── index.html         # SEO metadata, titles, and Google Fonts
│   ├── vite.config.js     # React + Tailwind v4 + Dev server proxy config
│   ├── package.json       # React libraries list
│   └── src/
│       ├── main.jsx       # React mount point
│       ├── App.jsx        # Routing, login flows, and global state
│       ├── index.css      # Tailwind directives & CSS theme setup
│       ├── App.css        # Base empty styles
│       ├── components/
│       │   ├── Navbar.jsx            # Action header with profile capsule
│       │   ├── MetricCard.jsx        # Interactive radial and scoring cards
│       │   ├── CategoryCharts.jsx    # Pie, comparative Bar, and Line charts
│       │   ├── PersonalityReport.jsx # Formatted profile badge and narrative
│       │   └── TakeoutUpload.jsx     # Dropzone for watch-history.json upload
│       └── pages/
│           ├── LandingPage.jsx       # Hero landing page & auth triggers
│           └── Dashboard.jsx         # Tabs workspace with PDF export
```

---

## Quick Start (Local Development)

### 1. Prerequisite Checklist
- **Python**: Version 3.13 or newer.
- **Node.js & npm**: Modern version.

### 2. Backend Setup
1. Open a terminal in the `backend/` directory:
   ```bash
   cd backend
   ```
2. Install Python dependencies:
   ```bash
   pip install -r requirements.txt
   ```
3. Run the development Flask server (runs on port `5000`):
   ```bash
   python app.py
   ```

### 3. Frontend Setup
1. Open a new terminal in the `frontend/` directory:
   ```bash
   cd frontend
   ```
2. Install Node.js packages:
   ```bash
   npm install
   ```
3. Start the dev client (Vite automatically proxies `/api` calls to port `5000`):
   ```bash
   npm run dev
   ```
4. Open your browser and navigate to `http://localhost:5173/`.

### 4. Interactive Review
- Click **Explore with Demo Mode** on the login page to immediately populate the dashboard with realistic sample data, enabling full testing of the charts, month-over-month comparisons, and PDF downloads without requiring Google OAuth configurations.

---

## API & Google OAuth Setup

To enable real Google Sign-In and fetch user data directly:

### 1. Register Google Cloud Credentials
1. Go to the [Google Cloud Console](https://console.cloud.google.com/).
2. Create a new project named `YouTube Personality Analyzer`.
3. Search for the **YouTube Data API v3** in the API Library and click **Enable**.
4. Go to **OAuth consent screen**:
   - Set User Type to **External**.
   - Input developer emails and name.
   - Under **Scopes**, click *Add or Remove Scopes* and add:
     - `.../auth/youtube.readonly` (View YouTube activity details)
     - `.../auth/userinfo.profile` (View basic profile details)
     - `.../auth/userinfo.email` (View primary email)
   - Add your email as a **Test User** (since your app will be in Testing mode).
5. Go to **Credentials**:
   - Click *Create Credentials* -> *OAuth client ID*.
   - Set Application Type to **Web application**.
   - Under **Authorized redirect URIs**, add:
     ```
     http://localhost:5000/api/auth/callback
     ```
   - Click Save, then copy the generated **Client ID** and **Client Secret**.

### 2. Configure Backend Variables
Update the values in `backend/.env`:
```ini
SECRET_KEY=generate-a-secure-random-key-here
DATABASE_URL=sqlite:///youtube_analyzer.db

GOOGLE_CLIENT_ID=your_copied_client_id.apps.googleusercontent.com
GOOGLE_CLIENT_SECRET=your_copied_client_secret
GOOGLE_REDIRECT_URI=http://localhost:5000/api/auth/callback

# Optional: Add to trigger real AI summaries using Gemini models
GEMINI_API_KEY=your_gemini_api_key_from_google_ai_studio
```

---

## Offline Import via Google Takeout

If a user prefers an completely offline report or wants to analyze their full viewing history:
1. Go to [Google Takeout](https://takeout.google.com/).
2. Select **YouTube and YouTube Music** only.
3. Choose **JSON** as the export format (instead of HTML) for your activity data.
4. Download and unzip the archive.
5. In the app's **Takeout Import** tab, drag and drop the `watch-history.json` file.
6. The backend will parse the history list, classify categories, and update the dashboard results.
