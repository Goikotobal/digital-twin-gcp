# Cloud Run Deployment - Complete Step-by-Step Guide

## Context
We're switching from Cloud Functions to Cloud Run to avoid Python dependency issues.
Cloud Run uses Docker containers, which gives us full control over the environment.

## Current Status
✅ Dockerfile created
✅ Flask-based main.py created
✅ requirements.txt updated
✅ All files in ~/projects/production/digital-twin-gcp/backend/

## Files Created

### backend/Dockerfile
```dockerfile
FROM python:3.11-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY main.py .
EXPOSE 8080
CMD exec gunicorn --bind :8080 --workers 1 --threads 8 --timeout 0 main:app
```

### backend/requirements.txt
```
flask==3.0.0
gunicorn==21.2.0
anthropic==0.39.0
```

### backend/main.py
Flask app with:
- POST / endpoint for chat
- CORS headers
- In-memory conversation storage
- Anthropic API integration
- Health check endpoint

---

## STEP 2: Update Terraform for Cloud Run (20 minutes)

### Location
`~/projects/production/digital-twin-gcp/terraform/`

### 2.1: Update main.tf

Replace the Cloud Functions section with Cloud Run:
```hcl
# Build and push Docker image to Artifact Registry
resource "null_resource" "docker_build" {
  triggers = {
    dockerfile_hash = filemd5("${path.module}/../backend/Dockerfile")
    main_py_hash    = filemd5("${path.module}/../backend/main.py")
  }

  provisioner "local-exec" {
    command = <<-EOT
      cd ${path.module}/../backend
      gcloud builds submit \
        --tag ${var.region}-docker.pkg.dev/${data.google_project.current.project_id}/${google_artifact_registry_repository.repo.name}/${var.project_name}-${var.environment}:latest \
        .
    EOT
  }

  depends_on = [google_artifact_registry_repository.repo]
}

# Artifact Registry repository
resource "google_artifact_registry_repository" "repo" {
  location      = var.region
  repository_id = "${local.name_prefix}-repo"
  format        = "DOCKER"
  
  labels = local.common_labels
}

# Cloud Run service
resource "google_cloud_run_v2_service" "api" {
  name     = "${local.name_prefix}-api"
  location = var.region

  template {
    containers {
      image = "${var.region}-docker.pkg.dev/${data.google_project.current.project_id}/${google_artifact_registry_repository.repo.name}/${var.project_name}-${var.environment}:latest"
      
      env {
        name  = "ANTHROPIC_API_KEY"
        value = var.anthropic_api_key
      }
      
      env {
        name  = "ENVIRONMENT"
        value = var.environment
      }
      
      resources {
        limits = {
          cpu    = "1"
          memory = "512Mi"
        }
      }
    }
    
    scaling {
      min_instance_count = 0
      max_instance_count = 10
    }
  }

  labels = local.common_labels

  depends_on = [null_resource.docker_build]
}

# Make Cloud Run service publicly accessible
resource "google_cloud_run_service_iam_member" "public" {
  service  = google_cloud_run_v2_service.api.name
  location = google_cloud_run_v2_service.api.location
  role     = "roles/run.invoker"
  member   = "allUsers"
}
```

### 2.2: Update outputs.tf
```hcl
output "function_url" {
  description = "URL of the Cloud Run service"
  value       = google_cloud_run_v2_service.api.uri
}

output "frontend_bucket_name" {
  description = "Name of the frontend bucket"
  value       = google_storage_bucket.frontend.name
}

output "frontend_url" {
  description = "Public URL of the frontend website"
  value       = "https://storage.googleapis.com/${google_storage_bucket.frontend.name}/index.html"
}

output "memory_bucket_name" {
  description = "Name of the memory bucket"
  value       = google_storage_bucket.memory.name
}
```

### 2.3: Update deploy.sh
```bash
#!/bin/bash
set -e

ENVIRONMENT=${1:-dev}
PROJECT_ID="upbeat-arch-477806-k8"

echo "🚀 Deploying to $ENVIRONMENT..."

# Check API key
if [ -z "$ANTHROPIC_API_KEY" ]; then
  echo "❌ Error: ANTHROPIC_API_KEY not set"
  exit 1
fi

# Initialize Terraform
echo "🔧 Initializing Terraform..."
terraform init -input=false

# Select workspace
if terraform workspace list 2>/dev/null | grep -q "$ENVIRONMENT"; then
  terraform workspace select $ENVIRONMENT
else
  terraform workspace new $ENVIRONMENT
fi

# Apply
echo "🚀 Deploying infrastructure..."
terraform apply \
  -var="environment=$ENVIRONMENT" \
  -var="anthropic_api_key=$ANTHROPIC_API_KEY" \
  -auto-approve

# Show outputs
echo ""
echo "✅ Deployment complete!"
echo ""
terraform output
```

---

## STEP 3: Enable Required APIs (5 minutes)
```bash
gcloud services enable \
  artifactregistry.googleapis.com \
  cloudbuild.googleapis.com \
  run.googleapis.com
```

---

