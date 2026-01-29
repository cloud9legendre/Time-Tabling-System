# Computer Lab Timetabling System (CLTS)

A robust, web-based application designed to streamline the scheduling of computer laboratories. It manages conflicts, enforces resource constraints, and provides a seamless booking experience for instructors and administrators.

## 🚀 Features

- **Smart Scheduling**: Automatically detects hard conflicts (e.g., double booking a lab or instructor) to prevent scheduling errors.
- **Role-Based Access Control**:
  - **Admin/Super Admin**: Full control to manage Labs, Modules, Instructors, and all Bookings.
  - **Instructor**: View personal schedule, request bookings (if configured), and export calendars.
- **Resource Management**: CRUD operations for Labs, Modules, and Instructors.
- **Security**:
  - **JWT Authentication**: Secure stateless sessions.
  - **CSRF Protection**: Defends against Cross-Site Request Forgery.
  - **Rate Limiting**: Protects against brute-force attacks on login.
  - **SSL/HTTPS**: Deployed behind Nginx with SSL termination.
- **Export Capabilities**: Export schedules to ICS (Calendar) format.

## 🛠 Technology Stack

- **Backend**: Python 3.10, FastAPI, SQLAlchemy
- **Database**: PostgreSQL 14
- **Frontend**: Jinja2 Templates (Server-Side Rendering) + Vanilla CSS
- **Infrastructure**: Docker, Docker Compose, Nginx (Reverse Proxy)

## 📋 Prerequisites

- **Docker Desktop** (installed and running)
- **Git** (for version control)

## ⚡ Quick Start (Local Deployment)

1. **Clone the Repository**

    ```bash
    git clone <repository_url>
    cd lab-timetabling-system
    ```

2. **Configure Environment**
    - Navigate to `backend/` and rename `.env.example` to `.env` (if applicable) or verify the existing `.env`.
    - *Note: Default credentials are pre-configured for local dev.*

3. **Generate SSL Certificates**
    The system uses Nginx with SSL. For local development, generate self-signed certificates:

    ```bash
    cd deployment
    bash generate_certs.sh
    ```

4. **Run with Docker Compose**
    Build and start the services:

    ```bash
    docker compose up -d --build
    ```

5. **Access the Application**
    Open your browser to:
    - **<https://localhost>**
    - *Note: You will see a security warning because of the self-signed certificate. Advanced/Proceed to access the site.*

## 🔑 Default Credentials

- **Email**: `admin@uom.lk`
- **Password**: `password123`

## 🌿 Data Seeding

To populate the database with comprehensive test data (Departments, Labs, Instructors, and Modules):

```bash
cd deployment
# Use cat (Git Bash/Linux) or type (PowerShell) to pipe the SQL file into psql
cat ../database/seed.sql | docker compose exec -T db psql -U admin -d lab_timetabling_db
```

*Note: Default Admin credentials are `admin@uom.lk` / `password123`*

## 📂 Project Structure

lab-timetabling-system/
├── backend/
│   ├── src/
│   │   ├── api/        # Main API endpoints
│   │   ├── auth/       # Security (JWT, CSRF)
│   │   ├── models/     # Database Models
│   │   └── templates/  # HTML Templates
│   ├── verify_auth.py  # Verification Script
│   └── requirements.txt
├── deployment/
│   ├── docker-compose.yml
│   ├── nginx/          # Nginx Config
│   └── generate_certs.sh
└── tests/              # Test Suite

## 🛡️ Security

This project implements modern security best practices:

- **Environment Variables**: Secrets are not hardcoded.
- **Hashing**: Passwords are hashed using bcrypt (via passlib).
- **Protection**: Middleware enforces CSRF checks and Rate Limits (5 login attempts/min).

## 📝 Development

To verify the deployment or run tests:

```bash
# Run the authentication verification script inside the container
cd deployment
docker compose exec -e BASE_URL=https://nginx web python /app/verify_auth.py
```
