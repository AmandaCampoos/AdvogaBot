# =============================
# ALERTA DE CPU DA EC2
# =============================

# SNS - Tópico para envio de alertas de CPU
resource "aws_sns_topic" "ec2_alerts" {
  name = "ec2-alerts-topic"
}

# Assinatura por e-mail (você precisa confirmar após o apply)
resource "aws_sns_topic_subscription" "email_alert" {
  topic_arn = aws_sns_topic.ec2_alerts.arn
  protocol  = "email"
  endpoint  = "amanda.x.pb@compasso.com.br"
}

# Alarme do CloudWatch para monitorar uso de CPU na EC2
resource "aws_cloudwatch_metric_alarm" "ec2_cpu_high" {
  alarm_name          = "EC2HighCPU"
  comparison_operator = "GreaterThanThreshold"
  evaluation_periods  = 1
  metric_name         = "CPUUtilization"
  namespace           = "AWS/EC2"
  period              = 300 # 5 minutos
  statistic           = "Average"
  threshold           = 70
  alarm_description   = "Alerta quando a CPU da instância EC2 ultrapassar 70% por 5 minutos"
  alarm_actions       = [aws_sns_topic.ec2_alerts.arn]
  ok_actions          = [aws_sns_topic.ec2_alerts.arn]

  dimensions = {
    InstanceId = aws_instance.sprint7_instance.id # <- Atualize com o nome correto da sua EC2
  }

  tags = {
    Name = "EC2 CPU Alarm"
  }
}