## STEP 4: Deploy to Cloud Run (30 minutes)

### 4.1: Navigate and deploy
```bash
cd ~/projects/production/digital-twin-gcp/terraform
./deploy.sh dev
```

### Expected output:
- Building Docker image (5-10 min)
- Uploading to Artifact Registry
- Creating Cloud Run service
- Setting IAM permissions
- Output with service URL

### 4.2: Test the deployment
```bash
# Get the URL
SERVICE_URL=$(terraform output -raw function_url)

# Test with curl
curl -X POST $SERVICE_URL \
  -H "Content-Type: application/json" \
  -d '{"message": "Hello, my name is Alex", "sessionId": "test123"}'
```

**Expected response:**
```json
{
  "response": "Hello Alex! It's nice to meet you...",
  "sessionId": "test123"
}
```

---

## STEP 5: Update Frontend (10 minutes)

### 5.1: Update frontend with new URL
```bash
cd ~/projects/production/digital-twin-gcp/frontend

# Get Cloud Run URL
SERVICE_URL=$(cd ../terraform && terraform output -raw function_url)

# Update HTML
sed -i "s|const API_URL = .*|const API_URL = '$SERVICE_URL';|" index.html

# Verify
grep "API_URL" index.html
```

### 5.2: Upload to Cloud Storage
```bash
FRONTEND_BUCKET=$(cd ../terraform && terraform output -raw frontend_bucket_name)
gsutil cp index.html gs://$FRONTEND_BUCKET/

# Get frontend URL
terraform output frontend_url
```

### 5.3: Test in browser

Open the frontend URL and try:
1. "Hello"
2. "My name is [your name]"
3. "What did I just tell you?" (test memory)

---

## STEP 6: Document Success (10 minutes)

### 6.1: Update PROGRESS.md
```bash
cd ~/projects/production/digital-twin-gcp

cat >> PROGRESS.md << 'PROGRESS'

## ✅ Cloud Run Deployment - SUCCESS!

### Date: [Current Date]

**What We Did:**
1. Created Dockerfile for containerized deployment
2. Switched from Cloud Functions to Cloud Run
3. Updated Terraform configuration
4. Successfully deployed working backend
5. Connected frontend to Cloud Run service

**Results:**
- ✅ Backend responding correctly
- ✅ Frontend working end-to-end
- ✅ Conversations working with memory
- ✅ No dependency issues!

**URLs:**
- Frontend: [paste your URL]
- Backend: [paste your URL]

**Why Cloud Run is Better:**
- No Python dependency conflicts
- Full control over environment
- More professional approach
- Scales automatically
- Industry-standard containerization

**Key Learning:**
- Docker containerization
- Flask web framework
- Cloud Run deployment
- Infrastructure as Code with containers
- Professional serverless architecture

PROGRESS

git add -A
git commit -m "Successfully deployed to Cloud Run!"
```

---

## TROUBLESHOOTING

### If Docker build fails:
```bash
# Check Docker is installed
docker --version

# If not, Cloud Build will handle it (no local Docker needed)
```

### If Artifact Registry fails:
```bash
# Enable the API
gcloud services enable artifactregistry.googleapis.com

# Check permissions
gcloud projects get-iam-policy upbeat-arch-477806-k8
```

### If Cloud Run deployment fails:
```bash
# Check logs
gcloud run services logs read tuin-dev-api --region=us-central1

# Check service status
gcloud run services describe tuin-dev-api --region=us-central1
```

### If API returns 500:
```bash
# Check Cloud Run logs
gcloud run services logs read tuin-dev-api --region=us-central1 --limit=50

# Verify environment variables
gcloud run services describe tuin-dev-api --region=us-central1 --format="get(spec.template.spec.containers[0].env)"
```

---

## COST TRACKING

**Cloud Run Costs:**
- First 2 million requests/month: FREE
- 360,000 GB-seconds memory: FREE
- 180,000 vCPU-seconds: FREE

**We're well within free tier!**

---

## NEXT: Day 5 - CI/CD

Once Cloud Run is working:
1. Set up GitHub Actions
2. Automate Docker builds
3. Auto-deploy on push
4. Add testing pipeline

See: `day5_cicd_guide.md`

---

## Quick Reference Commands
```bash
# Deploy
cd ~/projects/production/digital-twin-gcp/terraform
./deploy.sh dev

# Check status
gcloud run services list

# View logs
gcloud run services logs read tuin-dev-api --region=us-central1

# Destroy everything
terraform destroy -var="anthropic_api_key=$ANTHROPIC_API_KEY" -auto-approve

# Test backend
curl -X POST $(terraform output -raw function_url) \
  -H "Content-Type: application/json" \
  -d '{"message": "test", "sessionId": "123"}'
```

---

## SUCCESS CRITERIA

✅ Docker image builds successfully
✅ Cloud Run service deploys
✅ Backend returns JSON with "response" key
✅ Frontend connects and shows responses
✅ Conversation memory works within session
✅ No typing_extensions errors!

---

**Estimated Total Time: 90 minutes**

**You've got this!** 🚀
