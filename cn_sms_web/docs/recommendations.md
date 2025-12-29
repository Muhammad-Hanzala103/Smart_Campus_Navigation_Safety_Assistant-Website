# Prioritized Recommendations & Missing Items

## 1. Safety & Security (Critical)
- **[CRITICAL] CORS Policy**: Currently `CORS(app, resources={r"/api/*": {"origins": "*"}})`. This allows ANY website to make requests to your API.
  - *Fix*: Change to `origins=["https://your-frontend-domain.com", "http://localhost:5000"]`.
- **[HIGH] Secret Keys**: `SECRET_KEY` is likely hardcoded or defaulted in `config.py`.
  - *Fix*: Ensure production uses `os.environ.get('SECRET_KEY')` and it is NEVER committed to git.
- **[MEDIUM] Image Uploads**: No strict file size limit implemented in `app.py`.
  - *Fix*: Add `app.config['MAX_CONTENT_LENGTH'] = 5 * 1024 * 1024` (5MB).

## 2. Missing Features (Action Required)
- **AI Model**: The file `ai_analyzer.py` is a STUB. It generates random numbers.
  - *Action*: Connect to Hugging Face Inference API or TensorFlow Lite model for real detection.
- **Email Service**: Forgot password generates tokens in logs but does not send emails.
  - *Action*: Integrate `Flask-Mail` with SMTP credentials.
- **Map Editor**: The `map_editor.html` page exists but lacks JS logic to save nodes.
  - *Action*: Implement drag-and-drop JS and `POST /api/map/nodes` endpoint.

## 3. Deployment & DevOps
- **Docker**: Dockerfile exists but no `docker-compose.yml` for DB + App.
  - *Action*: Create `docker-compose.yml` to spin up everything easily.
- **HTTPS**: Not configured.
  - *Action*: Use Nginx as a reverse proxy with Let's Encrypt SSL.

## 4. UI/UX Improvements
- **Mobile**: Login input fields are small on mobile. Increase padding.
- **Feedback**: Add "Loading..." spinners when submitting heavy images.
