# iam.tf

# IAM Role para EC2
resource "aws_iam_role" "ec2_role" {
  name = "sprint7-ec2-role"

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect = "Allow"
        Principal = {
          Service = "ec2.amazonaws.com"
        }
        Action = "sts:AssumeRole"
      }
    ]
  })
}

# Inline policy para acesso ao S3, Bedrock e CloudWatch
resource "aws_iam_role_policy" "inline_policy" {
  name = "sprint7-ec2-policy"
  role = aws_iam_role.ec2_role.id

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect   = "Allow"
        Action   = ["s3:GetObject", "s3:PutObject"]
        Resource = "arn:aws:s3:::${var.bucket_name}/*"
      },
      {
        Effect   = "Allow"
        Action   = ["bedrock:*"]
        Resource = "*"
      },
      {
        Effect   = "Allow"
        Action   = [
          "logs:CreateLogGroup",
          "logs:CreateLogStream",
          "logs:PutLogEvents"
        ]
        Resource = "*"
      }
    ]
  })
}

# Instance Profile para associar à EC2
resource "aws_iam_instance_profile" "ec2_profile" {
  name = "sprint7-ec2-instance-profile"
  role = aws_iam_role.ec2_role.name
}