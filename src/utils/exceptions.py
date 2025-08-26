"""Custom exceptions for the email Lambda function."""

class EmailProcessingError(Exception):
    """Base exception for email processing errors."""
    pass

class TemplateServiceError(EmailProcessingError):
    """Exception raised for template service errors."""
    pass

class EmailServiceError(EmailProcessingError):
    """Exception raised for email service errors."""
    pass