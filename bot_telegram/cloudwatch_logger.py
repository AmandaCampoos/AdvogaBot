import boto3
import os
from datetime import datetime

def log_to_cloudwatch(message, level="INFO", stream_name="telegram-bot"):
    try:
        logs_client = boto3.client(
            "logs",
            region_name="us-east-1",
            aws_access_key_id=os.getenv("AWS_ACCESS_KEY_ID"),
            aws_secret_access_key=os.getenv("AWS_SECRET_ACCESS_KEY"),
            aws_session_token=os.getenv("AWS_SESSION_TOKEN"),
        )

        log_group = "chatbot-juridico"
        timestamp = int(datetime.now().timestamp() * 1000)

        # Cria grupo se não existir
        try:
            logs_client.create_log_group(logGroupName=log_group)
        except logs_client.exceptions.ResourceAlreadyExistsException:
            pass

        # Cria stream se não existir
        try:
            logs_client.create_log_stream(logGroupName=log_group, logStreamName=stream_name)
            sequence_token = None
        except logs_client.exceptions.ResourceAlreadyExistsException:
            streams = logs_client.describe_log_streams(logGroupName=log_group, logStreamNamePrefix=stream_name)
            sequence_token = streams['logStreams'][0].get('uploadSequenceToken')

        log_event = {
            'logGroupName': log_group,
            'logStreamName': stream_name,
            'logEvents': [{
                'timestamp': timestamp,
                'message': f"[{level}] {message}"
            }]
        }

        if sequence_token:
            log_event['sequenceToken'] = sequence_token

        logs_client.put_log_events(**log_event)

    except Exception as e:
        print(f"🚨 Falha ao enviar log para CloudWatch: {str(e)}")
