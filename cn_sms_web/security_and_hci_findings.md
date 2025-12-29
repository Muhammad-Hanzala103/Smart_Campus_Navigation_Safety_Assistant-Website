# Security & HCI Findings

## Security Priorities (High/Medium)

- [Medium] **CORS Configuration**
  - **Issue**: `CORS(app, resources={r"/api/*": {"origins": "*"}})`.
  - **Risk**: Allows any website to call your API.
  - **Fix**: In `app/__init__.py`, set explicit origins from `.env`.
  - **Code**: `c:/New folder/Projects/SSNS/cn_sms_web/app/__init__.py:50`

- [Low] **Session Cookie Secure Flag**
  - **Issue**: `SESSION_COOKIE_SECURE` defaults to `False`.
  - **Risk**: Cookies sent over HTTP (not HTTPS).
  - **Fix**: Set `SESSION_COOKIE_SECURE = True` in `config.py` for production.

- [Low] **AI Model Input**
  - **Issue**: `ai_analyzer.py` currently uses random/mock data.
  - **Risk**: No validation of real input if switched to "hf" mode incorrectly.
  - **Fix**: Ensure `ai_service.py` handles API timeouts/errors gracefully.

## HCI & Usability Improvements

1.  **Action Feedback**
    - **Issue**: Some API errors return generic JSON.
    - **Fix**: Ensure `api.py` always returns `{"error": "User-friendly message"}`.
    - **Example**: Change "Invalid input" to "Password must be 8+ characters".

2.  **Map Interaction**
    - **Issue**: Pin clustering on `map.html` might be crowded.
    - **Fix**: Use Leaflet.markercluster or limit initial zoom level.

3.  **Status Page Readability**
    - **Issue**: `status.html` might use red/green colors that are hard for colorblind users.
    - **Fix**: Add icons (✅/❌) next to text status.

4.  **Login Flow on Mobile**
    - **Issue**: Input fields might be too small on Android WebView.
    - **Fix**: Add `input { font-size: 16px; }` to CSS to prevent iOS zoom and improve tap targets.
