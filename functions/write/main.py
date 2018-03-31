import boto3
import json
import base64
import io
import zipfile

READ_URL_PREFIX = 'https://vu4fn1fim6.execute-api.us-west-2.amazonaws.com/live/'

def createZip(codeBody):
    # Zip up this code to an in-memory buffer
    zipBuffer = io.BytesIO()
    with zipfile.ZipFile(zipBuffer, 'w', zipfile.ZIP_DEFLATED) as iteratorZip:
        filename = zipfile.ZipInfo('main.py')

        # give full access to included file
        filename.external_attr = 0o755 << 16
        iteratorZip.writestr(filename, codeBody)
    return zipBuffer.getvalue()

# The body of a lambda function that'll redirect you to this url
def rawCode(rawUrl):
    # Base-64 encode the url so there are no interpolation + injection
    # shenanigans here.  We're concatonating user input with code then executing
    # it, so we need to be careful.
    encodedUrl = base64.b64encode(rawUrl.encode())

    return f"""
import base64
url = {encodedUrl}""" + """
url = base64.b64decode(url).decode()
def handle(event, context):
    return { 'url': url }
"""

def handle(event, context):
    # Grab the url from the post body and limit it to 1k characters
    url = json.loads(event['body'])['url'][:1000]

    # Grab the next identifier from our global iterator
    awsLambda = boto3.client('lambda')
    invokeResponse = awsLambda.invoke(
        FunctionName='shortener_iterator'
    )
    body = invokeResponse['Payload'].read()
    nextId = json.loads(body)['body']

    # Create a new lambda function for this link
    newFunctionName = f"shortener_read_{nextId}"
    codeConfig = {
        'ZipFile': createZip(rawCode(url))
    }
    awsLambda.create_function(
        FunctionName=newFunctionName,
        Runtime='python3.6',
        Role='arn:aws:iam::732378318181:role/sorter_lambda_function',
        Handler='main.handle',
        Code=codeConfig
    )

    return {
        'statusCode': 201,
        'body': READ_URL_PREFIX + nextId
    }

