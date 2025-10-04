# Smart Garden Planner - Terraform Infrastructure

This Terraform configuration creates the necessary DigitalOcean Spaces (object storage) infrastructure for the Smart Garden Planner application.

## What This Creates

- **DigitalOcean Spaces Bucket**: For storing application logs, user data, and backups
- **CORS Configuration**: Allows web application to access the storage
- **Lifecycle Rules**: Automatically manages storage costs by cleaning up old files
- **CDN Endpoint** (optional): For faster content delivery
- **Versioning**: Protects against accidental data loss

## Prerequisites

1. **DigitalOcean Account**: Sign up at [digitalocean.com](https://digitalocean.com)
2. **DigitalOcean API Token**: 
   - Go to [API Tokens](https://cloud.digitalocean.com/account/api/tokens)
   - Click "Generate New Token"
   - Give it a name and select "Write" scope
   - Copy the token (you won't see it again!)
3. **Terraform**: Install from [terraform.io](https://terraform.io/downloads)

## Quick Start

1. **Clone and navigate to terraform directory**:
   ```bash
   cd terraform
   ```

2. **Copy the example variables file**:
   ```bash
   cp terraform.tfvars.example terraform.tfvars
   ```

3. **Edit `terraform.tfvars`** with your values:
   ```hcl
   do_token    = "your_digitalocean_api_token_here"
   bucket_name = "your-unique-bucket-name"  # Must be globally unique
   region      = "nyc3"  # Choose closest region
   ```

4. **Initialize Terraform**:
   ```bash
   terraform init
   ```

5. **Plan the deployment**:
   ```bash
   terraform plan
   ```

6. **Apply the configuration**:
   ```bash
   terraform apply
   ```

7. **Note the outputs** - you'll need these for your application configuration.

## Configuration Options

### Regions
Choose the region closest to your users:
- `nyc3` - New York
- `ams3` - Amsterdam  
- `sgp1` - Singapore
- `sfo3` - San Francisco
- `fra1` - Frankfurt

### Environment-Specific Deployments

For different environments (dev, staging, prod):

```bash
# Development
terraform workspace new dev
terraform apply -var="environment=dev" -var="bucket_name=garden-planner-dev"

# Production
terraform workspace new prod
terraform apply -var="environment=prod" -var="bucket_name=garden-planner-prod" -var="force_destroy=false"
```

### CDN Configuration

To enable CDN for faster content delivery:

```hcl
enable_cdn        = true
cdn_custom_domain = "cdn.yourdomain.com"  # Optional
cdn_ttl          = 3600
```

## Security Best Practices

1. **Never commit `terraform.tfvars`** - it contains sensitive tokens
2. **Use environment variables** for sensitive values:
   ```bash
   export TF_VAR_do_token="your_token_here"
   terraform apply
   ```
3. **Enable remote state** for team collaboration (see `versions.tf`)
4. **Set `force_destroy = false`** in production

## Application Integration

After running Terraform, update your `.env` file with the output values:

```bash
# Get the output values
terraform output env_variables

# Add to your .env file
DO_SPACES_ENDPOINT=https://nyc3.digitaloceanspaces.com
DO_SPACES_REGION=nyc3
DO_SPACES_BUCKET=your-bucket-name
```

You'll also need to create Spaces access keys:
1. Go to [DigitalOcean Spaces Keys](https://cloud.digitalocean.com/account/api/spaces)
2. Click "Generate New Key"
3. Add to your `.env`:
   ```
   DO_SPACES_KEY=your_access_key_id
   DO_SPACES_SECRET=your_secret_access_key
   ```

## Cost Management

The configuration includes lifecycle rules to manage costs:
- Files older than 90 days are automatically deleted
- Old versions are cleaned up after 30 days
- You can adjust these in `main.tf`

## Monitoring

Monitor your Spaces usage in the DigitalOcean console:
- [Spaces Dashboard](https://cloud.digitalocean.com/spaces)
- Check storage usage and bandwidth
- Monitor costs in the billing section

## Troubleshooting

### Common Issues

1. **Bucket name already exists**:
   - Bucket names must be globally unique
   - Try adding a suffix: `garden-planner-yourname-dev`

2. **Permission denied**:
   - Check your API token has "Write" permissions
   - Verify the token is correctly set in `terraform.tfvars`

3. **Region not available**:
   - Some regions may not support all features
   - Try `nyc3` or `ams3` as reliable options

### Getting Help

- Check [DigitalOcean Spaces Documentation](https://docs.digitalocean.com/products/spaces/)
- Review [Terraform DigitalOcean Provider Docs](https://registry.terraform.io/providers/digitalocean/digitalocean/latest/docs)

## Cleanup

To destroy all resources (⚠️ **This will delete all data!**):

```bash
terraform destroy
```

## Files Structure

```
terraform/
├── main.tf                 # Main infrastructure configuration
├── variables.tf            # Input variables
├── outputs.tf             # Output values
├── versions.tf            # Provider versions and backend config
├── terraform.tfvars.example  # Example configuration
└── README.md              # This file
```