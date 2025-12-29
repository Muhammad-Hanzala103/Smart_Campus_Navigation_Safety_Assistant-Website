# Prioritized Task List

**Project**: CNSMS (Campus Navigation and Safety Management System)

---

## 🔴 High Priority (Must Fix/Do)

### 1. Fix CORS Security
- **Assignee**: Muhammad Hanzala
- **Est. Time**: 1 Hour
- **Task**: In `app/__init__.py`, change `CORS` config to restrict origins. Current `*` is unsafe.
- **File**: `app/__init__.py`

### 2. Implement Real AI Model (or Better Mock)
- **Assignee**: Haseeb Nawaz
- **Est. Time**: 4 Hours
- **Task**: Update `ai_analyzer.py`. Ideally, connect to HuggingFace API (Inference API) to actually detect objects like "fire" or "weapon" instead of random return.
- **File**: `app/services/ai_analyzer.py`

### 3. User Profile Editing
- **Assignee**: Third Member
- **Est. Time**: 3 Hours
- **Task**: Create a `profile.html` page where users can change their name or password.
- **File**: `templates/dashboard/profile.html` (New File)

---

## 🟡 Medium Priority (Should Do)

### 4. Improve Map Editor
- **Assignee**: Muhammad Hanzala
- **Est. Time**: 4 Hours
- **Task**: Make `map_editor.html` functional. Allow admins to drag-and-drop nodes and save their X/Y coordinates to DB via API.
- **File**: `templates/map_editor.html`

### 5. Email Notifications
- **Assignee**: Haseeb Nawaz
- **Est. Time**: 2 Hours
- **Task**: Configure `email_service.py` to use `Flask-Mail` with a real Gmail account (using App Password) so resets actually work.
- **File**: `app/services/email_service.py`

---

## 🟢 Low Priority (Nice to Have)

### 6. Analytics Export
- **Assignee**: Third Member
- **Est. Time**: 2 Hours
- **Task**: Add a "Download CSV" button on the Dashboard for incident reports.
- **File**: `app/blueprints/dashboard.py`

### 7. Dark Mode Toggle
- **Assignee**: Shared
- **Est. Time**: 1 Hour
- **Task**: Add a JS toggle to switch CSS variables for a dark theme.
- **File**: `static/js/app.js`
