terraform {
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 4.0.0"
    }
  }

  required_version = "~> 1.0"
}

provider "aws" {
  region = var.region
}

################################################################################
# Input variable definitions
################################################################################

variable "deployment_name" {
  type = string
}

variable "image_tag" {
  type = string
}

variable "image_repository" {
  type = string
}

variable "image_version" {
  type = string
}

variable "region" {
  description = "AWS region for all resources."

  type    = string
  default = "ap-south-1"
}

variable "timeout" {
  description = "Timout for the Lambda Function."
  type        = number
  default     = 300
}

variable "memory_size" {
  description = "Memory allocated to lambda function."
  type        = number
  default     = 256
}

################################################################################
# Resource definitions
################################################################################

data "aws_ecr_repository" "service" {
  name = var.image_repository
}

data "aws_ecr_image" "service_image" {
  repository_name = data.aws_ecr_repository.service.name
  image_tag       = var.image_version
}

resource "aws_lambda_function" "fn" {
  function_name = "${var.deployment_name}-function"
  role          = aws_iam_role.lambda_exec.arn

  timeout      = var.timeout
  memory_size  = var.memory_size
  image_uri    = "${data.aws_ecr_repository.service.repository_url}@${data.aws_ecr_image.service_image.id}"
  package_type = "Image"

  image_config {
    command = [
      "app.mangum_app",
    ]
    entry_point = []
  }
}

resource "aws_cloudwatch_log_group" "lg" {
  name = "/aws/lambda/${aws_lambda_function.fn.function_name}"

  retention_in_days = 30
}

resource "aws_iam_role" "lambda_exec" {
  name = "${var.deployment_name}-iam"

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [{
      Action = "sts:AssumeRole"
      Effect = "Allow"
      Sid    = ""
      Principal = {
        Service = "lambda.amazonaws.com"
      }
      }
    ]
  })
}

resource "aws_iam_role_policy_attachment" "lambda_policy" {
  role       = aws_iam_role.lambda_exec.name
  policy_arn = "arn:aws:iam::aws:policy/service-role/AWSLambdaBasicExecutionRole"
}

resource "aws_apigatewayv2_api" "lambda" {
  name          = "${var.deployment_name}-gw"
  protocol_type = "HTTP"
}

resource "aws_apigatewayv2_stage" "lambda" {
  api_id = aws_apigatewayv2_api.lambda.id

  name        = "$default"
  auto_deploy = true

  access_log_settings {
    destination_arn = aws_cloudwatch_log_group.api_gw.arn

    format = jsonencode({
      requestId               = "$context.requestId"
      sourceIp                = "$context.identity.sourceIp"
      requestTime             = "$context.requestTime"
      protocol                = "$context.protocol"
      httpMethod              = "$context.httpMethod"
      resourcePath            = "$context.resourcePath"
      routeKey                = "$context.routeKey"
      status                  = "$context.status"
      responseLength          = "$context.responseLength"
      integrationErrorMessage = "$context.integrationErrorMessage"
      }
    )
  }
}

resource "aws_apigatewayv2_integration" "lambda" {
  api_id = aws_apigatewayv2_api.lambda.id

  integration_uri    = aws_lambda_function.fn.invoke_arn
  integration_type   = "AWS_PROXY"
  integration_method = "POST"
}

resource "aws_apigatewayv2_route" "root" {
  api_id = aws_apigatewayv2_api.lambda.id

  route_key = "ANY /"
  target    = "integrations/${aws_apigatewayv2_integration.lambda.id}"
}

resource "aws_apigatewayv2_route" "services" {
  api_id = aws_apigatewayv2_api.lambda.id

  route_key = "ANY /{proxy+}"
  target    = "integrations/${aws_apigatewayv2_integration.lambda.id}"
}

resource "aws_cloudwatch_log_group" "api_gw" {
  name              = "/aws/api_gw/${aws_apigatewayv2_api.lambda.name}"
  retention_in_days = 30
}

resource "aws_lambda_permission" "api_gw" {
  statement_id  = "AllowExecutionFromAPIGateway"
  action        = "lambda:InvokeFunction"
  function_name = aws_lambda_function.fn.function_name
  principal     = "apigateway.amazonaws.com"
  source_arn    = "${aws_apigatewayv2_api.lambda.execution_arn}/*/*"
}

################################################################################
# Output value definitions
################################################################################

output "function_name" {
  description = "Name of the Lambda function."
  value       = aws_lambda_function.fn.function_name
}

output "image_tag" {
  description = "The Image tag that is used for creating the function"
  value       = var.image_tag
}
output "endpoint" {
  description = "Base URL for API Gateway stage."
  value       = aws_apigatewayv2_stage.lambda.invoke_url
}
