"""
Digital Ocean Spaces (S3-compatible) storage service.
"""
import os
import json
import boto3
from datetime import datetime
from typing import Optional, Dict, Any
from botocore.exceptions import ClientError, NoCredentialsError
import logging

logger = logging.getLogger(__name__)


class DigitalOceanSpacesClient:
    """Client for Digital Ocean Spaces object storage."""
    
    def __init__(self):
        """Initialize the Spaces client."""
        self.spaces_key = os.getenv("DO_SPACES_KEY")
        self.spaces_secret = os.getenv("DO_SPACES_SECRET")
        self.spaces_endpoint = os.getenv("DO_SPACES_ENDPOINT")
        self.spaces_region = os.getenv("DO_SPACES_REGION", "nyc3")
        self.bucket_name = os.getenv("DO_SPACES_BUCKET", "garden-planner-logs")
        
        self.client = None
        self.enabled = self._is_configured()
        
        if self.enabled:
            try:
                self.client = boto3.client(
                    's3',
                    endpoint_url=self.spaces_endpoint,
                    aws_access_key_id=self.spaces_key,
                    aws_secret_access_key=self.spaces_secret,
                    region_name=self.spaces_region
                )
                logger.info("Digital Ocean Spaces client initialized successfully")
            except Exception as e:
                logger.warning(f"Failed to initialize Spaces client: {e}")
                self.enabled = False
        else:
            logger.info("Digital Ocean Spaces not configured - backup disabled")
    
    def _is_configured(self) -> bool:
        """Check if all required Spaces credentials are configured."""
        required_vars = [
            self.spaces_key,
            self.spaces_secret,
            self.spaces_endpoint,
        ]
        return all(var is not None and var.strip() != "" for var in required_vars)
    
    async def backup_request_log(self, log_data: Dict[Any, Any]) -> Optional[str]:
        """
        Backup request log data to Digital Ocean Spaces.
        
        Args:
            log_data: Dictionary containing the log data
            
        Returns:
            S3 key if successful, None if failed or disabled
        """
        if not self.enabled or not self.client:
            logger.debug("Spaces backup skipped - not configured")
            return None
        
        try:
            # Generate unique key for the log entry
            timestamp = datetime.utcnow()
            log_id = log_data.get('id', 'unknown')
            key = f"request-logs/{timestamp.year}/{timestamp.month:02d}/{timestamp.day:02d}/{log_id}_{timestamp.strftime('%H%M%S')}.json"
            
            # Convert to JSON string
            json_data = json.dumps(log_data, indent=2, default=str)
            
            # Upload to Spaces
            self.client.put_object(
                Bucket=self.bucket_name,
                Key=key,
                Body=json_data.encode('utf-8'),
                ContentType='application/json',
                Metadata={
                    'location': log_data.get('location', ''),
                    'garden_type': log_data.get('garden_type', ''),
                    'success': str(log_data.get('success', False)),
                    'timestamp': timestamp.isoformat()
                }
            )
            
            logger.info(f"Successfully backed up log {log_id} to Spaces: {key}")
            return key
            
        except ClientError as e:
            logger.error(f"Failed to backup to Spaces: {e}")
            return None
        except Exception as e:
            logger.error(f"Unexpected error during Spaces backup: {e}")
            return None
    
    async def list_backups(self, prefix: str = "request-logs/") -> list:
        """
        List backup files in Spaces.
        
        Args:
            prefix: S3 key prefix to filter results
            
        Returns:
            List of backup file keys
        """
        if not self.enabled or not self.client:
            return []
        
        try:
            response = self.client.list_objects_v2(
                Bucket=self.bucket_name,
                Prefix=prefix
            )
            
            return [obj['Key'] for obj in response.get('Contents', [])]
            
        except ClientError as e:
            logger.error(f"Failed to list Spaces backups: {e}")
            return []
    
    async def get_backup(self, key: str) -> Optional[Dict[Any, Any]]:
        """
        Retrieve a backup file from Spaces.
        
        Args:
            key: S3 key of the backup file
            
        Returns:
            Parsed JSON data or None if failed
        """
        if not self.enabled or not self.client:
            return None
        
        try:
            response = self.client.get_object(
                Bucket=self.bucket_name,
                Key=key
            )
            
            json_data = response['Body'].read().decode('utf-8')
            return json.loads(json_data)
            
        except ClientError as e:
            logger.error(f"Failed to retrieve backup from Spaces: {e}")
            return None
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse backup JSON: {e}")
            return None


# Global instance
spaces_client = DigitalOceanSpacesClient()