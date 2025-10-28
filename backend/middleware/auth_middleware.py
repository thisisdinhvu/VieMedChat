from flask import jsonify, request
from flask_jwt_extended import verify_jwt_in_request, get_jwt_identity
from functools import wraps

def token_required(f):
    """Decorator để check JWT token trong request"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        try:
            print("\n" + "="*60)
            print("🔐 AUTH MIDDLEWARE CHECK")
            print("="*60)
            print(f"Request: {request.method} {request.path}")
            print(f"Headers: {dict(request.headers)}")
            
            auth_header = request.headers.get('Authorization')
            print(f"Authorization header: {auth_header}")
            
            if not auth_header:
                print("❌ No Authorization header!")
                return jsonify({
                    "message": "Thiếu token xác thực"
                }), 401
            
            if not auth_header.startswith('Bearer '):
                print("❌ Authorization header doesn't start with 'Bearer '")
                return jsonify({
                    "message": "Token format không đúng"
                }), 401
            
            print("✅ Verifying JWT...")
            verify_jwt_in_request()
            
            user_id = get_jwt_identity()
            print(f"✅ Token valid! User ID: {user_id}")
            print("="*60 + "\n")
            
            return f(user_id, *args, **kwargs)
            
        except Exception as e:
            print(f"❌ JWT Verification failed: {e}")
            print(f"Error type: {type(e).__name__}")
            print("="*60 + "\n")
            
            return jsonify({
                "message": "Token không hợp lệ hoặc đã hết hạn.", 
                'error': str(e)
            }), 401
    
    return decorated_function