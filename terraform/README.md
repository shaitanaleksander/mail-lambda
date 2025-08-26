# Terraform Deployment for Email Lambda Function

This Terraform configuration deploys the email processing Lambda function with SQS trigger and all necessary AWS resources.

## Architecture

```
SQS Queue → Lambda Function → SES
     ↓
Dead Letter Queue
```

## Resources Created

- **Lambda Function**: Processes email templates and sends via SES
- **SQS Queue**: Receives email processing messages
- **Dead Letter Queue**: Handles failed messages
- **IAM Role & Policy**: Lambda execution permissions
- **CloudWatch Log Group**: Lambda function logs
- **Event Source Mapping**: SQS to Lambda trigger

## Prerequisites

1. **AWS CLI configured** with appropriate credentials
2. **Terraform installed** (>= 1.0)
3. **SES verified domain/email addresses** for sending emails

## Quick Start

1. **Navigate to terraform directory:**
   ```bash
   cd terraform
   ```

2. **Create terraform.tfvars:**
   ```bash
   cp terraform.tfvars.example terraform.tfvars
   # Edit terraform.tfvars with your values
   ```

3. **Initialize Terraform:**
   ```bash
   terraform init
   ```

4. **Plan deployment:**
   ```bash
   terraform plan
   ```

5. **Apply configuration:**
   ```bash
   terraform apply
   ```

## Configuration Variables

| Variable | Description | Default | Required |
|----------|-------------|---------|----------|
| `aws_region` | AWS region for deployment | `eu-north-1` | No |
| `project_name` | Project name for resource naming | `skillzzy-mail` | No |
| `default_from_address` | Default sender email | `noreply@skillzzy.com` | No |
| `lambda_timeout` | Lambda timeout in seconds | `300` | No |
| `lambda_memory_size` | Lambda memory in MB | `256` | No |
| `sqs_batch_size` | Messages per Lambda invocation | `10` | No |

## Important Notes

### SES Setup Required
Before deploying, ensure your sender email addresses are verified in SES:

```bash
# Verify an email address
aws ses verify-email-identity --email-address noreply@skillzzy.com

# Check verification status
aws ses get-identity-verification-attributes --identities noreply@skillzzy.com
```

### Production Considerations

1. **SES Sandbox**: New AWS accounts start in SES sandbox mode
   - Can only send to verified email addresses
   - Request production access via AWS Console

2. **Monitoring**: Set up CloudWatch alarms for:
   - Lambda errors
   - SQS dead letter queue messages
   - Lambda duration/timeout

3. **Cost Optimization**:
   - Adjust `lambda_memory_size` based on actual usage
   - Monitor SQS message retention costs
   - Set up CloudWatch log retention

## Testing the Deployment

After deployment, test by sending a message to the SQS queue:

```bash
# Get queue URL from Terraform output
QUEUE_URL=$(terraform output -raw sqs_queue_url)

# Send test message
aws sqs send-message \
  --queue-url $QUEUE_URL \
  --message-body '{
    "template_name": "greeting",
    "language": "en", 
    "recipient_email": "test@example.com",
    "subject": "Test Email",
    "template_data": {
      "user_first_name": "Test User"
    }
  }'
```

## Cleanup

To destroy all resources:

```bash
terraform destroy
```

## Troubleshooting

### Common Issues

1. **SES not verified**: Verify sender email in SES console
2. **Lambda timeout**: Increase `lambda_timeout` if processing takes longer
3. **Permission denied**: Check IAM policies and SES verification

### Monitoring

- **Lambda Logs**: `/aws/lambda/skillzzy-mail-email-processor`
- **SQS Metrics**: Check queue depth and message age
- **DLQ Messages**: Investigate failed message patterns