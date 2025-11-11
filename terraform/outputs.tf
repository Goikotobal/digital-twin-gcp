output "function_url" {
  description = "URL of the Cloud Function API"
  value       = google_cloudfunctions_function.api.https_trigger_url
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
