import json
import logging
from typing import Dict, Any
from src.services.email_service import EmailService
from src.services.template_service import TemplateService

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

def lambda_handler(event: Dict[str, Any], context: Any) -> Dict[str, Any]:
    """
    AWS Lambda handler for processing email templates from SQS triggers.
    
    Expected SQS message body format:
    {
        "template_name": "greeting",
        "language": "en", 
        "recipient_email": "user@example.com",
        "subject": "Welcome to Skillzzy!",
        "template_data": {
            "user_first_name": "John",
            "interview_datetime": "2024-01-15 14:30",
            "google_calendar_url": "https://calendar.google.com/...",
            ...
        }
    }
    
    Args:
        event: SQS event containing message records
        context: Lambda context object
    
    Returns:
        Response dictionary with processing results
    """
    try:
        logger.info(f"Processing {len(event.get('Records', []))} SQS messages")
        
        template_service = TemplateService()
        email_service = EmailService()
        
        processed_count = 0
        failed_count = 0
        
        for record in event.get('Records', []):
            try:
                # Parse the SQS message body
                message_body = record['body']
                if isinstance(message_body, str):
                    message_body = json.loads(message_body)
                
                logger.info(f"Processing message: {record['messageId']}")
                logger.info(f"Message body: {message_body}")
                
                # Validate required fields
                required_fields = ['template_name', 'language', 'recipient_email', 'subject', 'template_data']
                for field in required_fields:
                    if field not in message_body:
                        raise ValueError(f"Missing required field: {field}")
                
                template_name = message_body['template_name']
                language = message_body['language']
                recipient_email = message_body['recipient_email']
                subject = message_body['subject']
                template_data = message_body['template_data']
                
                # Render the email template
                html_content = template_service.render_template(
                    template_name=template_name,
                    language=language,
                    template_data=template_data
                )
                
                # Send the email
                email_service.send_email(
                    recipient_email=recipient_email,
                    subject=subject,
                    html_content=html_content
                )
                
                processed_count += 1
                logger.info(f"Successfully processed message {record['messageId']} for {recipient_email}")
                
            except Exception as e:
                failed_count += 1
                logger.error(f"Failed to process message {record.get('messageId', 'unknown')}: {str(e)}")
        
        logger.info(f"Processing complete. Processed: {processed_count}, Failed: {failed_count}")
        
        return {
            'statusCode': 200,
            'body': json.dumps({
                'processed': processed_count,
                'failed': failed_count,
                'message': f'Processed {processed_count} emails, {failed_count} failed'
            })
        }
        
    except Exception as e:
        logger.error(f"Lambda handler error: {str(e)}")
        return {
            'statusCode': 500,
            'body': json.dumps({
                'error': str(e),
                'message': 'Failed to process email batch'
            })
        }