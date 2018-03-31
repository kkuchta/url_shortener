def handle(event, context):
    with open('./index.html', 'r') as indexFile:
        body=indexFile.read()
    return {
        'statusCode': 200,
        'body': body,
        'headers': {
            'Content-Type': 'text/html'
        }
    }
