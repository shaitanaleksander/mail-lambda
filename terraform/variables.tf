variable "aws_region" {
  description = "AWS region for deployment"
  type        = string
  default     = "eu-north-1"
}

variable "project_name" {
  description = "Name of the project (used for naming resources)"
  type        = string
  default     = "skillzzy-mail"
}

variable "default_from_address" {
  description = "Default email address to send emails from"
  type        = string
  default     = "noreply@skillzzy.com"
}

variable "lambda_runtime" {
  description = "Lambda runtime version"
  type        = string
  default     = "python3.9"
}

variable "lambda_timeout" {
  description = "Lambda function timeout in seconds"
  type        = number
  default     = 300
}

variable "lambda_memory_size" {
  description = "Lambda function memory size in MB"
  type        = number
  default     = 256
}

variable "log_level" {
  description = "Log level for Lambda function"
  type        = string
  default     = "INFO"
  validation {
    condition     = contains(["DEBUG", "INFO", "WARNING", "ERROR"], var.log_level)
    error_message = "Log level must be one of: DEBUG, INFO, WARNING, ERROR."
  }
}

variable "log_retention_days" {
  description = "CloudWatch log retention period in days"
  type        = number
  default     = 14
}

variable "max_receive_count" {
  description = "Maximum number of times a message can be received before being sent to DLQ"
  type        = number
  default     = 3
}

variable "sqs_batch_size" {
  description = "Number of messages to process in each Lambda invocation"
  type        = number
  default     = 10
  validation {
    condition     = var.sqs_batch_size >= 1 && var.sqs_batch_size <= 10000
    error_message = "SQS batch size must be between 1 and 10000."
  }
}

variable "sqs_batching_window" {
  description = "Maximum time to wait for batching messages in seconds"
  type        = number
  default     = 5
  validation {
    condition     = var.sqs_batching_window >= 0 && var.sqs_batching_window <= 300
    error_message = "SQS batching window must be between 0 and 300 seconds."
  }
}

variable "sqs_parallelization_factor" {
  description = "Number of concurrent Lambda executions per shard"
  type        = number
  default     = 2
  validation {
    condition     = var.sqs_parallelization_factor >= 1 && var.sqs_parallelization_factor <= 10
    error_message = "SQS parallelization factor must be between 1 and 10."
  }
}

variable "tags" {
  description = "Tags to apply to all resources"
  type        = map(string)
  default = {
    Project     = "skillzzy-mail"
    Environment = "production"
    ManagedBy   = "terraform"
  }
}