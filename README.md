# Email Lambda Service

This Lambda function processes email templates and sends them via AWS SES. It's designed to be triggered by SQS messages containing template data.

## Features

- Template-based email generation with inline CSS styling
- Mobile-responsive email templates
- Multi-language support (English and Ukrainian)
- SQS-triggered processing
- AWS SES integration
- Automatic CSS inlining for email client compatibility
- Error handling and logging

## Project Structure

```
mail-lambda/
├── lambda_function.py          # Main Lambda handler
├── requirements.txt            # Python dependencies
├── mail-lambda.zip            # Ready-to-deploy package
├── src/
│   ├── services/
│   │   ├── email_service.py    # SES email sending logic
│   │   └── template_service.py # Template loading, CSS inlining, and rendering
│   └── utils/
│       └── exceptions.py       # Custom exception classes
├── templates/
│   ├── greeting/
│   │   ├── en.html            # English greeting template
│   │   └── ua.html            # Ukrainian greeting template
│   ├── candidate-interview-scheduled/
│   │   ├── en.html
│   │   └── ua.html
│   ├── interviewer-interview-scheduled/
│   │   ├── en.html
│   │   └── ua.html
│   ├── interview-rejected/
│   │   ├── en.html
│   │   └── ua.html
│   └── interview-request-expired/
│       ├── en.html
│       └── ua.html
└── terraform/                 # Infrastructure as Code
    ├── main.tf
    ├── lambda.tf
    ├── iam.tf
    ├── sqs.tf
    ├── variables.tf
    ├── outputs.tf
    └── terraform.tfvars.example
```

## Email Template Features

### Mobile-Responsive Design
- Automatically optimized for mobile email clients
- Proper viewport scaling and font sizing
- Touch-friendly button sizes

### CSS Inlining
- Automatically converts CSS classes to inline styles
- Compatible with Gmail, Outlook, and other email clients
- No external CSS dependencies required

### Multi-Language Support
- English (`en`) and Ukrainian (`ua`) templates
- Easy to add additional languages

## SQS Message Format

The Lambda expects SQS messages with the following JSON structure:

```json
{
  "template_name": "greeting",
  "language": "en",
  "recipient_email": "user@example.com",
  "subject": "Welcome to Skillzzy!",
  "template_data": {
    "user_first_name": "John",
    "interview_datetime": "2024-01-15 14:30",
    "google_calendar_url": "https://calendar.google.com/...",
    "candidate_name": "John Doe",
    "interviewer_name": "Jane Smith",
    "candidate_skills": ["Python", "React", "AWS"],
    "interviewer_skills": ["Python", "System Design"]
  }
}
```

## Template Variables

### Common Variables
- `user_first_name` - Recipient's first name
- `interview_datetime` - Interview date and time
- `google_calendar_url` - Google Calendar event URL

### Interview-Specific Variables
- `candidate_name` - Interview candidate name
- `interviewer_name` - Interviewer name
- `candidate_skills` - List of candidate skills (automatically converted to HTML list)
- `interviewer_skills` - List of interviewer skills (automatically converted to HTML list)
- `interview_type` - Type of interview
- `interview_duration` - Duration of interview

## Deployment

### Quick Deployment
The `mail-lambda.zip` file is ready for immediate upload to AWS Lambda console.

### Using Terraform (Recommended)

1. Copy the example variables file:
   ```bash
   cp terraform/terraform.tfvars.example terraform/terraform.tfvars
   ```

2. Edit `terraform/terraform.tfvars` with your values:
   ```hcl
   project_name = "mail-lambda"
   region       = "us-east-1"
   environment  = "production"
   ```

3. Deploy the infrastructure:
   ```bash
   cd terraform
   terraform init
   terraform plan
   terraform apply
   ```

### Building Deployment Package

If you need to rebuild the deployment package:

```bash
# Install dependencies
pip install -r requirements.txt -t .

# Create deployment package (Windows)
powershell -Command "Compress-Archive -Path lambda_function.py, src, templates, boto3*, botocore*, jmespath*, s3transfer*, urllib3*, six*, python_dateutil*, dateutil -DestinationPath mail-lambda.zip -Force"

# Clean up
powershell -Command "Remove-Item -Recurse -Force boto3*, botocore*, jmespath*, s3transfer*, urllib3*, six*, python_dateutil*, dateutil, bin"
```

## Local Development

1. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

2. Test template rendering:
   ```python
   from src.services.template_service import TemplateService
   
   service = TemplateService()
   html = service.render_template('greeting', 'en', {'user_first_name': 'John'})
   print(html)
   ```

## Configuration

### Environment Variables

- `LOG_LEVEL` - Logging level (default: INFO)
- `AWS_REGION` - AWS region for SES (default: us-east-1)

### SES Setup

1. Verify your domain/email in AWS SES
2. Request production access if needed
3. Ensure Lambda execution role has SES permissions:
   - `ses:SendEmail`
   - `ses:SendRawEmail`
   - `ses:GetIdentityVerificationAttributes`

## Monitoring

The Lambda function logs all operations to CloudWatch. Monitor:

- Processing success/failure rates
- Template rendering errors
- SES sending failures
- SQS message processing times

## Error Handling

The function handles various error scenarios:

- Missing template files
- Invalid template variables
- SES sending failures
- SQS message parsing errors
- Mixed data types (string vs dict) in SQS body

Failed messages are logged but not reprocessed to avoid infinite loops.

## Template Development

### Creating New Templates

1. Create a new folder under `templates/` with your template name
2. Add language-specific HTML files (e.g., `en.html`, `ua.html`)
3. Use CSS classes that will be automatically inlined:
   - `greeting-container` - Main container
   - `greeting-header` - Header section
   - `greeting-content` - Content section
   - `greeting-footer` - Footer section
   - `greeting-button` - Call-to-action buttons

### CSS Styling

The template service automatically converts CSS classes to inline styles optimized for email clients. No external CSS files are needed.

## Contributing

1. Make changes to the codebase
2. Update templates as needed
3. Rebuild deployment package if necessary
4. Test locally
5. Deploy via Terraform or manual upload
6. Monitor CloudWatch logs