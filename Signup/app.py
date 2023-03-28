import sys
import os
import logging
import pymysql
import json

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

def handler(event, context):
  fname = event['fname']
  lname = event['lname']
  email = event['email']
  org_name = event['org']
  usage = event['usage']

  try:
    with conn.cursor() as cur:
      sql = 'INSERT INTO signup_forms (fname, lname, email, org_name, `usage`, `status`) VALUES (%s, %s, %s, %s, %s, %s)'
      cur.execute(sql, (fname, lname, email, org_name, usage, 'pending'))
      conn.commit()
    return {
      'statusCode': 200
    }
  except e:
    print(e)
    return {
      'statusCode': 500
    }
