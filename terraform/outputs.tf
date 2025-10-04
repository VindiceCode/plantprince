# Spaces bucket information
output "bucket_name" {
  description = "Name of the created Spaces bucket"
  value       = digitalocean_spaces_bucket.garden_planner_storage.name
}

output "bucket_domain_name" {
  description = "Domain name of the Spaces bucket"
  value       = digitalocean_spaces_bucket.garden_planner_storage.bucket_domain_name
}

output "bucket_urn" {
  description = "URN of the Spaces bucket"
  value       = digitalocean_spaces_bucket.garden_planner_storage.urn
}

output "bucket_region" {
  description = "Region of the Spaces bucket"
  value       = digitalocean_spaces_bucket.garden_planner_storage.region
}

# CDN information (if enabled)
output "cdn_endpoint" {
  description = "CDN endpoint URL (if CDN is enabled)"
  value       = var.enable_cdn ? digitalocean_cdn.garden_planner_cdn[0].endpoint : null
}

output "cdn_custom_domain" {
  description = "CDN custom domain (if configured)"
  value       = var.enable_cdn && var.cdn_custom_domain != null ? digitalocean_cdn.garden_planner_cdn[0].custom_domain : null
}

# Environment variables for application
output "env_variables" {
  description = "Environment variables to set in your application"
  value = {
    DO_SPACES_ENDPOINT = "https://${var.region}.digitaloceanspaces.com"
    DO_SPACES_REGION   = var.region
    DO_SPACES_BUCKET   = digitalocean_spaces_bucket.garden_planner_storage.name
    DO_SPACES_URL      = "https://${digitalocean_spaces_bucket.garden_planner_storage.bucket_domain_name}"
  }
  sensitive = false
}

# Instructions for setting up access keys
output "setup_instructions" {
  description = "Instructions for completing the setup"
  value = <<-EOT
    
    🌱 Smart Garden Planner - DigitalOcean Spaces Setup Complete!
    
    Next steps:
    
    1. Create Spaces access keys in DigitalOcean console:
       - Go to: https://cloud.digitalocean.com/account/api/spaces
       - Click "Generate New Key"
       - Copy the Access Key ID and Secret Access Key
    
    2. Update your .env file with these values:
       DO_SPACES_KEY=your_access_key_id_here
       DO_SPACES_SECRET=your_secret_access_key_here
       DO_SPACES_ENDPOINT=https://${var.region}.digitaloceanspaces.com
       DO_SPACES_REGION=${var.region}
       DO_SPACES_BUCKET=${digitalocean_spaces_bucket.garden_planner_storage.name}
    
    3. Your bucket is ready at:
       ${digitalocean_spaces_bucket.garden_planner_storage.bucket_domain_name}
    
    4. Test the setup by running your application with Docker:
       docker-compose up --build
    
    📝 Note: Keep your access keys secure and never commit them to version control!
    
  EOT
}

# Terraform state information
output "terraform_workspace" {
  description = "Current Terraform workspace"
  value       = terraform.workspace
}