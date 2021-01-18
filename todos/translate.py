import os
import json

from todos import decimalencoder
import boto3
dynamodb = boto3.resource('dynamodb')


def translate(event, context):
    table = dynamodb.Table(os.environ['DYNAMODB_TABLE'])

    # fetch todo from the database
    result = table.get_item(
        Key={
            'id': event['pathParameters']['id']
        }
    )
    print(result)
    itemJson = json.dumps(result['Item'],cls=decimalencoder.DecimalEncoder)
    
    comprehend = boto3.client(service_name='comprehend', region_name='us-east-1')
    jsoncomprehen = json.loads(itemJson)

    langsourceJson=comprehend.detect_dominant_language(Text=jsoncomprehen['text'])
    print(langsourceJson)
    langSource=langsourceJson['Languages'][0]['LanguageCode']

    print(langSource)
    targetLanguage={
        'lang': event['pathParameters']['lang']
    }
    translate = boto3.client(service_name='translate', region_name='us-east-1', use_ssl=True)

    resultTranslate = translate.translate_text(Text=jsoncomprehen['text'], 
        SourceLanguageCode=langSource, TargetLanguageCode=targetLanguage['lang'])
    
    jsoncomprehen['text'] = resultTranslate

    # create a response
    response = {
        "statusCode": 200,
        "body": jsoncomprehen
    }

    return response
