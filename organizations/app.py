import json
import pymysql
import os
import logging
import sys
import datetime
import pymysql
import boto3

rds_host = os.environ.get('rds_host')
rds_username = os.environ.get('rds_username')
rds_password = os.environ.get('rds_password')
db_name = os.environ.get('rds_db')



logger = logging.getLogger()
logger.setLevel(logging.INFO)



#connection
try:
  connection = pymysql.connect(host=rds_host, user=username, passwd=password, db=db_name, connect_timeout=5)
except pymysql.MySQLError as e:
  logger.error('ERROR: unexpected error. Could not connect to MySQL instance')
  logger.error(e)
  sys.exit()

def lambda_handler(event, context):
    
    body = {}
    print(event)
    result = []
    status_Code = 200
    # try:
    cursor = connection.cursor()
    if event["queryStringParameters"] is not None:
        if event["httpMethod"] == "GET":
            try:
                if "id" in event['queryStringParameters'].keys():
                    sql = "SELECT * FROM `organizations` WHERE `id`=%s"
                    cursor.execute(sql, (event["queryStringParameters"]["id"]))
                    
                if "name" in event['queryStringParameters'].keys():
                    sql = "SELECT * FROM `organizations` WHERE `name`=%s"
                    cursor.execute(sql, (event["queryStringParameters"]["name"]))
                
                # Executing the SQL command
                rows = cursor.fetchall()
                for row in rows:
                    result.append(row)
            
            except Exception as e:
                # Rolling back in case of error
                logger.error(e)
                connection.rollback()
                status_Code = 400
                result = {'response':"Bad Request",
                'description':"The request could not be understood by the server due to incorrect syntax. The client SHOULD NOT repeat the request without modifications."
                } 
            
        
        elif event["httpMethod"] == "PUT":
            try:
                data = json.loads(event['body'])
            except: 
                data = (event['body'])
            val = (data["name"], data["concurrent_users"], data["total_users"], data["isDeleted"], event["queryStringParameters"]["id"])
            sql = "UPDATE organizations SET name = %s, concurrent_users = %s, total_users = %s, isDeleted = %s WHERE `id`=%s"
            
            try:
            # Executing the SQL command
                cursor.execute(sql, val)  
        
            # Commit your changes in the database
                connection.commit();
                result = data
        
            except Exception as e:
            # Rolling back in case of error
                logger.error(e)
                connection.rollback()
                status_Code = 400
                result = {'response':"Bad Request",
                'description':"The request could not be understood by the server due to incorrect syntax. The client SHOULD NOT repeat the request without modifications."
                }
               
        
        elif event["httpMethod"] == "DELETE":
            sql = "UPDATE organizations SET isDeleted = 1 where id =%s"
    
            try:
            # Executing the SQL command
                cursor.execute(sql,(event["queryStringParameters"]["id"]))
        
            # Commit your changes in the database
                connection.commit();
              
        
            except Exception as e:
            # Rolling back in case of error
                logger.error(e)
                connection.rollback()
                status_Code = 400
                result = {'response':"Bad Request",
                'description':"The request could not be understood by the server due to incorrect syntax. The client SHOULD NOT repeat the request without modifications."
                }
                
        elif event["httpMethod"] == "PATCH":
            try:
                data = json.loads(event['body'])
            except: 
                data = (event['body'])
            result = data
            temp=(data["field"])
            val = (data["value"],event["queryStringParameters"]["id"])
            sql = "UPDATE organizations SET {0} = %s where id = %s ".format(temp) 
            try:
            # Executing the SQL command
                cursor.execute(sql, val)
        
            # Commit your changes in the database
                connection.commit();
                result = data
        
            except Exception as e:
            # Rolling back in case of error
                logger.error(e)
                connection.rollback()
                status_Code = 400
                result = {'response':"Bad Request",
                'description':"The request could not be understood by the server due to incorrect syntax. The client SHOULD NOT repeat the request without modifications."
                }
        elif event["httpMethod"] == "POST":
            status_Code = 400
            result = {'response':"Bad Request",
            'description':"The request could not be understood by the server due to incorrect syntax. The client SHOULD NOT repeat the request without modifications."
            }
            logger.error(result)
        elif event["httpMethod"] == "OPTIONS": 
             status_Code = 200
        else:
            status_Code = 501
            result = {'response':"Not Implemented",
            'description':"The HTTP method is not supported by the server and cannot be handled."
            }
            logger.error(result)
           
     
    else: 
        if event["httpMethod"] == "GET":
            try:
                # Executing the SQL command
                cursor.execute("SELECT * FROM organizations")
                rows = cursor.fetchall()
                for row in rows:
                    result.append(row)
            except Exception as e:
            # Rolling back in case of error
                logger.error(e)
                connection.rollback()
                status_Code = 400
                result = {'response':"Bad Request",
                'description':"The request could not be understood by the server due to incorrect syntax. The client SHOULD NOT repeat the request without modifications."
                }
            
        
        elif event["httpMethod"] == "POST":
            try:
                data = json.loads(event['body'])
            except: 
                data = (event['body'])
            cursor = connection.cursor()
           
        
            sql = """INSERT INTO organizations(
           name, concurrent_users, total_users, isDeleted)
           VALUES  (%s, %s, %s, %s)"""
            val = (data["name"], data["concurrent_users"], data["total_users"], data["isDeleted"])
        
            try:
            # Executing the SQL command
                cursor.execute(sql, val)
        
            # Commit your changes in the database
                connection.commit();
                result = data
                
            except Exception as e:
            # Rolling back in case of error
                logger.error(e)
                connection.rollback()
                status_Code = 400
                result = {'response':"Bad Request",
                'description':"The request could not be understood by the server due to incorrect syntax. The client SHOULD NOT repeat the request without modifications."
                }
                
        
        elif event["httpMethod"] == "PUT":
            try:
                data = json.loads(event['body'])
            except: 
                data = (event['body'])
            val = (data["name"], data["concurrent_users"], data["total_users"], data["isDeleted"])
            sql = "UPDATE organizations SET name = %s, concurrent_users = %s, total_users = %s, isDeleted = %s"
            
            try:
            # Executing the SQL command
                cursor.execute(sql, val)  
        
            # Commit your changes in the database
                connection.commit();
                result = data
        
            except Exception as e:
            # Rolling back in case of error
                logger.error(e)
                connection.rollback()
                status_Code = 400
                result = {'response':"Bad Request",
                'description':"The request could not be understood by the server due to incorrect syntax. The client SHOULD NOT repeat the request without modifications."
                }
               
        
        elif event["httpMethod"] == "DELETE":
            sql = "UPDATE organizations SET isDeleted = 1"
            try:
            # Executing the SQL command
                cursor.execute(sql)
        
            # Commit your changes in the database
                connection.commit();
                
        
            except Exception as e:
            # Rolling back in case of error
                logger.error(e)
                connection.rollback()
                status_Code = 400
                result = {'response':"Bad Request",
                'description':"The request could not be understood by the server due to incorrect syntax. The client SHOULD NOT repeat the request without modifications."
                }
                
        elif event["httpMethod"] == "PATCH":
            try:
                data = json.loads(event['body'])
            except: 
                data = (event['body'])
            result = data
            temp=(data["field"])
            val = (data["value"])
            sql = "UPDATE organizations SET {0} = %s ".format(temp) 
            try:
            # Executing the SQL command
                cursor.execute(sql, val)
        
            # Commit your changes in the database
                connection.commit();
                result = data
        
            except Exception as e:
            # Rolling back in case of error
                logger.error(e)
                connection.rollback()
                status_Code = 400
                result = {'response':"Bad Request",
                'description':"The request could not be understood by the server due to incorrect syntax. The client SHOULD NOT repeat the request without modifications."
                }
        elif event["httpMethod"] == "OPTIONS":
             status_Code = 200
        else:
            status_Code = 501
            result = {'response':"Not Implemented",
            'description':"The HTTP method is not supported by the server and cannot be handled."
            }
            logger.error(result)
                
    # except Exception as e:
    #     logger.error(e)
    #     status_Code = 500
    #     result = {'response':"Internal Server Error",
    #              'description':"The server encountered an unexpected condition that prevented it from fulfilling the request."
    #              }
    #     logger.error(result)

   
    
    response = {
        "statusCode": status_Code,
        "isBase64Encoded": False,
        "headers": {
            'Access-Control-Allow-Headers': 'Content-Type,X-Amz-Date,Authorization,X-Api-Key,X-Amz-Security-Token',
            'Access-Control-Allow-Origin': '*',
            'Access-Control-Allow-Methods': 'OPTIONS,POST,GET,PATCH,PUT,DELETE'
            
        },
        "body": json.dumps(result),
    }

    

    return response


  