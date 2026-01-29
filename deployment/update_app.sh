#!/bin/bash

echo "🚀 Starting Seamless Update..."

# 1. Rebuild the image separately (does not stop current container)
echo "🛠️  Building new image..."
docker compose build web

# 2. Swap containers
# This stops the old container and starts the new one immediately.
# Downtime is limited only to the startup time of FastAPI (~1-2 seconds).
echo "🔄 Swapping containers..."
docker compose up -d --no-deps web

# 3. Cleanup old images to save space
docker image prune -f

echo "✅ Update Complete!"
#```

#**How to use:**
#1.  Make your code changes in `backend/src/...`.
#2.  Run: `bash update_app.sh`

#---

### 3. True Zero Downtime (Advanced)

#If you absolutely cannot afford even 1 second of downtime, you must run multiple copies of your app. Since we are using Nginx, we can scale the app container.

#**Step 1: Update `nginx/nginx.conf`**
#Ensure your Nginx upstream block looks like this (it relies on Docker's internal DNS):

#```nginx
#upstream fastapi_app {
#    server web:8000;
#}
#```

#**Step 2: The Rolling Update Command**
#Run this manually when you need a zero-downtime update:

#```bash
# 1. Build the new image
#docker compose build web

# 2. Start a 2nd container with the new image (Old one keeps running)
#docker compose up -d --scale web=2 --no-recreate

# 3. Wait for the new container to be healthy (approx 10s)
#echo "Waiting for new container to initialize..."
#sleep 10

# 4. Stop the old container (Nginx will automatically route to the new one)
# Note: Identify the old container ID manually or simply scale down if Docker is smart enough (Docker Compose usually kills the newest, so this is tricky).
# The safest simple way is usually sufficient (Strategy #2 above).