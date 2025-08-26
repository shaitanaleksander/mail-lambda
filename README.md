# Email Lambda Function

AWS Lambda function that processes email templates from local files, fills them with data from SQS messages, and sends emails via SES.

## Architecture

```
SQS Message → Lambda Function → Local Templates → SES (Send Email)
```

## Features

- **SQS Integration**: Triggered by SQS messages containing email data
- **Local Template Storage**: Uses HTML email templates packaged with the Lambda function
- **String Formatting**: Simple Python string formatting for template rendering
- **SES Email Delivery**: Sends emails via AWS Simple Email Service
- **Multi-language Support**: Templates available in multiple languages (en, ua)
- **Error Handling**: Comprehensive error handling and logging

## SQS Message Format

SQS messages should contain JSON in the body with the following structure:

```json
{
  "template_name": "greeting",
  "language": "en",
  "recipient_email": "user@example.com", 
  "subject": "Welcome to Skillzzy!",
  "template_data": {
    "user_first_name": "John",
    "interview_datetime": "2024-01-15 14:30",
    "google_calendar_url": "https://calendar.google.com/..."
  }
}
```

## Available Templates

- **greeting**: Welcome email for new users
- **candidate-interview-scheduled**: Interview confirmation for candidates
- **interviewer-interview-scheduled**: Interview confirmation for interviewers
- **interview-rejected**: Interview cancellation notification
- **interview-request-expired**: Interview request expiration notice

Each template is available in:
- `en` - English
- `ua` - Ukrainian

## Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `DEFAULT_FROM_ADDRESS` | Default sender email address | `noreply@skillzzy.com` |
| `LOG_LEVEL` | Logging level | `INFO` |

## Template Variables by Template Type

### 1. **greeting** - Welcome email
```json
{
  "template_data": {
    "user_first_name": "John"
  }
}
```

### 2. **candidate-interview-scheduled** - Interview confirmation for candidates
```json
{
  "template_data": {
    "recipient_first_name": "Jane",
    "interview_datetime": "2024-01-15 14:30",
    "interviewer_first_name": "Mike",
    "interviewer_last_name": "Johnson", 
    "interviewer_specialization": "Frontend Development",
    "interviewer_soft_skill_mark": "9",
    "interviewer_hard_skill_mark": "8",
    "google_calendar_url": "https://calendar.google.com/..."
  }
}
```

### 3. **interviewer-interview-scheduled** - Interview confirmation for interviewers
```json
{
  "template_data": {
    "recipient_first_name": "Mike",
    "interview_datetime": "2024-01-15 14:30", 
    "candidate_first_name": "Jane",
    "candidate_last_name": "Smith",
    "candidate_specialization": "Frontend Development",
    "candidate_skills": "<li>JavaScript</li><li>React</li><li>Node.js</li>",
    "google_calendar_url": "https://calendar.google.com/..."
  }
}
```

### 4. **interview-rejected** - Interview cancellation
```json
{
  "template_data": {
    "recipient_first_name": "Jane",
    "rejection_user_first_name": "Mike",
    "scheduled_time": "2024-01-15 14:30"
  }
}
```

### 5. **interview-request-expired** - Request expiration notice
```json
{
  "template_data": {
    "user_first_name": "John"
  }
}
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

3. Deploy to AWS Lambda with appropriate IAM permissions for SQS and SES.

## IAM Permissions

The Lambda function requires the following permissions:

```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow", 
      "Action": [
        "ses:SendEmail",
        "ses:SendRawEmail",
        "ses:GetIdentityVerificationAttributes"
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
    },
    {
      "Effect": "Allow",
      "Action": [
        "logs:CreateLogGroup",
        "logs:CreateLogStream", 
        "logs:PutLogEvents"
      ],
      "Resource": "arn:aws:logs:*:*:*"
    }
  ]
}
```

## Complete SQS Message Examples

### Example 1: Greeting Email
```json
{
  "template_name": "greeting",
  "language": "en",
  "recipient_email": "john.doe@example.com",
  "subject": "Welcome to Skillzzy!",
  "template_data": {
    "user_first_name": "John"
  }
}
```

### Example 2: Interview Scheduled (Candidate)
```json
{
  "template_name": "candidate-interview-scheduled",
  "language": "en", 
  "recipient_email": "jane.smith@example.com",
  "subject": "Your Interview is Scheduled",
  "template_data": {
    "recipient_first_name": "Jane",
    "interview_datetime": "2024-01-15 14:30",
    "interviewer_first_name": "Mike",
    "interviewer_last_name": "Johnson",
    "interviewer_specialization": "Frontend Development",
    "interviewer_soft_skill_mark": "9",
    "interviewer_hard_skill_mark": "8", 
    "google_calendar_url": "https://calendar.google.com/calendar/u/0/r/eventedit?text=Interview+with+Mike+Johnson"
  }
}