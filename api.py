from flask import Flask, request, jsonify
from flask_cors import CORS
import requests
import os
from datetime import datetime
import json
import time

app = Flask(__name__)
CORS(app)

# ==================== HIDDEN API CONFIGURATION ====================
API_CONFIG = {
    'leak': 'https://lynx.mireiariosss.workers.dev/api/chain',
    'aadhar': 'https://lynx.mireiariosss.workers.dev/api/icmr/aadhar',
    'number': 'https://lynx.mireiariosss.workers.dev/api/search'
}

# ==================== HIDDEN API KEYS ====================
VALID_API_KEYS = {
    '@x_Traceowner': 'active',
    'Bhai': 'active',
    'Demo': 'active'
}

# ==================== API KEY VALIDATION ====================
def validate_api_key(f):
    def decorated_function(*args, **kwargs):
        api_key = request.args.get('key')
        if not api_key:
            return jsonify({'success': False, 'error': 'API key is required'}), 401
        if api_key not in VALID_API_KEYS:
            return jsonify({'success': False, 'error': 'Invalid API key'}), 401
        if VALID_API_KEYS[api_key] != 'active':
            return jsonify({'success': False, 'error': 'API key is inactive'}), 403
        return f(*args, **kwargs)
    decorated_function.__name__ = f.__name__
    return decorated_function

# ==================== FORWARD REQUEST ====================
def forward_request(service, params):
    original_url = API_CONFIG.get(service)
    if not original_url:
        return {'success': False, 'error': f'Service {service} not found'}, 404
    
    # Build URL with parameter
    param_value = list(params.values())[0]
    url = f"{original_url}/{param_value}"
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Accept': 'application/json, text/plain, */*',
        'Accept-Encoding': 'gzip, deflate',
        'Connection': 'keep-alive'
    }
    
    try:
        response = requests.get(url=url, headers=headers, timeout=60)
        
        # Parse response
        try:
            data = response.json()
        except:
            try:
                data = json.loads(response.text)
            except:
                data = {'success': True, 'data': response.text}
        
        # Clean unwanted text
        data = clean_response(data)
        
        # Parse nested JSON string if present
        data = parse_nested_json(data)
        
        # Add developer credit
        data = add_developer_credit(data)
        
        return data, response.status_code
            
    except requests.exceptions.Timeout:
        return {'success': False, 'error': 'Request timeout'}, 504
    except requests.exceptions.ConnectionError:
        return {'success': False, 'error': 'Service unavailable'}, 503
    except requests.exceptions.RequestException as e:
        return {'success': False, 'error': str(e)}, 500

# ==================== PARSE NESTED JSON ====================
def parse_nested_json(data):
    """Parse nested JSON strings into actual JSON objects"""
    if isinstance(data, dict):
        parsed_data = {}
        for key, value in data.items():
            if isinstance(value, str):
                # Try to parse if it looks like JSON
                value_stripped = value.strip()
                if value_stripped.startswith('{') or value_stripped.startswith('['):
                    try:
                        parsed_data[key] = json.loads(value_stripped)
                    except:
                        parsed_data[key] = value
                else:
                    parsed_data[key] = value
            elif isinstance(value, dict):
                parsed_data[key] = parse_nested_json(value)
            elif isinstance(value, list):
                parsed_data[key] = [parse_nested_json(item) if isinstance(item, (dict, str)) else item for item in value]
            else:
                parsed_data[key] = value
        return parsed_data
    elif isinstance(data, list):
        return [parse_nested_json(item) if isinstance(item, (dict, str)) else item for item in data]
    elif isinstance(data, str):
        data_stripped = data.strip()
        if data_stripped.startswith('{') or data_stripped.startswith('['):
            try:
                return json.loads(data_stripped)
            except:
                return data
        return data
    return data

# ==================== CLEAN RESPONSE ====================
def clean_response(data):
    """Remove unwanted text from response"""
    if isinstance(data, dict):
        cleaned_data = {}
        for key, value in data.items():
            if isinstance(value, str):
                value = value.replace('📱 join: @lynx_apis for more 🔥', '')
                value = value.replace('join: @lynx_apis for more', '')
                value = value.replace('@lynx_apis', '')
                value = value.strip()
                cleaned_data[key] = value
            elif isinstance(value, dict):
                cleaned_data[key] = clean_response(value)
            elif isinstance(value, list):
                cleaned_data[key] = [clean_response(item) if isinstance(item, (dict, str)) else item for item in value]
            else:
                cleaned_data[key] = value
        return cleaned_data
    elif isinstance(data, list):
        return [clean_response(item) if isinstance(item, (dict, str)) else item for item in data]
    elif isinstance(data, str):
        data = data.replace('📱 join: @lynx_apis for more 🔥', '')
        data = data.replace('join: @lynx_apis for more', '')
        data = data.replace('@lynx_apis', '')
        return data.strip()
    return data

def add_developer_credit(data):
    """Add developer credit to response"""
    if isinstance(data, dict):
        if 'error' in data and not data.get('success', True):
            data['Developer'] = '@x_Traceowner'
            return data
        
        data['Developer'] = '@x_Traceowner'
        return data
    return data

# ==================== ROUTES ====================

@app.route('/')
def home():
    return jsonify({
        'name': 'API Gateway 🔥',
        'version': '1.0',
        'status': 'active',
        'developer': '@x_Traceowner',
        'endpoints': {
            'leak': '/api/leak?key=YOUR_KEY&info=NUMBER',
            'aadhar': '/api/aadhar?key=YOUR_KEY&aadhar=AADHAR_NUMBER',
            'number': '/api/number?key=YOUR_KEY&info=NUMBER'
        },
        'note': 'Contact @x_Traceowner for API access'
    })

@app.route('/api/leak')
@validate_api_key
def leak_api():
    info = request.args.get('info')
    if not info:
        return jsonify({'error': 'info parameter is required'}), 400
    result, status = forward_request('leak', {'info': info})
    return jsonify(result), status

@app.route('/api/aadhar')
@validate_api_key
def aadhar_api():
    aadhar = request.args.get('aadhar')
    if not aadhar:
        return jsonify({'error': 'aadhar parameter is required'}), 400
    result, status = forward_request('aadhar', {'aadhar': aadhar})
    return jsonify(result), status

@app.route('/api/number')
@validate_api_key
def number_api():
    info = request.args.get('info')
    if not info:
        return jsonify({'error': 'info parameter is required'}), 400
    result, status = forward_request('number', {'info': info})
    return jsonify(result), status

@app.route('/health')
def health():
    return jsonify({
        'status': 'active',
        'timestamp': datetime.now().isoformat(),
        'developer': '@x_Traceowner'
    })

@app.errorhandler(404)
def not_found(error):
    return jsonify({'error': 'Endpoint not found', 'Developer': '@x_Traceowner'}), 404

@app.errorhandler(500)
def internal_error(error):
    return jsonify({'error': 'Internal server error', 'Developer': '@x_Traceowner'}), 500

# ==================== MAIN ====================
if __name__ == '__main__':
    port = int(os.environ.get('PORT', 8080))
    print("="*50)
    print("🚀 API Gateway Running")
    print("="*50)
    print(f"📡 Port: {port}")
    print(f"🔑 API Keys: {len(VALID_API_KEYS)} (Hidden)")
    print(f"👨‍💻 Developer: @x_Traceowner")
    print("="*50)
    app.run(host='0.0.0.0', port=port, debug=False)

# For Vercel
app = app