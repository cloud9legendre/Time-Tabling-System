#!/bin/bash

echo "🚀 Starting Seamless Update..."

# 1. Rebuild the image separately (does not stop current container)
echo "🛠️  Building new image..."
docker compose build web

# 2. Swap containers
# This stops the old container and starts the new one immediately.
echo "🔄 Swapping containers..."
docker compose up -d --no-deps web

# 3. Cleanup old images to save space
docker image prune -f

echo "✅ Update Complete!"