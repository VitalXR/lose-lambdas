import os
import logging
import boto3

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
    # c = event['context']
    # groups = c['groups']
    
    # if not is_admin(groups):
    #   return {
    #     'statusCode': 403,
    #     # "isBase64Encoded": False,
    #     # "headers": {
    #     #   'Access-Control-Allow-Headers': 'Content-Type,X-Amz-Date,Authorization,X-Api-Key,X-Amz-Security-Token',
    #     #   'Access-Control-Allow-Origin': '*',
    #     #   'Access-Control-Allow-Methods': 'OPTIONS,POST,GET,PATCH,PUT,DELETE'
    #     # },
    #     'body': 'Unauthorized'
    #   }
    
    # org_id = c['org_id']
    token = event['token']
    prevPasswd = event['prevPasswd']
    newPasswd = event['newPasswd']

    client = boto3.client('cognito-idp')

    response = client.change_password(
      PreviousPassword=prevPasswd,
      ProposedPassword=newPasswd,
      AccessToken=token
    )

    return {
      'statusCode': 200,
    }
  except:
    return {
      'statusCode': 500,
      'body': 'Internal Server Error'
    }
