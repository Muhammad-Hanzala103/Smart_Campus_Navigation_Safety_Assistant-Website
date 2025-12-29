# Presentation Slides Outline

**Title**: CNSMS - Campus Navigation & Safety System
**Time**: 5-7 Minutes

---

## Slide 1: Title & Team
- **Project Name**: CNSMS
- **Team Members**: Muhammad Hanzala, Haseeb Nawaz, [Member 3]
- **Tagline**: "Smarter Safety for a Safer Campus"

## Slide 2: The Problem
- Campus incidents (theft, medical emergencies) are hard to report quickly.
- Security officers lack real-time visibility.
- Manual reporting (phone calls) is slow and lacks location data.

## Slide 3: Our Solution
- **Mobile App**: One-tap reporting with photo & location.
- **Web Dashboard**: Live map view for security dispatch.
- **AI Intelligence**: Auto-detects severity (Fire = Critical) to prioritize response.

## Slide 4: System Architecture (Diagram)
- **Android App**: Java/Retrofit (Student facing).
- **Backend API**: Python Flask + JWT (The brain).
- **Database**: SQLite (The memory).
- **Hybrid Auth**: Secure login for both Web & Phone.

## Slide 5: Key Features (Demo)
- **Real-time Map**: Visual heatmap of danger zones.
- **AI Analysis**: "Upload a photo -> AI says 'High Risk'".
- **Status Updates**: Student gets notified when officer resolves issue.

## Slide 6: Challenges & Learning
- **Connecting Android to Localhost**: Solved using ADB Reverse Tunneling.
- **Hybrid Authentication**: Managing Cookies vs Tokens was tricky but solved.
- **AI Integration**: Designed a modular service architecture.

## Slide 7: Future Scope
- Real-time GPS tracking of officers.
- Push Notifications (Firebase) for instant alerts.
- Offline mode for report caching.

**[Thank You / Q&A]**
