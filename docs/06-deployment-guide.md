# Deployment Guide

This guide covers deploying the Computer Lab Timetabling System (CLTS).

**Key Architecture Note**:
This application uses **Server-Side Rendering (SSR)**.

* **Frontend**: Built with Jinja2 templates served directly by the backend.
* **Backend**: FastAPI application.
* **Database**: PostgreSQL.
* **Deployment Unit**: The Frontend and Backend are deployed together in a **single container**.

---

## ☁️ Recommended: Deploy to Fly.io

This is the fastest way to get the full stack (App + Database) running in production.

### Prerequisites

1. **Install flyctl**: [Follow Instructions Here](https://fly.io/docs/hands-on/install-flyctl/)
2. **Login**: `fly auth login`

### Step 1: Create the Database

Fly.io provides managed Postgres. We'll create this first.

```bash
# Create a new Postgres cluster
# Follow the prompts:
# - App Name: give it a unique name (e.g., clts-db-prod)
# - Configuration: Development (for free tier) or Production
fly postgres create
```

**Note**: Save the credentials displayed (Username, Password, Hostname), though Fly handles attachment automatically in the next steps.

### Step 2: Initialize the App

Navigate to the `backend/` directory where the `Dockerfile` resides.

```bash
cd backend

# Initialize the app
fly launch
```

**Prompts:**

* **App Name**: Choose a unique name (e.g., `clts-app`).
* **Region**: Pick the same region as your database.
* **Database**: **IMPORTANT!** Select the Postgres cluster you created in Step 1. Fly will automatically attach it and set the `DATABASE_URL` secret.
* **Redis**: No.
* **Deploy now?**: **NO**. We need to set a few more secrets first.

### Step 3: Configure Environment Variables

You need to set the sensitive variables required by the application.

```bash
# Generate a secure string for SECRET_KEY (e.g., use `openssl rand -hex 32` or an online generator)
fly secrets set SECRET_KEY="<your-generated-secret-key>"

# Set token expiry (minutes)
fly secrets set ACCESS_TOKEN_EXPIRE_MINUTES=60
```

### Step 4: Deploy

Now that the database is attached and secrets are set, deploy the version 1.

```bash
fly deploy
```

### Step 5: Verify & Operations

Once deployed, your app is live.

* **Visit**: Open the URL provided by Fly (e.g., `https://clts-app.fly.dev`).
* **Status**: Check logs if something goes wrong.

    ```bash
    fly logs
    ```

#### Running Database Migrations / Seeding

To run one-off scripts like seeding the database, you can SSH into the running VM.

```bash
# Open a console in the running VM
fly ssh console

# Run the python seed script (ensure seed.py is in your container)
python /app/seed_data.py  # (Adjust command based on your actual seed script location)
```

---

## 💻 Option 2: Local Deployment (Docker Compose)

Use this for local development.

1. **Generate Certs**: `cd deployment && bash generate_certs.sh`
2. **Environment**: Ensure `.env` exists in `backend/` or `deployment/`.
3. **Run**:

    ```bash
    docker compose up -d --build
    ```

4. **Access**: `https://localhost` (Accept self-signed cert warning).

---

## 🚀 Option 3: Google Cloud Run

For serverless deployments.

1. **Build**: Submit build to Google Artifact Registry.
2. **Database**: Create a **Cloud SQL** instance (Postgres).
3. **Deploy**: Use `gcloud run deploy`.
    * Must set `DATABASE_URL` to connect to Cloud SQL (often requires using the Cloud SQL Proxy or VPC Connector).
    * No sidecar Nginx needed; Cloud Run handles SSL.
