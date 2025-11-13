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

# Storage bucket for Cloud Function source code
resource "google_storage_bucket" "function_source" {
  name          = "${local.name_prefix}-function-source-${data.google_project.current.number}"
  location      = var.region
  force_destroy = true
  
  uniform_bucket_level_access = true
  
  labels = local.common_labels
}

# Upload function source
resource "google_storage_bucket_object" "function_source" {
  name   = "function-${var.environment}-source.zip"
  bucket = google_storage_bucket.function_source.name
  source = "${path.module}/../backend/function.zip"
}

# Cloud Function (Gen 1) - Much simpler and more stable
resource "google_cloudfunctions_function" "api" {
  name        = "${local.name_prefix}-api"
  description = "Digital Twin API"
  runtime     = "python39"
  region      = var.region

  available_memory_mb   = var.function_memory
  timeout               = var.function_timeout
  entry_point           = "chat_handler"
  
  source_archive_bucket = google_storage_bucket.function_source.name
  source_archive_object = google_storage_bucket_object.function_source.name

  trigger_http = true

  environment_variables = {
    MEMORY_BUCKET     = google_storage_bucket.memory.name
    BEDROCK_MODEL_ID  = var.claude_model
    ANTHROPIC_API_KEY = var.anthropic_api_key
    ENVIRONMENT       = var.environment
  }

  labels = local.common_labels
}

# Make Cloud Function publicly accessible
resource "google_cloudfunctions_function_iam_member" "invoker" {
  project        = google_cloudfunctions_function.api.project
  region         = google_cloudfunctions_function.api.region
  cloud_function = google_cloudfunctions_function.api.name
  role           = "roles/cloudfunctions.invoker"
  member         = "allUsers"
}
