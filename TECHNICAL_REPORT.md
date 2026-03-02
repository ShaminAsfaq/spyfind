# Technical Report: Spyfind System Expansion & ML Integration

## 1. Executive Summary
This report details the technical transformation of the Spyfind platform into a high-scale bot detection and management system. Key accomplishments include the ingestion of 3.6M+ records, implementation of a machine learning prediction pipeline, and the optimization of database architectures to maintain sub-second latency across massive datasets.

---

## 2. Database Schema & Data Engineering

### 2.1. Ground Truth Implementation
To support supervised learning and system verification, a new relational model was introduced:
*   **Model**: `BotDetection`
*   **Fields**: `user_id` (FK), `is_bot` (Boolean), `source` (String), `created_at` (DateTime).
*   **Initialization**: A migration script identified 3,479 pre-existing users and categorized them as "Humans" to establish a baseline.

### 2.2. High-Volume Data Ingestion
A multi-threaded capable ingestion pipeline was developed to process external CSV datasets:
*   **User Migration**: Successfully imported 7,543 bot profiles, mapping disparate CSV headers to the SQLAlchemy `User` ORM.
*   **Content Ingestion**: Processed over **3,602,227 tweets** (roars).
*   **Automated Feature Extraction**: Implemented regex-based hashtag extraction during ingestion to populate the many-to-many `tweet_hashtag` association table dynamically.

---

## 3. Performance Optimization & Scalability

### 3.1. Database Indexing
To resolve a 60-second latency issue identified during hashtag lookups, strategic B-Tree indexes were applied:
*   `idx_tweet_hashtag_tweet_id`
*   `idx_tweet_hashtag_hashtag_id`
*   `idx_tweets_author_id`

### 3.2. Query Optimization
Backend logic in `app/crud.py` was refactored to utilize the association table directly for aggregate functions (e.g., `COUNT`), bypassing expensive joins on the 3.6M row `tweets` table.

### 3.3. Frontend Pagination & Intersection Observer
To ensure a responsive UI, the "load-all" approach was replaced with an **Infinite Scroll** architecture:
*   **Batch Size**: 20 roars per request.
*   **Technology**: `IntersectionObserver` API used to trigger asynchronous fetch calls to the new `/api/hashtags/{id}/tweets` endpoint.

---

## 4. Machine Learning Integration

### 4.1. Environment & Dependencies
The runtime environment was upgraded to support scikit-learn modules, specifically integrating `numpy`, `pandas`, `joblib`, and `scikit-learn`.

### 4.2. Feature Engineering Logic
A deterministic calculation engine was implemented to generate 5 key features from the SQL database:
1.  **Statuses Count**: Total published content.
2.  **Followers Count**: Inbound social graph.
3.  **Friends Count**: Outbound social graph.
4.  **Reputation**: $\frac{Followers}{Followers + Friends + 1}$
5.  **Post-to-Follower Ratio**: $\frac{Statuses}{Followers + 1}$

### 4.3. Model Deployment
The pre-trained **Decision Tree Classifier** (`bot_detector.pkl`) was deployed via `joblib`. A production-ready prediction endpoint was added to `app/routes.py` to provide real-time inference.

---

## 5. User Interface & System Management

### 5.1. Bot Detector Panel
A specialized dashboard was developed for single-user inference. Features include:
*   Real-time feature calculation display.
*   Model prediction output (BOT/HUMAN).
*   Deep-linking to full profiles in new browser tabs.

### 5.2. Admin Panel Enhancements
The primary User Management Panel was upgraded for high-density data management:
*   **Status Indicators**: Icons (🤖/👤) mapping directly to the database ground truth.
*   **Data Filtering**: Implemented server-side filtering for bot/human categorization.
*   **Utility Tools**: Integrated a "Copy to Clipboard" feature for usernames and optimized pagination to 50 users per page.
*   **UI/UX Restoration**: Reverted to a clean, professional theme with standardized button scaling and proper layout nesting.

---

## 6. Technical Specifications
*   **Backend**: FastAPI, SQLAlchemy ORM.
*   **Database**: SQLite (Optimized with custom indexing).
*   **ML Model**: Scikit-learn DecisionTreeClassifier.
*   **Frontend**: Vanilla JavaScript (ES6+), HTML5, CSS3.
