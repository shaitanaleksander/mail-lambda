# Email Lambda Function

AWS Lambda function that processes email templates from S3, fills them with data from SQS messages, and sends emails via SES.

## Architecture

```
SQS Message → Lambda Function → S3 (Template) → SES (Send Email)
```

## Features

- **SQS Integration**: Triggered by SQS messages containing email data
- **S3 Template Storage**: Retrieves HTML email templates from S3 buckets
- **Jinja2 Templating**: Renders templates with dynamic data
- **SES Email Delivery**: Sends emails via AWS Simple Email Service
- **Error Handling**: Comprehensive error handling and logging
- **Validation**: Email address and message data validation

## Message Format

SQS messages should contain JSON with the following structure:

```json
{
  "template_bucket": "my-email-templates",
  "template_key": "welcome-email.html",
  "to_addresses": ["user@example.com"],
  "subject": "Welcome to our service!",
  "from_address": "noreply@company.com",
  "template_data": {
    "user_name": "John Doe",
    "company_name": "ACME Corp",
    "activation_url": "https://example.com/activate/123"
  }
}
```

## Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `DEFAULT_FROM_ADDRESS` | Default sender email address | `noreply@example.com` |
| `AWS_REGION` | AWS region for services | `us-east-1` |
| `LOG_LEVEL` | Logging level | `INFO` |
| `MAX_RECIPIENTS_PER_EMAIL` | Maximum recipients per email | `50` |

## Template Example

```html
<!DOCTYPE html>
<html>
<head>
    <title>{{ subject }}</title>
</head>
<body>
    <h1>Welcome {{ user_name }}!</h1>
    <p>Thank you for joining {{ company_name }}.</p>
    <a href="{{ activation_url }}">Activate your account</a>
</body>
</html>
```

## Deployment

1. Package dependencies:
   ```bash
   pip install -r requirements.txt -t .
   ```

2. Create deployment package:
   ```bash
   zip -r lambda-deployment.zip .
   ```

3. Deploy to AWS Lambda with appropriate IAM permissions for S3, SQS, and SES.

## IAM Permissions

The Lambda function requires the following permissions:

```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Action": [
        "s3:GetObject"
      ],
      "Resource": "arn:aws:s3:::your-template-bucket/*"
    },
    {
      "Effect": "Allow", 
      "Action": [
        "ses:SendEmail",
        "ses:SendRawEmail"
      ],
      "Resource": "*"
    },
    {
      "Effect": "Allow",
      "Action": [
        "sqs:ReceiveMessage",
        "sqs:DeleteMessage",
        "sqs:GetQueueAttributes"
      ],
      "Resource": "arn:aws:sqs:*:*:your-queue-name"
    }
  ]
}
```