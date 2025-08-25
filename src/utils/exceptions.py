"""Custom exceptions for the email Lambda function."""

class EmailProcessingError(Exception):
    """Base exception for email processing errors."""
    pass

class S3ServiceError(EmailProcessingError):
    """Exception raised for S3 service errors."""
    pass

class SQSServiceError(EmailProcessingError):
    """Exception raised for SQS service errors."""
    pass

class EmailServiceError(EmailProcessingError):
    """Exception raised for email service errors."""
    pass