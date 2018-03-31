import re
import json
import boto3

def handle(event, context):
    # Get the id from the url and clean it up
    id = event['pathParameters']['id']
    id = re.sub(r'[^a-zA-Z0-9]', '', id)[:10]

    # Run the lambda read function for that id
    awsLambda = boto3.client('lambda')
    try:
        invokeResponse = awsLambda.invoke(FunctionName=f"shortener_read_{id}")
    except awsLambda.exceptions.ResourceNotFoundException:
        return { 'statusCode': 404, 'body': 'Unknown short link' }

    # Redirect to the result
    body = invokeResponse['Payload'].read()
    url = json.loads(body)['url']
    return {
        'statusCode': 301,
        'headers': { 'Location': url }
    }
