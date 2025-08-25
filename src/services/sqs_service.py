import json
import logging
from typing import Dict, Any, List
from email_validator import validate_email, EmailNotValidError
from src.utils.exceptions import SQSServiceError

logger = logging.getLogger(__name__)

class SQSService:
    """Service for handling SQS message parsing and validation."""
    
    def parse_message(self, record: Dict[str, Any]) -> Dict[str, Any]:
        """
        Parse SQS message record and extract email data.
        
        Expected message format:
        {
            "template_bucket": "my-email-templates",
            "template_key": "welcome-email.html",
            "to_addresses": ["user@example.com"],
            "subject": "Welcome!",
            "from_address": "noreply@company.com",
            "template_data": {
                "user_name": "John Doe",
                "company_name": "ACME Corp"
            }
        }
        
        Args:
            record: SQS message record
            
        Returns:
            Parsed message data dictionary
            
        Raises:
            SQSServiceError: If message parsing or validation fails
        """
        try:
            message_body = record.get('body')
            if not message_body:
                raise SQSServiceError("SQS message body is empty")
            
            try:
                message_data = json.loads(message_body)
            except json.JSONDecodeError as e:
                raise SQSServiceError(f"Invalid JSON in SQS message: {str(e)}")
            
            self._validate_message_data(message_data)
            
            logger.info(f"Successfully parsed SQS message for {len(message_data['to_addresses'])} recipients")
            return message_data
            
        except Exception as e:
            if isinstance(e, SQSServiceError):
                raise
            raise SQSServiceError(f"Failed to parse SQS message: {str(e)}")
    
    def _validate_message_data(self, data: Dict[str, Any]) -> None:
        """
        Validate required fields in message data.
        
        Args:
            data: Message data dictionary
            
        Raises:
            SQSServiceError: If validation fails
        """
        required_fields = [
            'template_bucket',
            'template_key', 
            'to_addresses',
            'subject',
            'template_data'
        ]
        
        for field in required_fields:
            if field not in data:
                raise SQSServiceError(f"Missing required field: {field}")
        
        if not isinstance(data['to_addresses'], list):
            raise SQSServiceError("to_addresses must be a list")
        
        if not data['to_addresses']:
            raise SQSServiceError("to_addresses cannot be empty")
        
        for email in data['to_addresses']:
            if not isinstance(email, str):
                raise SQSServiceError(f"Invalid email address format: {email}")
            try:
                validate_email(email)
            except EmailNotValidError:
                raise SQSServiceError(f"Invalid email address: {email}")
        
        if data.get('from_address'):
            try:
                validate_email(data['from_address'])
            except EmailNotValidError:
                raise SQSServiceError(f"Invalid from_address: {data['from_address']}")
        
        if not isinstance(data['template_data'], dict):
            raise SQSServiceError("template_data must be a dictionary")
        
        if not isinstance(data['subject'], str) or not data['subject'].strip():
            raise SQSServiceError("subject must be a non-empty string")