resource "aws_iam_role" "lambda_textract_role" {
  name = "lambda-textract-role"

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [{
      Effect = "Allow"
      Principal = {
        Service = "lambda.amazonaws.com"
      }
      Action = "sts:AssumeRole"
    }]
  })
}

resource "aws_iam_role_policy" "lambda_textract_policy" {
  name = "lambda-textract-policy"
  role = aws_iam_role.lambda_textract_role.id

  policy = jsonencode({
    Version = "2012-10-17",
    Statement = [
      {
        Effect = "Allow",
        Action = [
          "textract:AnalyzeDocument"
        ],
        Resource = "*"
      },
      {
        Effect = "Allow",
        Action = [
          "s3:GetObject",
          "s3:PutObject",
          "s3:ListBucket"
        ],
        Resource = [
          "arn:aws:s3:::${var.bucket_name}",
          "arn:aws:s3:::${var.bucket_name}/*"
        ]
      },
      {
        Effect = "Allow",
        Action = [
          "logs:CreateLogGroup",
          "logs:CreateLogStream",
          "logs:PutLogEvents"
        ],
        Resource = "*"
      }
    ]
  })
}

resource "aws_lambda_function" "textract" {
  function_name = "textract-processor"
  role          = aws_iam_role.lambda_textract_role.arn
  handler       = "main.lambda_handler"
  runtime       = "python3.11"
  timeout       = 300

  filename         = "${path.module}/../textract/textract_lambda/lambda_textract.zip"
  source_code_hash = filebase64sha256("${path.module}/../textract/textract_lambda/lambda_textract.zip")

  environment {
    variables = {
      BUCKET_NAME = var.bucket_name
    }
  }

  tags = {
    Project = var.project_name
  }
}
