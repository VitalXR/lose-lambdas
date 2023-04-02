import os
import logging

import pymysql

logger = logging.getLogger()
logger.setLevel(logging.INFO)

def lambda_handler(event, context):
    rds_host = os.environ.get('rds_host')
    username = os.environ.get('rds_username')
    password = os.environ.get('rds_password')
    db_name = os.environ.get('rds_db')

    conn = pymysql.connect(host=rds_host, user=username, passwd=password, db=db_name, connect_timeout=5)

    email = event['request']['userAttributes']['email']

    with conn.cursor() as cur:
        sql = 'SELECT id FROM pending_users WHERE email=%s AND cognitoed=0'
        cur.execute(sql, (email))
        conn.commit()
        res = cur.fetchone()
        if res is None:
            raise Exception("email not found")
        return event