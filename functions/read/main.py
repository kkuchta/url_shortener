import re
import json
import boto3

def handle(event, context):
    # Clean up the id parameter and limit it's length to something sensible
    id = event['pathParameters']['id']
    id = re.sub(r'[^a-zA-Z0-9]', '', id)[:10]

    function = f"shortener_read_{id}"

    awsLambda = boto3.client('lambda')
    invokeResponse = awsLambda.invoke(
        FunctionName=function
    )
    body = invokeResponse['Payload'].read()
    url = json.loads(body)['url']

    return {
        'statusCode': 301,
        'headers': {
            'Location': url
        }
    }
