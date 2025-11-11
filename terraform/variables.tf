variable "project_id" {
  description = "GCP Project ID"
  type        = string
  default     = "upbeat-arch-477806-k8"
}

variable "project_name" {
  description = "Name prefix for all resources"
  type        = string
  default     = "tuin"
}

variable "region" {
  description = "GCP region"
  type        = string
  default     = "us-central1"
}

variable "environment" {
  description = "Environment name (dev, test, prod)"
  type        = string
  default     = "dev"
}

variable "anthropic_api_key" {
  description = "Anthropic API key for Claude"
  type        = string
  sensitive   = true
}

variable "claude_model" {
  description = "Claude model to use"
  type        = string
  default     = "claude-3-sonnet-20240229"
}

variable "function_timeout" {
  description = "Cloud Function timeout in seconds"
  type        = number
  default     = 60
}

variable "function_memory" {
  description = "Cloud Function memory in MB"
  type        = number
  default     = 256
}

variable "function_max_instances" {
  description = "Maximum number of function instances"
  type        = number
  default     = 3
}
