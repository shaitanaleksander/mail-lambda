import boto3
import logging
from typing import Dict, Any
from botocore.exceptions import ClientError, NoCredentialsError
from src.utils.exceptions import S3ServiceError

logger = logging.getLogger(__name__)

class S3Service:
    """Service for handling S3 operations for email templates."""
    
    def __init__(self):
        """Initialize S3 client."""
        try:
            self.s3_client = boto3.client('s3')
        except NoCredentialsError:
            logger.error("AWS credentials not found")
            raise S3ServiceError("AWS credentials not configured")
    
    def get_template(self, bucket: str, key: str) -> str:
        """
        Retrieve email template from S3 bucket.
        
        Args:
            bucket: S3 bucket name
            key: S3 object key for the template
            
        Returns:
            Template content as string
            
        Raises:
            S3ServiceError: If template retrieval fails
        """
        try:
            logger.info(f"Retrieving template from s3://{bucket}/{key}")
            
            response = self.s3_client.get_object(Bucket=bucket, Key=key)
            template_content = response['Body'].read().decode('utf-8')
            
            logger.info(f"Successfully retrieved template, size: {len(template_content)} chars")
            return template_content
            
        except ClientError as e:
            error_code = e.response['Error']['Code']
            if error_code == 'NoSuchBucket':
                raise S3ServiceError(f"S3 bucket '{bucket}' does not exist")
            elif error_code == 'NoSuchKey':
                raise S3ServiceError(f"Template '{key}' not found in bucket '{bucket}'")
            else:
                raise S3ServiceError(f"Failed to retrieve template: {str(e)}")
        except Exception as e:
            raise S3ServiceError(f"Unexpected error retrieving template: {str(e)}")
    
    def template_exists(self, bucket: str, key: str) -> bool:
        """
        Check if template exists in S3.
        
        Args:
            bucket: S3 bucket name
            key: S3 object key for the template
            
        Returns:
            True if template exists, False otherwise
        """
        try:
            self.s3_client.head_object(Bucket=bucket, Key=key)
            return True
        except ClientError:
            return False