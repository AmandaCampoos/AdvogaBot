
# função para receber alertas no email, caso a conta AWS ultrapassar 15$ USD

# SNS
resource "aws_sns_topic" "budget_alerts" {
  name = "budget-alerts-topic"
}

# Assinatura por e-mail (você precisa confirmar o e-mail que vai receber da AWS)
resource "aws_sns_topic_subscription" "budget_email" {
  topic_arn = aws_sns_topic.budget_alerts.arn
  protocol  = "email"
  endpoint  = "amanda.x.pb@compasso.com.br"
}

# Orçamento mensal 
resource "aws_budgets_budget" "monthly_cost_alert" {
  name              = "monthly-cost-budget"
  budget_type       = "COST"
  limit_amount      = "15"
  limit_unit        = "USD"
  time_unit         = "MONTHLY"

  # time_period_start = formatdate("YYYY-MM-DD_hh:mm", timestamp()) # definir data(Opcional)

  # Alerta quando ultrapassar 100% do valor
  notification {
    comparison_operator = "GREATER_THAN"
    threshold           = 100
    threshold_type      = "PERCENTAGE"
    notification_type   = "ACTUAL"

    subscriber {
      subscription_type = "SNS"
      address           = aws_sns_topic.budget_alerts.arn
    }
  }
}
