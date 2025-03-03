# Cloud Engineer Guardrail Challenge: SQS Security Compliance

## Overview

Using AWS CloudFormation (YAML only) created Python Lambda function which checks for newly created SQS queues. It also checks for following data points
- Verify that a VPC endpoint for SQS exists
- Ensure that the SQS queue has encryption enabled
- Confirm that the queue uses a customer-managed key (CMK) rather than an AWS-managed key.
- Check that the queue is tagged with the following keys (values can be arbitrary):
  -   Name
  -   Created By
  -   Cost Center
If any check fails, trigger an alert by publishing a message to an SNS topic or by logging an error.

---
### Resources Created using this Cloudformation
  - **Lambda Function:**
  - **IAM Role:** 
  - **EventBridge Rule:** 
  - **Optional Alerting Mechanism:** 
  - **Control Tower Guardrail:** 

## Deployment Instructions
### **Pre-requisites**
Before deploying the stack, ensure you have:
1. **AWS CLI installed** ([Installation Guide](https://docs.aws.amazon.com/cli/latest/userguide/install-cliv2.html)).
2. **An S3 bucket** to store the Lambda function ZIP file. This can be created using AWS Console or using AWS CLI running below commands
   - **aws s3 mb** (your-s3-bucket)
4. **AWS IAM permissions** to create CloudFormation stacks, S3, Lambda, SQS, and SNS resources.

### **Step 1: Created Service Account Policy for the OrgID for Dead Letter Queue**
```sh
aws cloudformation create-stack --stack-name DLQDeploymentStack \
  --template-body file://dlq-control-tower.yml \
  --parameters ParameterKey=OUID,ParameterValue=<your-aws-organization-id> \
```
### **Step 2: Create S3 bucket <name-of-the-bucket>**
Create S3 bucket by running the following command using AWS CLI:
```sh
aws s3 mb <name-of-s3-bucket-to-be-created>
```
### **Step 3: Create Zip File for the lambda function**
Run the following command to create the ZIP file:
```sh
zip lambda_function.zip lambda_function.py
```
### **Step 4: Upload the zip Python Function script to S3 bucket created**
Upload the ZIP file to your S3 bucket:
```sh
aws s3 cp lambda_function.zip s3://<your-s3-bucket>/lambda_function.zip
```
### **Step 5: Now run the main Cloud Formation Template Stack by running below command with parameters**
Run the following AWS CLI command to deploy the CloudFormation stack
```sh
aws cloudformation create-stack --stack-name LambdaDeploymentStack \
  --template-body file://cloudformation-template-sqs-lambda.yaml \
  --parameters ParameterKey=S3BucketName,ParameterValue=<your-s3-bucket> \
               ParameterKey=S3ObjectKey,ParameterValue=lambda_function.zip \
               ParameterKey=awsSQSManagedPolicy,ParameterValue=arn:aws:iam::aws:policy/service-role/AWSLambdaSQSQueueExecutionRole \
               ParameterKey=awsSQSManagedPolicy,ParameterValue=arn:aws:iam::aws:policy/AmazonSNSFullAccess \
               ParameterKey=Sqsname,ParameterValue=sqs-destination-for-func \
               ParameterKey=LambdaFunctionName,ParameterValue=sqs-event-func \
               ParameterKey=LambdaRuntime,ParameterValue=python3.9 \
               ParameterKey=LambdaMemorySize,ParameterValue=128 \
               ParameterKey=SQSEventBatchSize,ParameterValue=10
```
### **Step 6: Verify Deployment**
Check Stack Status
```sh
aws cloudformation describe-stacks --stack-name LambdaDeploymentStack --query "Stacks[0].StackStatus"
```
### **Step 7: Retrieve the Lambda Function ARN, IAMRole ARN , SNS ARN and SQSQueue ARN**
```sh
aws cloudformation describe-stacks --stack-name LambdaDeploymentStack --query "Stacks[0].Outputs"
Expected Output:
    [
      {
        "OutputKey": "LambdaFunctionARN",
        "OutputValue": "arn:aws:lambda:us-east-1:12345678:function:sqs-event-func"
      },
      {
        "OutputKey": "IAMRoleARN",
        "OutputValue": "arn:aws:iam::12345678:role/sqs-event-func-ExecutionRole"
      },
      {
        "OutputKey": "SNSARN",
        "OutputValue": "arn:aws:iam::12345678:role/SQSQueueCreationAlerts"
      },
      {
        "OutputKey": "SQSQueueARN",
        "OutputValue": "arn:aws:iam::12345678:role/sqs-destination-for-func"
      }
    ]
```
**Suggested File Structure:**
  ```
  ├── README.md
  ├── lambda_function.py
  ├── dlq-control-tower.yml  # This CloudFormation template will be used to creat Service Account Policy for Dead Letter Queue for OrgID passed as a parameter
  └── cloudformation-template-sqs-lambda.yml # This template will create all the resources to be used by the Lambda Function
        -  SNSSubscription
        -  SNSNotificationTopic
        -  EventMapping
        -  LambdaExecutionRole
        -  Lambda Function
        -  LogGroup
        -  SQS
        -  EventInvoke
        -  LambdaInvokePermission

  ```
### **Summary**
- CloudFormation Template → Deploys Lambda from S3 ZIP file.
- Python Script → Lambda function that checks the VPC Endpoints, check Customer Managed Key, SQS is properly Encrypted and Validates Tags associated with SQS.
- Deployment Steps → Zip the file, upload to S3, and deploy via CloudFormation.
