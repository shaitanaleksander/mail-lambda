import os
from typing import Dict, Any

def get_config() -> Dict[str, Any]:
    """
    Get configuration from environment variables.
    
    Returns:
        Configuration dictionary
    """
    return {
        'default_from_address': os.environ.get('DEFAULT_FROM_ADDRESS', 'noreply@example.com'),
        'aws_region': os.environ.get('AWS_REGION', 'us-east-1'),
        'log_level': os.environ.get('LOG_LEVEL', 'INFO'),
        'max_recipients_per_email': int(os.environ.get('MAX_RECIPIENTS_PER_EMAIL', '50')),
        'template_cache_ttl': int(os.environ.get('TEMPLATE_CACHE_TTL', '300')),
    }