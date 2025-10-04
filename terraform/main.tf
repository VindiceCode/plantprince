terraform {
  required_version = ">= 1.0"
  required_providers {
    digitalocean = {
      source  = "digitalocean/digitalocean"
      version = "~> 2.0"
    }
  }
}

# Configure the DigitalOcean Provider
provider "digitalocean" {
  token = var.do_token
}

# Create a DigitalOcean Spaces bucket for garden planner logs and data
resource "digitalocean_spaces_bucket" "garden_planner_storage" {
  name   = var.bucket_name
  region = var.region

  # Enable versioning for data protection
  versioning {
    enabled = true
  }

  # Configure CORS for web application access
  cors_rule {
    allowed_headers = ["*"]
    allowed_methods = ["GET", "PUT", "POST", "DELETE", "HEAD"]
    allowed_origins = var.allowed_origins
    max_age_seconds = 3000
  }

  # Lifecycle configuration to manage storage costs
  lifecycle_rule {
    id      = "log_cleanup"
    enabled = true

    # Clean up old log files after 90 days
    expiration {
      days = 90
    }

    # Move to cheaper storage after 30 days
    noncurrent_version_expiration {
      days = 30
    }
  }

  # Force destroy for development/testing (remove for production)
  force_destroy = var.force_destroy
}

# Create a CDN endpoint for the Spaces bucket (optional, for serving static assets)
resource "digitalocean_cdn" "garden_planner_cdn" {
  count  = var.enable_cdn ? 1 : 0
  origin = digitalocean_spaces_bucket.garden_planner_storage.bucket_domain_name

  # Custom subdomain (optional)
  custom_domain = var.cdn_custom_domain

  # TTL settings
  ttl = var.cdn_ttl
}

# Create Spaces access keys for the application
resource "digitalocean_spaces_bucket_object" "readme" {
  region       = digitalocean_spaces_bucket.garden_planner_storage.region
  bucket       = digitalocean_spaces_bucket.garden_planner_storage.name
  key          = "README.md"
  content      = local.readme_content
  content_type = "text/markdown"

  # Make it publicly readable
  acl = "public-read"
}

# Local values for content
locals {
  readme_content = <<-EOT
# Smart Garden Planner Storage

This DigitalOcean Spaces bucket is used for storing:

- User request/response logs
- Generated garden plans (optional backup)
- Application data and assets

## Structure

```
/logs/
  /requests/          # API request logs
  /responses/         # LLM response logs
  /errors/           # Error logs
/backups/            # Database backups (if needed)
/assets/             # Static assets (if needed)
```

## Access

This bucket is configured with appropriate CORS settings for web application access.
Access keys are managed through Terraform and should be stored securely.

Created: ${timestamp()}
EOT
}