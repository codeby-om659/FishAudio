# 🎙️ AI Voice Timetable & Reminder API

FastAPI, MySQL, aur Fish Audio API par aadharit ek smart backend service jo users ke scheduled timetable tasks ke liye personalized, human-like voice reminders (.mp3) real-time mein generate karti hai.

---

## 🛠️ Tech Stack & Prerequisites

- *Backend Framework:* FastAPI (Python)
- *Database:* MySQL
- *Database Driver:* mysql-connector-python
- *Voice Generation API:* Fish Audio (Text-to-Speech)
- *Server:* Uvicorn

---

## 🗄️ Database Architecture

Project mein relational database structure (2 tables) ka use kiya gaya hai:

1. *users (Parent Table):* User credentials aur registration details store karne ke liye.
2. *tasks (Child Table):* Timetable/schedules store karne ke liye (user_id foreign key ke sath users table se connected with ON DELETE CASCADE).

### SQL Schema Setup

MySQL Workbench ya MySQL Command Line Client par yeh SQL script run karein:

```sql
CREATE DATABASE IF NOT EXISTS timetable_db;
USE timetable_db;

CREATE TABLE IF NOT EXISTS users (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    email VARCHAR(150) UNIQUE NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS tasks (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    title VARCHAR(255) NOT NULL,
    description TEXT,
    scheduled_time DATETIME NOT NULL,
    is_completed BOOLEAN DEFAULT FALSE,
    reminder_sent BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
);
