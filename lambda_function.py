import json
import logging
from typing import Dict, Any, List
from src.services.email_service import EmailService
from src.services.s3_service import S3Service
from src.services.sqs_service import SQSService
from src.utils.exceptions import EmailProcessingError

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

def lambda_handler(event: Dict[str, Any], context: Any) -> Dict[str, Any]:
    """
    AWS Lambda handler for processing email templates from SQS triggers.
    
    Args:
        event: SQS event containing message records
        context: Lambda context object
    
    Returns:
        Response dictionary with processing results
    """
    try:
        logger.info(f"Processing {len(event.get('Records', []))} SQS messages")
        
        sqs_service = SQSService()
        s3_service = S3Service()
        email_service = EmailService()
        
        processed_count = 0
        failed_count = 0
        
        for record in event.get('Records', []):
            try:
                message_data = sqs_service.parse_message(record)
                
                template_content = s3_service.get_template(
                    bucket=message_data['template_bucket'],
                    key=message_data['template_key']
                )
                
                rendered_email = email_service.render_template(
                    template_content,
                    message_data['template_data']
                )
                
                email_service.send_email(
                    to_addresses=message_data['to_addresses'],
                    subject=message_data['subject'],
                    body_html=rendered_email,
                    from_address=message_data.get('from_address')
                )
                
                processed_count += 1
                logger.info(f"Successfully processed email for {message_data['to_addresses']}")
                
            except Exception as e:
                failed_count += 1
                logger.error(f"Failed to process message: {str(e)}")
        
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