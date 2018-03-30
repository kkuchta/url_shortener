import boto3
import json
import base64
import io
import zipfile

def createZip(codeBody):
    zipBuffer = io.BytesIO()

    # Zip up this code to an in-memory buffer
    with zipfile.ZipFile(zipBuffer, 'w', zipfile.ZIP_DEFLATED) as iteratorZip:
        filename = zipfile.ZipInfo('main.py')

        # give full access to included file
        filename.external_attr = 0o755 << 16

        iteratorZip.writestr(filename, codeBody)
    #with open("/tmp/output.zip", "wb") as tmp_file:
        #tmp_file.write(zipBuffer.getvalue())
    return zipBuffer.getvalue()

def rawCode(rawUrl):
    # Base-64 encode the url so there are no interpolation + injection
    # shenanigans here.  We're concatonating user input with code then executing
    # it, so we need to be careful.
    encodedUrl = base64.b64encode(rawUrl.encode())

    # TODO: return a 30X redirect instead of the url in a body here
    return f"""
import base64
url = {encodedUrl}""" + """
url = base64.b64decode(url).decode()
def handle(event, context):
    return { 'url': url }
"""

def handle(event, context):

    # TODO: pull this from event
    url = 'http://kevinkuchta.com'

    # Grab the next identifier from our global iterator
    awsLambda = boto3.client('lambda')
    invokeResponse = awsLambda.invoke(
        FunctionName='shortener_iterator'
    )
    body = invokeResponse['Payload'].read()
    nextId = json.loads(body)['body']

    newFunctionName = f"shortener_read_{nextId}"
    print('rawcode=', rawCode(url))
    print('creating a function named', newFunctionName)
    codeConfig = {
        'ZipFile': createZip(rawCode(url))
    }
    createResponse = awsLambda.create_function(
        FunctionName=newFunctionName,
        Runtime='python3.6',
        Role='arn:aws:iam::732378318181:role/sorter_lambda_function',
        Handler='main.handle',
        Code=codeConfig
    )

    return { 'id': nextId }

