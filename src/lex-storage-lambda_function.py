import json
import datetime
import time
import os
import dateutil.parser
import logging
import boto3
import uuid
import ast

logger = logging.getLogger()
logger.setLevel(logging.DEBUG)

print('Loading function')

def lambda_handler(event, context):
    #Receive values from SNS - translatorBot_DynamoDB_Storage
    message = event['Records'][0]['Sns']['Message']
    message1 = ast.literal_eval(message)
    phrase = message1['phrase_text']
    source_lang = message1['source']
    target_lang = message1['target']
    translatedText = message1['trans_text']
    
    
    dynamodb = boto3.resource('dynamodb')
    table = dynamodb.Table('translatorBot')
    table.put_item(
        Item={
            'id' : str(uuid.uuid4()),
            'original_text' : phrase,
            'source_language' : source_lang,
            'target_language' : target_lang,
            'translated_text' : translatedText
            }
            )
            
    #Trigger SNS Service - translatorBot_triggerLexDataToEC2
    arn = "arn:aws:sns:us-east-1:626480635631:translatorBot_triggerLexDataToEC2"
    message = "Trigger Lambda function - lexDataToEC2"
    client = boto3.client('sns')
    response = client.publish(
    TargetArn=arn,
    Message=json.dumps({'default': json.dumps(message)}),
    MessageStructure='json')
