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

    client = boto3.client('cognito-idp')
    userpool_id = os.environ.get('up_id')

    response = client.list_users(
      UserPoolId=userpool_id,
      AttributesToGet=[
        'email',
        'custom:org_id'
      ]
    )

    users = response['Users']
    res = []

    for user in users:
      if 'UserCreateDate' in user:
        user['UserCreateDate'] = user['UserCreateDate'].strftime('%m/%d/%Y')
      if 'UserLastModifiedDate' in user:
        user['UserLastModifiedDate'] = user['UserLastModifiedDate'].strftime('%m/%d/%Y')
      if 'Username' in user:
        user.pop('Username')
      if 'Attributes' in user:                  
        for attr in user['Attributes']:
          if attr['Name'] == 'custom:org_id' and attr['Value'] == org_id:
            res.append(user)
            break
    
    return {
      'body': json.dumps(res)
    }
  except ClientError as err:
    return {
      'statusCode': 500,
      'body': json.dumps(err.response['Error']['Code'])
    }
  except Exception as err:
    return {
      'statusCode': 500,
      'body': f'Internal Server Error'
    }
