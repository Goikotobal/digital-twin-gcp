import functions_framework
import json
import os
import urllib.request
import urllib.parse

@functions_framework.http
def chat_handler(request):
    """Ultra-simple chat handler using direct HTTP calls."""
    
    # CORS
    if request.method == 'OPTIONS':
        return ('', 204, {
            'Access-Control-Allow-Origin': '*',
            'Access-Control-Allow-Methods': 'POST, OPTIONS',
            'Access-Control-Allow-Headers': 'Content-Type',
        })

    headers_out = {
        'Access-Control-Allow-Origin': '*',
        'Content-Type': 'application/json'
    }

    try:
        request_json = request.get_json(silent=True)
        if not request_json:
            return (json.dumps({'error': 'Invalid JSON'}), 400, headers_out)

        user_message = request_json.get('message', '')
        
        if not user_message:
            return (json.dumps({'error': 'Message required'}), 400, headers_out)

        # Call Anthropic API directly via HTTP
        api_key = os.environ.get('ANTHROPIC_API_KEY', '')
        
        data = {
            "model": "claude-3-sonnet-20240229",
            "max_tokens": 1024,
            "messages": [{"role": "user", "content": user_message}]
        }
        
        req = urllib.request.Request(
            'https://api.anthropic.com/v1/messages',
            data=json.dumps(data).encode('utf-8'),
            headers={
                'Content-Type': 'application/json',
                'anthropic-version': '2023-06-01',
                'x-api-key': api_key
            }
        )
        
        with urllib.request.urlopen(req) as response:
            result = json.loads(response.read().decode('utf-8'))
            assistant_message = result['content'][0]['text']
        
        return (json.dumps({
            'response': assistant_message,
            'sessionId': request_json.get('sessionId', 'default')
        }), 200, headers_out)

    except Exception as e:
        return (json.dumps({
            'error': f'Error: {str(e)}'
        }), 500, headers_out)
