# DigitalOcean API Token
variable "do_token" {
  description = "DigitalOcean API token"
  type        = string
  sensitive   = true
}

# Spaces bucket configuration
variable "bucket_name" {
  description = "Name of the DigitalOcean Spaces bucket"
  type        = string
  default     = "garden-planner-storage"
  
  validation {
    condition     = can(regex("^[a-z0-9][a-z0-9-]*[a-z0-9]$", var.bucket_name))
    error_message = "Bucket name must be lowercase, start and end with alphanumeric characters, and can contain hyphens."
  }
}

variable "region" {
  description = "DigitalOcean region for the Spaces bucket"
  type        = string
  default     = "nyc3"
  
  validation {
    condition = contains([
      "nyc3", "ams3", "sgp1", "sfo3", "fra1"
    ], var.region)
    error_message = "Region must be one of: nyc3, ams3, sgp1, sfo3, fra1."
  }
}

# CORS configuration
variable "allowed_origins" {
  description = "List of allowed origins for CORS"
  type        = list(string)
  default     = ["*"]
}

# CDN configuration
variable "enable_cdn" {
  description = "Enable CDN for the Spaces bucket"
  type        = bool
  default     = false
}

variable "cdn_custom_domain" {
  description = "Custom domain for CDN (optional)"
  type        = string
  default     = null
}

variable "cdn_ttl" {
  description = "TTL for CDN cache in seconds"
  type        = number
  default     = 3600
}

# Environment configuration
variable "environment" {
  description = "Environment name (dev, staging, prod)"
  type        = string
  default     = "dev"
  
  validation {
    condition     = contains(["dev", "staging", "prod"], var.environment)
    error_message = "Environment must be one of: dev, staging, prod."
  }
}

variable "project_name" {
  description = "Name of the project"
  type        = string
  default     = "smart-garden-planner"
}

# Safety configuration
variable "force_destroy" {
  description = "Allow Terraform to destroy the bucket even if it contains objects (use with caution)"
  type        = bool
  default     = false
}

# Tags
variable "tags" {
  description = "Tags to apply to resources"
  type        = map(string)
  default = {
    Project     = "smart-garden-planner"
    Environment = "dev"
    ManagedBy   = "terraform"
  }
}