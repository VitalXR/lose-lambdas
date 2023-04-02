import os
import sys
import logging

import pymysql

logger = logging.getLogger()
logger.setLevel(logging.INFO)

try:
  rds_host = os.environ.get('rds_host')
  username = os.environ.get('rds_username')
  password = os.environ.get('rds_password')
  db_name = os.environ.get('rds_db')

  conn = pymysql.connect(host=rds_host, user=username, passwd=password, db=db_name, connect_timeout=5)
except pymysql.MySQLError as e:
  logger.error('ERROR: unexpected error. Could not connect to MySQL instance')
  logger.error(e)
  sys.exit()

def is_admin(groups):
  g = groups.split(',')
  isVxrAdmin = g.count('VxrAdmin')
  isOrgAdmin = g.count('OrgAdmin')
  if (isVxrAdmin == 0 and isOrgAdmin == 0):
    return False
  return True

def handler(event, context):
  r = 0
  try:
    c = event['context']
    groups = c['groups']
    
    r = 1
    if not is_admin(groups):
      return {
        'statusCode': 403,
        'body': 'Unauthorized'
      }
    
    org_id = c['org_id']
    email = event['email']
    r = 2
    with conn.cursor() as cur:
      sql = 'INSERT INTO pending_users (email, org_id, cognitoed, `role`) VALUES (%s, %s, %s, %s)'
      cur.execute(sql, (email, int(org_id), 0, 'NonAdmin'))
      conn.commit()
    r = 3
    return {
      'statusCode': 200
    }

  except Exception as e:
    logger.error(e)
    return {
      'statusCode': 500,
      'body': f'Internal Server Error - {r}'
    }

# def handler(event, context):
#   try:
#     c = event['context']
#     groups = c['groups']
    
#     if not is_admin(groups):
#       return {
#         'statusCode': 403,
#         'body': 'Unauthorized'
#       }
    
#     org_id = c['org_id']
#     email = event['email']

#     client = boto3.client('cognito-idp')
#     userpool_id = os.environ.get('up_id')

#     response = client.admin_create_user(
#       UserPoolId=userpool_id,
#       Username=email,
#       UserAttributes=[
#         {
#           'Name': 'email',
#           'Value': email
#         },
#         {
#           'Name': 'custom:org_id',
#           'Value': str(org_id)
#         }
#       ])

#     response = client.admin_add_user_to_group(
#       UserPoolId=userpool_id,
#       Username=response['User']['Username'],
#       GroupName='NonAdmin')

#     return {
#       'statusCode': 200
#     }
#   except ClientError as err:
#     return {
#       'statusCode': 500,
#       'body': json.dumps(err.response['Error']['Code'])
#     }
#   except:
#     return {
#       'statusCode': 500,
#       'body': 'Internal Server Error'
#     }
