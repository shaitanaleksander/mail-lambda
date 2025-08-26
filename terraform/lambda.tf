# Create deployment package
data "archive_file" "lambda_zip" {
  type        = "zip"
  output_path = "${path.module}/lambda-deployment.zip"
  
  source_dir = "${path.module}/.."
  excludes = [
    "terraform/",
    ".git/",
    ".gitignore",
    "deployment_config.yaml",
    "README.md",
    "lambda-deployment.zip"
  ]
}

# Lambda function
resource "aws_lambda_function" "email_lambda" {
  filename         = data.archive_file.lambda_zip.output_path
  function_name    = "${var.project_name}-email-processor"
  role            = aws_iam_role.lambda_role.arn
  handler         = "lambda_function.lambda_handler"
  runtime         = var.lambda_runtime
  timeout         = var.lambda_timeout
  memory_size     = var.lambda_memory_size

  source_code_hash = data.archive_file.lambda_zip.output_base64sha256

  environment {
    variables = {
      DEFAULT_FROM_ADDRESS = var.default_from_address
      LOG_LEVEL           = var.log_level
    }
  }

  depends_on = [
    aws_iam_role_policy_attachment.lambda_policy_attachment,
    aws_cloudwatch_log_group.lambda_logs
  ]

  tags = var.tags
}

# CloudWatch Log Group for Lambda
resource "aws_cloudwatch_log_group" "lambda_logs" {
  name              = "/aws/lambda/${var.project_name}-email-processor"
  retention_in_days = var.log_retention_days
  
  tags = var.tags
}

# Lambda event source mapping for SQS
resource "aws_lambda_event_source_mapping" "sqs_trigger" {
  event_source_arn = aws_sqs_queue.email_queue.arn
  function_name    = aws_lambda_function.email_lambda.arn
  
  # Batch size for processing messages
  batch_size = var.sqs_batch_size
  
  # Maximum batching window in seconds
  maximum_batching_window_in_seconds = var.sqs_batching_window
  
  # Enable parallel processing
  parallelization_factor = var.sqs_parallelization_factor
  
  # Error handling
  function_response_types = ["ReportBatchItemFailures"]
}