# CIIAS - Technical Project Report

**Project Name:** Campus Integrated Intelligence & Analytics System (CIIAS)
**Version:** 2.0 (Industrial)
**Author:** Muhammad Hanzala

## 1. Executive Summary
CIIAS is a unified Smart Campus Ecosystem combining an Android Client and a Flask Web Portal. It addresses the fragmentation of university services by integrating Safety, Academics, and Logistics into one platform.

## 2. System Architecture
### 2.1 Backend (The Brain)
- **Framework:** Python Flask (Blueprint Architecture).
- **Database:** PostgreSQL (with SQLAlchemy ORM).
- **Real-time:** Socket.IO to sync App types (Web <-> Android).
- **Security:** JWT Auth, Role-Based Access Control (RBAC), Rate Limiting.

### 2.2 Android Client
- **Architecture:** MVVM (Model-View-ViewModel).
- **Maps:** OSMDroid + ARCore for Augmented Reality.
- **Optimization:** R8 Shrinking & ProGuard Obfuscation.

## 3. Key Modules Implementation

### 3.1 AI Incident Detection
- **Input:** Text/Image from Incident Report.
- **Processing:** Pre-trained HuggingFace Model (DistilBERT) for severity classification.
- **Output:** Alert Level (High/Medium/Low).

### 3.2 Smart Cafeteria (Queue Management)
- **Tech:** WebSockets.
- **Flow:** Student orders -> Server pushes Order -> Kitchen Dashboard updates instantly.

## 4. Deployment Pipeline
- **CD/CD:** GitHub -> Vercel.
- **Config:** `vercel.json` for serverless function handling.

## 5. Conclusion
The system successfully met all "Ultimate" requirements, achieving feature parity between Web and Mobile while maintaining industrial performance standards.
