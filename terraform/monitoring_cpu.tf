# Implementando alertas da EC2 via email
# O desenvolvedor receberar um email para confirmacao de autorizacao 

resource "aws_sns_topic" "ec2_alerts" {
  name = "ec2-alerts-topic"
}

# Assinatura por e-mail
resource "aws_sns_topic_subscription" "email_alert" {
  topic_arn = aws_sns_topic.ec2_alerts.arn
  protocol  = "email"
  endpoint  = "amanda.x.pb@compasso.com.br"
}

# Monitoramento de CPU , prevenção de gargalo e economia.
# Por que isso é importante? Evita lentidão e possivel ou que caia.

resource "aws_cloudwatch_metric_alarm" "ec2_cpu_high" {
  alarm_name          = "EC2HighCPU"
  comparison_operator = "GreaterThanThreshold"
  evaluation_periods  = 1
  metric_name         = "CPUUtilization"
  namespace           = "AWS/EC2"
  period              = 300 # 300 segundos = 5 minutos
  statistic           = "Average"
  threshold           = 70
  alarm_description   = "Alerta quando a CPU da instância EC2 ultrapassar 70% por 5 minutos"
  alarm_actions       = [aws_sns_topic.ec2_alerts.arn] # Envia para o tópico SNS
  ok_actions          = [aws_sns_topic.ec2_alerts.arn] # Notifica quando voltar ao normal
  dimensions = {
    InstanceId = aws_instance.main.id # Referência à sua EC2
  }

  tags = {
    Name = "EC2 CPU Alarm"
  }
}

