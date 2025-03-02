import json
import boto3
import os
import json
import logger

sns_client = boto3.client("sns")
ec2 = boto3.client('ec2')
endpoints = ec2.describe_vpc_endpoints()
sns = boto3.client('sns')
sns_arn = os.environ.get('SNS_TOPIC_ARN')
sqs_name = os.environ.get('sqs_name')
sqs_client = boto3.client('sqs')

def lambda_handler(event, context):
    message = "SQS Message Queue is created"
    logger.info(message)
    if(check_customer_managed_key(sqs_client,sqs_name)) and check_sqs_vpc_endpoint(endpoints) and check_tag_verification(sqs_client, sqs_name):
        logger.info("SQS is compliant")
    else:
        logger.info("SQS is not compliant")
        sns.publish(TopicArn=sns_arn,Message="SQS is not compliant",Subject="SQS is not compliant")    
def check_sqs_vpc_endpoint(endpoints):
  try:
    logger.info("checking vpc endpoints for SQS")
    for endpoint in endpoints['VpcEndpoints']:
      if(endpoint['ServiceName'] == 'com.amazonaws.us-east-1.sqs'):
        return True
  except Exception as e:
    logger.error(f"Error checking SQS VPC endpoint: {e}")
    return False  
def check_customer_managed_key(sqs_client,sqs_name):
  try:
    logger.info("checking for customer managed keys")
    getQAttributes=sqs_client.get_queue_attributes(QueueUrl=sqs_name, AttributeNames=['SqsManagedSseEnabled'])
    if(getQAttributes['Attributes']):
      return True
  except Exception as e:
    logger.error(f"Error checking SQS Customer Manager Key: {e}")
    return False    
def check_tag_verification(sqs_client,sqs_name):
  try:
    logger.info("checking for tags on SQS")
    getQTags = sqs_client.list_queue_tags(QueueUrl=sqs_name)
    json_string = json.dumps(getQTags['Tags'], indent=2)
    tags = ['Name', 'Created-By', 'Cost-Center']
    for tag in tags:
      if(tag in json_string):
        return True
  except Exception as e:
    logger.error(f"Error checking SQS Customer Manager Key: {e}")
    return False
