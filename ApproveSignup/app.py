import boto3
from botocore.exceptions import ClientError
import json
import pymysql
import logging
import sys
import os

rds_host = os.environ.get('rds_host')
username = os.environ.get('rds_username')
password = os.environ.get('rds_password')
db_name = os.environ.get('rds_db')

logger = logging.getLogger()
logger.setLevel(logging.INFO)

try:
  conn = pymysql.connect(host=rds_host, user=username, passwd=password, db=db_name, connect_timeout=5)
except pymysql.MySQLError as e:
  logger.error('ERROR: unexpected error. Could not connect to MySQL instance')
  logger.error(e)
  sys.exit()

logger.info("SUCCESS: Connection to RDS MySQL instance succeeded")

def is_admin(groups):
  g = groups.split(',')
  isAdmin = g.count("VxrAdmin")
  if (isAdmin == 0):
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
  except:
    return {
      'statusCode': 500,
      'body': 'Internal Server Error'
    }

  org_name = event['org']
  email = event['email']

  with conn.cursor() as cur:
    cur.execute(f'INSERT INTO `organizations` (`name`, max_users, max_concurrent_users, is_deleted) VALUES (\'{org_name}\', 50, 5, 0)')
    org_id = cur.lastrowid
    cur.execute(f'SELECT id FROM signup_forms WHERE org_name=\'{org_name}\'')
    row = cur.fetchone()
    if row is not None:
      signup_form_id = row[0]
      cur.execute(f'DELETE FROM signup_forms WHERE id={signup_form_id}')
    conn.commit()
   
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
    ]
  )

  response = client.admin_add_user_to_group(
    UserPoolId=userpool_id,
    Username=response['User']['Username'],
    GroupName='OrgAdmin'
  )

  print(response)