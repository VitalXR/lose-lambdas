import sys
import os
import logging
import pymysql
import json

def is_admin(groups):
  g = groups.split(',')
  isAdmin = g.count("VxrAdmin")
  if (isAdmin == 0):
    return False
  return True

def handler(event, context):
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
  try:
    c = event['context']
    groups = c['groups']
    
    if not is_admin(groups):
      return {
        'statusCode': 403,
        'body': json.dumps('Unauthorized')
      }
  except:
    return {
      'statusCode': 500,
      'body': 'Internal Server Error'
    }

  try:
    with conn.cursor() as cur:
      res = []
      cur.execute('SELECT fname, lname, email, org_name, `usage`, `status`, UNIX_TIMESTAMP(created_at) AS `created_at` FROM signup_forms')
      for row in cur:
        res.append(row)
      return {
        'statusCode': 200,
        'body': json.dumps(res)
      }
  except:
    return {
      'statusCode': 500,
      'body': 'Internal Server Error'
    }
