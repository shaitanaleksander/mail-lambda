import boto3
import logging
import os
from typing import Dict, Any, Optional
from botocore.exceptions import ClientError, NoCredentialsError
from src.utils.exceptions import EmailServiceError

logger = logging.getLogger(__name__)

class EmailService:
    """Service for handling email sending via AWS SES."""
    
    def __init__(self):
        """Initialize SES client."""
        try:
            self.ses_client = boto3.client('ses')
            self.default_from_address = os.environ.get('DEFAULT_FROM_ADDRESS', 'noreply@skillzzy.com')
        except NoCredentialsError:
            logger.error("AWS credentials not found")
            raise EmailServiceError("AWS credentials not configured")
    
    def send_email(
        self,
        recipient_email: str,
        subject: str,
        html_content: str,
        from_address: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Send email via AWS SES.
        
        Args:
            recipient_email: Recipient email address
            subject: Email subject
            html_content: HTML email body content
            from_address: Sender email address (optional, uses default if not provided)
            
        Returns:
            SES response dictionary
            
        Raises:
            EmailServiceError: If email sending fails
        """
        try:
            sender = from_address or self.default_from_address
            
            logger.info(f"Sending email to {recipient_email}")
            logger.debug(f"From: {sender}, Subject: {subject}")
            
            response = self.ses_client.send_email(
                Source=sender,
                Destination={'ToAddresses': [recipient_email]},
                Message={
                    'Subject': {'Data': subject, 'Charset': 'UTF-8'},
                    'Body': {
                        'Html': {'Data': html_content, 'Charset': 'UTF-8'}
                    }
                }
            )
            
            message_id = response['MessageId']
            logger.info(f"Successfully sent email to {recipient_email}, MessageId: {message_id}")
            
            return {
                'message_id': message_id,
                'recipient': recipient_email,
                'status': 'sent'
            }
            
        except ClientError as e:
            error_code = e.response['Error']['Code']
            if error_code == 'MessageRejected':
                raise EmailServiceError(f"Email rejected by SES: {e.response['Error']['Message']}")
            elif error_code == 'SendingPausedException':
                raise EmailServiceError("SES sending is paused for this account")
            elif error_code == 'ConfigurationSetDoesNotExistException':
                raise EmailServiceError("SES configuration set does not exist")
            else:
                raise EmailServiceError(f"SES error: {str(e)}")
        except Exception as e:
            raise EmailServiceError(f"Unexpected error sending email: {str(e)}")
    
    def verify_email_address(self, email: str) -> bool:
        """
        Verify if an email address is verified in SES.
        
        Args:
            email: Email address to check
            
        Returns:
            True if verified, False otherwise
        """
        try:
            response = self.ses_client.get_identity_verification_attributes(
                Identities=[email]
            )
            
            verification_attrs = response.get('VerificationAttributes', {})
            email_attrs = verification_attrs.get(email, {})
            
            return email_attrs.get('VerificationStatus') == 'Success'
            
        except ClientError as e:
            logger.error(f"Error checking email verification status: {str(e)}")
            return False