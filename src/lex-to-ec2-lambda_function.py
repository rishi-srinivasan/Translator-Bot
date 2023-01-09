import json
import boto3
import ast
import logging
import uuid

logger = logging.getLogger()
logger.setLevel(logging.INFO)

dynamodb = boto3.resource('dynamodb')
s3 = boto3.client('s3')
table = dynamodb.Table('translatorBot')
getMethod = 'GET'
translationPath = '/translation'

def lambda_handler(event, context):
    #Get data from Dynamo DB
    logger.info(event)
    httpMethod = event['httpMethod']
    path = event['path']
    if httpMethod == getMethod and path == translationPath:
        response = getTranslations()
    else:
        response = buildResponse(404,'Not Found')
        
    #Store data in S3 bucket - translatorbot-datalake
    bucket = 'translatorbot-datalake'
    filename = str(uuid.uuid4())+'_translated.json'
    jsonFile = bytes(json.dumps(response['body']).encode('UTF-8'))
    s3.put_object(Bucket = bucket, Key=filename, Body=jsonFile)
    print('Data Stored in S3 bucket - translatorbot-datalake')
    return response
    
    
def getTranslations():
    try:
        response = table.scan()
        data = response['Items']
        
        while 'LastEvaluatedKey' in response:
            response = table.scan(ExclusiveStartKey=response['LastEvaluatedKey'])
            data.extend(response['Items'])
            #print(data)
            
        body = {
            'translations': data
        }
        return buildResponse(200, body)
    except:
        logger.exception('Error Found. Need to perform error handling!')
    
def buildResponse(statusCode, body=None):
    response = {
        'statusCode':statusCode,
        'headers':{
            'Content-Type':'application/json',
            'Access-Control-Allow-Origin':'*'
        }
    }
    if body is not None:
        response['body'] = json.dumps(body)
    return response
