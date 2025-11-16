"""S3 distributor for uploading files to AWS S3."""
from pathlib import Path
from typing import Dict, Any, Optional
import boto3
from botocore.exceptions import ClientError
from .base import BaseDistributor
from ..utils.config import Config

class S3Distributor(BaseDistributor):
    """Distributor for uploading files to AWS S3."""
    
    def __init__(self):
        self.s3_client = None
        if Config.AWS_ACCESS_KEY_ID and Config.AWS_SECRET_ACCESS_KEY:
            self.s3_client = boto3.client(
                's3',
                aws_access_key_id=Config.AWS_ACCESS_KEY_ID,
                aws_secret_access_key=Config.AWS_SECRET_ACCESS_KEY,
                region_name=Config.AWS_REGION
            )
    
    def distribute(
        self,
        file_path: Path,
        bucket: Optional[str] = None,
        key: Optional[str] = None,
        public: bool = False,
        **kwargs
    ) -> Dict[str, Any]:
        """
        Upload file to S3.
        
        Args:
            file_path: Path to file to upload
            bucket: S3 bucket name (uses config default if not provided)
            key: S3 object key (uses filename if not provided)
            public: Whether to make the object public
        """
        if not self.s3_client:
            raise ValueError("S3 client not configured. Set AWS credentials in .env file.")
        
        bucket = bucket or Config.AWS_S3_BUCKET
        if not bucket:
            raise ValueError("S3 bucket not specified and no default in config.")
        
        key = key or file_path.name
        
        try:
            extra_args = {}
            if public:
                extra_args['ACL'] = 'public-read'
            
            self.s3_client.upload_file(
                str(file_path),
                bucket,
                key,
                ExtraArgs=extra_args
            )
            
            # Generate URL
            url = self.s3_client.generate_presigned_url(
                'get_object',
                Params={'Bucket': bucket, 'Key': key},
                ExpiresIn=3600 * 24 * 7  # 7 days
            )
            
            if public:
                url = f"https://{bucket}.s3.{Config.AWS_REGION}.amazonaws.com/{key}"
            
            return {
                'success': True,
                'url': url,
                'bucket': bucket,
                'key': key,
                'method': 's3'
            }
        
        except ClientError as e:
            return {
                'success': False,
                'error': str(e),
                'method': 's3'
            }
    
    def get_name(self) -> str:
        return "AWS S3"

