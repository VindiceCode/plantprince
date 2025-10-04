terraform {
  required_version = ">= 1.0"
  
  required_providers {
    digitalocean = {
      source  = "digitalocean/digitalocean"
      version = "~> 2.34"
    }
  }

  # Optional: Configure remote state storage
  # Uncomment and configure for team collaboration
  # backend "s3" {
  #   endpoint                    = "https://nyc3.digitaloceanspaces.com"
  #   key                        = "terraform/smart-garden-planner.tfstate"
  #   bucket                     = "your-terraform-state-bucket"
  #   region                     = "us-east-1"  # Required for S3 compatibility
  #   skip_credentials_validation = true
  #   skip_metadata_api_check     = true
  # }
}