# Get current GCP project data
data "google_project" "current" {}

locals {
  name_prefix = "${var.project_name}-${var.environment}"
  
  common_labels = {
    project     = var.project_name
    environment = var.environment
    managed_by  = "terraform"
  }
}

# Storage bucket for conversation memory
resource "google_storage_bucket" "memory" {
  name          = "${local.name_prefix}-memory-${data.google_project.current.number}"
  location      = var.region
  force_destroy = true
  
  uniform_bucket_level_access = true
  
  labels = local.common_labels
}

# Storage bucket for frontend static website
resource "google_storage_bucket" "frontend" {
  name          = "${local.name_prefix}-frontend-${data.google_project.current.number}"
  location      = var.region
  force_destroy = true
  
  uniform_bucket_level_access = true
  
  website {
    main_page_suffix = "index.html"
    not_found_page   = "index.html"
  }
  
  cors {
    origin          = ["*"]
    method          = ["GET", "HEAD", "OPTIONS"]
    response_header = ["*"]
    max_age_seconds = 3600
  }
  
  labels = local.common_labels
}

# Make frontend bucket public
resource "google_storage_bucket_iam_member" "frontend_public" {
  bucket = google_storage_bucket.frontend.name
  role   = "roles/storage.objectViewer"
  member = "allUsers"
}

# Artifact Registry repository for Docker images
resource "google_artifact_registry_repository" "repo" {
  location      = var.region
  repository_id = "${local.name_prefix}-repo"
  format        = "DOCKER"
  
  labels = local.common_labels
}

# Build and push Docker image
resource "null_resource" "docker_build" {
  triggers = {
    dockerfile_hash = filemd5("${path.module}/../backend/Dockerfile")
    main_py_hash    = filemd5("${path.module}/../backend/main.py")
    requirements_hash = filemd5("${path.module}/../backend/requirements.txt")
  }

  provisioner "local-exec" {
    command = <<-EOT
      cd ${path.module}/../backend
      gcloud builds submit \
        --tag ${var.region}-docker.pkg.dev/${data.google_project.current.project_id}/${google_artifact_registry_repository.repo.name}/${var.project_name}:latest \
        --project ${data.google_project.current.project_id}
    EOT
  }

  depends_on = [google_artifact_registry_repository.repo]
}

# Cloud Run service
resource "google_cloud_run_v2_service" "api" {
  name     = "${local.name_prefix}-api"
  location = var.region

  template {
    containers {
      image = "${var.region}-docker.pkg.dev/${data.google_project.current.project_id}/${google_artifact_registry_repository.repo.name}/${var.project_name}:latest"
      
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
