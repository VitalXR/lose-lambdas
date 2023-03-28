import os
import logging
import sys
import datetime
import pymysql
import boto3

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

try:
  client = boto3.client('cognito-idp')
except Exception as e:
  logger.error('ERROR: unexpected error. Could not connect to Cognito instance')
  logger.error(e)
  sys.exit()

def handler(event, context):
  try:
    try:
      oid = event["oid"]
      email = event["email"]
    except KeyError as e:
      logger.error(e)
      return {
        'statusCode': 500,
        'body': 'missing organization ID and or user email'
      }
    
    try:
      response = client.admin_get_user(
        UserPoolId=os.environ.get('up_id'),
        Username=email
      )

      notinorg = True

      for attr in response['UserAttributes']:
        if (attr['Name'] == 'custom:org_id' and int(attr['Value']) == oid):
          notinorg = False
          break
      
      if notinorg:
        raise Exception("Mismatched User ID and Org ID")
    except Exception as e:
      logger.error(e)
      return {
        'statusCode': 403,
        'body': 'Forbidden'
      }
    
    with conn.cursor() as cur:
      curdatetime = datetime.datetime.now()
      exptime = curdatetime + datetime.timedelta(minutes=15)
      oid = int(oid)
      sql = 'INSERT INTO vr_sessions (user_email, org_id, exp_time) VALUES (%s, %s, %s)'
      cur.execute(sql, (email, oid, exptime))

      lastid = cur.lastrowid

      sql = 'SELECT COUNT(id) AS c FROM vr_sessions WHERE org_id=%s AND exp_time>%s'
      cur.execute(sql, (oid, curdatetime))
      count = cur.fetchone()[0]

      sql = 'SELECT max_concurrent_users FROM `organizations` WHERE id=%s'
      cur.execute(sql, (oid))
      maxcount = cur.fetchone()[0]

      if count > maxcount:
        sql = 'DELETE FROM vr_sessions WHERE id=%s'
        cur.execute(sql, (lastid))
        conn.commit()
        return {
          'statusCode': 400,
          'body': 'Max concurrent users reached'
        }
      
      conn.commit()

    return {
      'statusCode': 200
    }

  except Exception as e:
    logger.error(e)
    return {
      'statusCode': 500,
      'body': 'Internal Server Error'
    }