# should recieve email
# do admin signup with email
# if rejected, return error
# if not, add user to group and add org_id attribute

# need up_id

import os
import logging
import json

import boto3
from botocore.exceptions import ClientError
import pymysql

logger = logging.getLogger()
logger.setLevel(logging.INFO)

def handler(event, context):
    r = 0
    try:
        email = event['email']
        r = 1
        rds_host = os.environ.get('rds_host')
        username = os.environ.get('rds_username')
        password = os.environ.get('rds_password')
        db_name = os.environ.get('rds_db')

        r = 2
        conn = pymysql.connect(host=rds_host, user=username, passwd=password, db=db_name, connect_timeout=5)

        with conn.cursor() as cur:
            sql = 'SELECT * FROM pending_users WHERE email=%s AND cognitoed=0'
            cur.execute(sql, (email))
            row = cur.fetchone()

            if row is None:
                return {
                    'statusCode': 404,
                    'body': 'Not Found'
                }

            pending_user_id = row[0]
            org_id = row[2]
            role = row[4]
        r = 3
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
          GroupName=role
        )
        r = 4
        with conn.cursor() as cur:
            sql = 'DELETE FROM pending_users WHERE id=%s'
            cur.execute(sql, (pending_user_id))
            conn.commit()
        r = 5
        return {
            'statusCode': 200
        }
    except ClientError as err:
        return {
          'statusCode': 500,
          'body': json.dumps(err.response['Error']['Code'])
        }
    except Exception as e:
        logger.error(e)
        return {
            'statusCode': 500,
            'body': f'Internal Server Error {r}'
        }