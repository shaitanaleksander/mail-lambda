import boto3
import logging
from typing import Dict, Any, List, Optional
from jinja2 import Template, TemplateError
from botocore.exceptions import ClientError, NoCredentialsError
from src.utils.exceptions import EmailServiceError
from src.utils.config import get_config

logger = logging.getLogger(__name__)

class EmailService:
    """Service for handling email template rendering and SES sending."""
    
    def __init__(self):
        """Initialize SES client."""
        try:
            self.ses_client = boto3.client('ses')
            self.config = get_config()
        except NoCredentialsError:
            logger.error("AWS credentials not found")
            raise EmailServiceError("AWS credentials not configured")
    
    def render_template(self, template_content: str, template_data: Dict[str, Any]) -> str:
        """
        Render email template with provided data using Jinja2.
        
        Args:
            template_content: HTML template content
            template_data: Data to fill into template
            
        Returns:
            Rendered HTML content
            
        Raises:
            EmailServiceError: If template rendering fails
        """
        try:
            logger.info("Rendering email template")
            
            template = Template(template_content)
            rendered_content = template.render(**template_data)
            
            logger.info(f"Successfully rendered template, output size: {len(rendered_content)} chars")
            return rendered_content
            
        except TemplateError as e:
            raise EmailServiceError(f"Template rendering error: {str(e)}")
        except Exception as e:
            raise EmailServiceError(f"Unexpected error during template rendering: {str(e)}")
    
    def send_email(
        self,
        to_addresses: List[str],
        subject: str,
        body_html: str,
        from_address: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Send email via AWS SES.
        
        Args:
            to_addresses: List of recipient email addresses
            subject: Email subject
            body_html: HTML email body
            from_address: Sender email address (optional, uses default if not provided)
            
        Returns:
            SES response dictionary
            
        Raises:
            EmailServiceError: If email sending fails
        """
        try:
            sender = from_address or self.config['default_from_address']
            
            logger.info(f"Sending email to {len(to_addresses)} recipients")
            logger.debug(f"From: {sender}, Subject: {subject}")
            
            response = self.ses_client.send_email(
                Source=sender,
                Destination={'ToAddresses': to_addresses},
                Message={
                    'Subject': {'Data': subject, 'Charset': 'UTF-8'},
                    'Body': {
                        'Html': {'Data': body_html, 'Charset': 'UTF-8'}
                    }
                }
            )
            
            message_id = response['MessageId']
            logger.info(f"Successfully sent email, MessageId: {message_id}")
            
            return {
                'message_id': message_id,
                'recipients': to_addresses,
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
    
    def send_bulk_email(
        self,
        destinations: List[Dict[str, Any]],
        subject: str,
        body_html: str,
        from_address: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """
        Send bulk personalized emails via AWS SES.
        
        Args:
            destinations: List of destination dictionaries with email and template data
            subject: Email subject template
            body_html: HTML email body template
            from_address: Sender email address
            
        Returns:
            List of send results
        """
        results = []
        
        for dest in destinations:
            try:
                personalized_subject = Template(subject).render(**dest.get('template_data', {}))
                personalized_body = Template(body_html).render(**dest.get('template_data', {}))
                
                result = self.send_email(
                    to_addresses=[dest['email']],
                    subject=personalized_subject,
                    body_html=personalized_body,
                    from_address=from_address
                )
                results.append(result)
                
            except Exception as e:
                logger.error(f"Failed to send email to {dest.get('email', 'unknown')}: {str(e)}")
                results.append({
                    'email': dest.get('email'),
                    'status': 'failed',
                    'error': str(e)
                })
        
        return results