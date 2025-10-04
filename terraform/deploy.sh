#!/bin/bash

# Smart Garden Planner - Terraform Deployment Script
# Automates the deployment of DigitalOcean Spaces infrastructure

set -e  # Exit on any error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Check if we're in the terraform directory
if [ ! -f "main.tf" ]; then
    print_error "This script must be run from the terraform directory"
    print_status "Run: cd terraform && ./deploy.sh"
    exit 1
fi

print_status "🌱 Smart Garden Planner - Infrastructure Deployment"
echo "=================================================="

# Check if Terraform is installed
if ! command -v terraform &> /dev/null; then
    print_error "Terraform is not installed. Please install it from https://terraform.io/downloads"
    exit 1
fi

print_success "Terraform is installed: $(terraform version -json | jq -r '.terraform_version')"

# Check if terraform.tfvars exists
if [ ! -f "terraform.tfvars" ]; then
    print_warning "terraform.tfvars not found. Creating from example..."
    
    if [ -f "terraform.tfvars.example" ]; then
        cp terraform.tfvars.example terraform.tfvars
        print_warning "Please edit terraform.tfvars with your DigitalOcean API token and preferences"
        print_status "Opening terraform.tfvars for editing..."
        
        # Try to open with common editors
        if command -v code &> /dev/null; then
            code terraform.tfvars
        elif command -v nano &> /dev/null; then
            nano terraform.tfvars
        elif command -v vim &> /dev/null; then
            vim terraform.tfvars
        else
            print_status "Please edit terraform.tfvars manually with your preferred editor"
        fi
        
        echo ""
        read -p "Press Enter after you've configured terraform.tfvars..."
    else
        print_error "terraform.tfvars.example not found"
        exit 1
    fi
fi

# Validate that DO token is set
if grep -q "your_digitalocean_api_token_here" terraform.tfvars; then
    print_error "Please set your DigitalOcean API token in terraform.tfvars"
    exit 1
fi

print_success "Configuration file found"

# Initialize Terraform
print_status "Initializing Terraform..."
if terraform init; then
    print_success "Terraform initialized successfully"
else
    print_error "Failed to initialize Terraform"
    exit 1
fi

# Validate configuration
print_status "Validating Terraform configuration..."
if terraform validate; then
    print_success "Configuration is valid"
else
    print_error "Configuration validation failed"
    exit 1
fi

# Plan deployment
print_status "Planning deployment..."
if terraform plan -out=tfplan; then
    print_success "Plan created successfully"
else
    print_error "Failed to create deployment plan"
    exit 1
fi

# Ask for confirmation
echo ""
print_warning "Review the plan above. This will create resources in your DigitalOcean account."
print_warning "You will be charged for these resources according to DigitalOcean pricing."
echo ""
read -p "Do you want to proceed with the deployment? (y/N): " -n 1 -r
echo

if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    print_status "Deployment cancelled"
    rm -f tfplan
    exit 0
fi

# Apply the plan
print_status "Applying Terraform configuration..."
if terraform apply tfplan; then
    print_success "Infrastructure deployed successfully!"
else
    print_error "Deployment failed"
    exit 1
fi

# Clean up plan file
rm -f tfplan

# Show outputs
echo ""
print_status "Deployment completed! Here are your configuration details:"
echo "=========================================================="
terraform output setup_instructions

# Save outputs to a file for easy reference
print_status "Saving configuration to terraform-outputs.txt..."
terraform output -json > terraform-outputs.json
terraform output setup_instructions > terraform-outputs.txt

print_success "Configuration saved to terraform-outputs.txt and terraform-outputs.json"

# Remind about next steps
echo ""
print_warning "IMPORTANT NEXT STEPS:"
print_warning "1. Create Spaces access keys in DigitalOcean console"
print_warning "2. Update your application's .env file with the new values"
print_warning "3. Test the setup with your application"
echo ""

print_success "🎉 Infrastructure deployment complete!"