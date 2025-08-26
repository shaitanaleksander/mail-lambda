# SQS Queue for email processing
resource "aws_sqs_queue" "email_queue" {
  name = "${var.project_name}-email-queue"

  # Message retention period (14 days)
  message_retention_seconds = 1209600

  # Visibility timeout should be 6x Lambda timeout
  visibility_timeout_seconds = var.lambda_timeout * 6

  # Enable long polling
  receive_wait_time_seconds = 20

  # Redrive policy for dead letter queue
  redrive_policy = jsonencode({
    deadLetterTargetArn = aws_sqs_queue.email_dlq.arn
    maxReceiveCount     = var.max_receive_count
  })

  tags = var.tags
}

# Dead Letter Queue for failed messages
resource "aws_sqs_queue" "email_dlq" {
  name = "${var.project_name}-email-dlq"

  # Longer retention for failed messages (14 days)
  message_retention_seconds = 1209600

  tags = var.tags
}

# SQS Queue policy to allow sending messages
resource "aws_sqs_queue_policy" "email_queue_policy" {
  queue_url = aws_sqs_queue.email_queue.id

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect = "Allow"
        Principal = {
          AWS = "arn:aws:iam::${data.aws_caller_identity.current.account_id}:root"
        }
        Action = [
          "sqs:SendMessage",
          "sqs:ReceiveMessage",
          "sqs:DeleteMessage",
          "sqs:GetQueueAttributes"
        ]
        Resource = aws_sqs_queue.email_queue.arn
        Condition = {
          StringEquals = {
            "aws:SourceAccount" = data.aws_caller_identity.current.account_id
          }
        }
      }
    ]
  })
}