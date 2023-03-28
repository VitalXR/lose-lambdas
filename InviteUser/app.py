import os
import logging
import boto3
from botocore.exceptions import ClientError
import json

logger = logging.getLogger()
logger.setLevel(logging.INFO)

def is_admin(groups):
  g = groups.split(',')
  isVxrAdmin = g.count('VxrAdmin')
  isOrgAdmin = g.count('OrgAdmin')
  if (isVxrAdmin == 0 and isOrgAdmin == 0):
    return False
  return True

def handler(event, context):
  try:
    c = event['context']
    groups = c['groups']
    
    if not is_admin(groups):
      return {
        'statusCode': 403,
        'body': 'Unauthorized'
      }
    
    org_id = c['org_id']
    email = event['email']

    client = boto3.client('cognito-idp')
    userpool_id = os.environ.get('up_id')

    response = client.admin_create_user(
      UserPoolId=userpool_id,
      Username=email,
      UserAttributes=[
        {
          'Name': 'email',
          'Value': email
        },
        {
          'Name': 'custom:org_id',
          'Value': str(org_id)
        }
      ])

    response = client.admin_add_user_to_group(
      UserPoolId=userpool_id,
      Username=response['User']['Username'],
      GroupName='NonAdmin')

    return {
      'statusCode': 200
    }
  except ClientError as err:
    return {
      'statusCode': 500,
      'body': json.dumps(err.response['Error']['Code'])
    }
  except:
    return {
      'statusCode': 500,
      'body': 'Internal Server Error'
    }
