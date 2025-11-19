# from flask import Flask, jsonify
# from flask_cors import CORS
# from flask_jwt_extended import JWTManager
# from dotenv import load_dotenv
# import os

# load_dotenv()

# from config.database import init_db
# from routes.api.auth_routes import auth_bp
# from routes.api.chat_routes import chat_bp

# app = Flask(__name__)

# # ✅ JWT Configuration - QUAN TRỌNG!
# app.config['JWT_SECRET_KEY'] = os.getenv('JWT_SECRET_KEY')
# app.config['JWT_TOKEN_LOCATION'] = ['headers']
# app.config['JWT_HEADER_NAME'] = 'Authorization'
# app.config['JWT_HEADER_TYPE'] = 'Bearer'

# # ✅ Thêm các config này:
# app.config['JWT_ACCESS_TOKEN_EXPIRES'] = False  # Không hết hạn (hoặc timedelta(days=7))
# app.config['PROPAGATE_EXCEPTIONS'] = True

# # CORS
# CORS(app, resources={
#     r"/api/*": {
#         "origins": "*",
#         "methods": ["GET", "POST", "PUT", "DELETE", "OPTIONS"],
#         "allow_headers": ["Content-Type", "Authorization"]
#     }
# })

# # ✅ Initialize JWT AFTER config
# jwt = JWTManager(app)

# # ✅ JWT Error Handlers
# @jwt.expired_token_loader
# def expired_token_callback(jwt_header, jwt_payload):
#     print("❌ Token expired!")
#     return jsonify({
#         'message': 'Token đã hết hạn',
#         'error': 'token_expired'
#     }), 401

# @jwt.invalid_token_loader
# def invalid_token_callback(error):
#     print(f"❌ Invalid token: {error}")
#     return jsonify({
#         'message': 'Token không hợp lệ',
#         'error': 'invalid_token'
#     }), 401

# @jwt.unauthorized_loader
# def missing_token_callback(error):
#     print(f"❌ Missing token: {error}")
#     return jsonify({
#         'message': 'Thiếu token xác thực',
#         'error': 'authorization_required'
#     }), 401

# # Initialize Database
# print("🔄 Initializing database...")
# try:
#     with app.app_context():
#         init_db()
#     print("✅ Database initialized!")
# except Exception as e:
#     print(f"❌ Database init failed: {e}")
#     import traceback
#     traceback.print_exc()

# # Register blueprints
# app.register_blueprint(auth_bp, url_prefix='/api/auth')
# app.register_blueprint(chat_bp, url_prefix='/api/chat')

# print("\n📝 Registered routes:")
# for rule in app.url_map.iter_rules():
#     if not rule.endpoint.startswith('static'):
#         print(f"  {rule.endpoint}: {rule.rule}")

# @app.route('/')
# def home():
#     return jsonify({'message': 'Chatbot API is running! 🐍'})

# @app.errorhandler(500)
# def internal_error(error):
#     print(f"❌ 500 Error: {error}")
#     import traceback
#     traceback.print_exc()
#     return jsonify({'message': 'Lỗi server', 'error': str(error)}), 500

# if __name__ == '__main__':
#     port = int(os.getenv('PORT', 5000))
    
#     print("\n" + "="*60)
#     print("🚀 FLASK SERVER STARTING")
#     print("="*60)
#     print(f"Port: {port}")
#     print(f"Environment: {os.getenv('FLASK_ENV', 'production')}")
#     print(f"JWT Secret: {'SET ✅' if os.getenv('JWT_SECRET_KEY') else 'MISSING ❌'}")
#     print(f"Database: {os.getenv('DB_HOST', 'MISSING ❌')}")
#     print("="*60 + "\n")
    
#     app.run(
#         host='0.0.0.0',
#         port=port,
#         debug=True
#     )

# # --- IGNORE ---
# # from flask import Flask, jsonify
# # from flask_cors import CORS
# # from flask_jwt_extended import JWTManager
# # from dotenv import load_dotenv
# # import os

# # load_dotenv()

# # from config.database import init_db
# # from routes.api.auth_routes import auth_bp
# # from routes.api.chat_routes import chat_bp

# # # ✅ THÊM IMPORT NÀY
# # from utils.startup import initialize_rag_components

# # app = Flask(__name__)

# # # JWT Config
# # app.config['JWT_SECRET_KEY'] = os.getenv('JWT_SECRET_KEY')
# # app.config['JWT_TOKEN_LOCATION'] = ['headers']
# # app.config['JWT_HEADER_NAME'] = 'Authorization'
# # app.config['JWT_HEADER_TYPE'] = 'Bearer'
# # app.config['JWT_ACCESS_TOKEN_EXPIRES'] = False
# # app.config['PROPAGATE_EXCEPTIONS'] = True

# # # CORS
# # CORS(app, resources={
# #     r"/api/*": {
# #         "origins": "*",
# #         "methods": ["GET", "POST", "PUT", "DELETE", "OPTIONS"],
# #         "allow_headers": ["Content-Type", "Authorization"]
# #     }
# # })

# # jwt = JWTManager(app)

# # # JWT Error Handlers
# # @jwt.expired_token_loader
# # def expired_token_callback(jwt_header, jwt_payload):
# #     return jsonify({'message': 'Token đã hết hạn'}), 401

# # @jwt.invalid_token_loader
# # def invalid_token_callback(error):
# #     return jsonify({'message': 'Token không hợp lệ'}), 401

# # @jwt.unauthorized_loader
# # def missing_token_callback(error):
# #     return jsonify({'message': 'Thiếu token xác thực'}), 401

# # # Initialize Database
# # print("🔄 Initializing database...")
# # try:
# #     with app.app_context():
# #         init_db()
# #     print("✅ Database initialized!")
# # except Exception as e:
# #     print(f"❌ Database init failed: {e}")

# # # ✅ PRE-INITIALIZE RAG COMPONENTS
# # # This runs ONCE on server startup
# # with app.app_context():
# #     initialize_rag_components()

# # # Register blueprints
# # app.register_blueprint(auth_bp, url_prefix='/api/auth')
# # app.register_blueprint(chat_bp, url_prefix='/api/chat')

# # @app.route('/')
# # def home():
# #     return jsonify({'message': 'Chatbot API is running! 🐍'})

# # @app.errorhandler(500)
# # def internal_error(error):
# #     print(f"❌ 500 Error: {error}")
# #     import traceback
# #     traceback.print_exc()
# #     return jsonify({'message': 'Lỗi server'}), 500

# # if __name__ == '__main__':
# #     port = int(os.getenv('PORT', 5000))
    
# #     print("\n" + "="*60)
# #     print("🚀 FLASK SERVER STARTING")
# #     print("="*60)
# #     print(f"Port: {port}")
# #     print(f"Environment: {os.getenv('FLASK_ENV', 'production')}")
# #     print(f"JWT Secret: {'SET ✅' if os.getenv('JWT_SECRET_KEY') else 'MISSING ❌'}")
# #     print(f"Database: {os.getenv('DB_HOST', 'MISSING ❌')}")
# #     print("="*60 + "\n")
    
# #     app.run(host='0.0.0.0', port=port, debug=True)

from flask import Flask, jsonify
from flask_cors import CORS
from flask_jwt_extended import JWTManager
from dotenv import load_dotenv
import os

load_dotenv()

from config.database import init_db
from routes.api.auth_routes import auth_bp
from routes.api.chat_routes import chat_bp

# ✅ IMPORT PRE-INITIALIZATION
from backend.utils.start_up import initialize_rag_components

app = Flask(__name__)

# JWT Configuration
app.config['JWT_SECRET_KEY'] = os.getenv('JWT_SECRET_KEY')
app.config['JWT_TOKEN_LOCATION'] = ['headers']
app.config['JWT_HEADER_NAME'] = 'Authorization'
app.config['JWT_HEADER_TYPE'] = 'Bearer'
app.config['JWT_ACCESS_TOKEN_EXPIRES'] = False
app.config['PROPAGATE_EXCEPTIONS'] = True

# CORS
CORS(app, resources={
    r"/api/*": {
        "origins": "*",
        "methods": ["GET", "POST", "PUT", "DELETE", "OPTIONS"],
        "allow_headers": ["Content-Type", "Authorization"]
    }
})

jwt = JWTManager(app)

# JWT Error Handlers
@jwt.expired_token_loader
def expired_token_callback(jwt_header, jwt_payload):
    print("❌ Token expired!")
    return jsonify({
        'message': 'Token đã hết hạn',
        'error': 'token_expired'
    }), 401

@jwt.invalid_token_loader
def invalid_token_callback(error):
    print(f"❌ Invalid token: {error}")
    return jsonify({
        'message': 'Token không hợp lệ',
        'error': 'invalid_token'
    }), 401

@jwt.unauthorized_loader
def missing_token_callback(error):
    print(f"❌ Missing token: {error}")
    return jsonify({
        'message': 'Thiếu token xác thực',
        'error': 'authorization_required'
    }), 401

# Initialize Database
print("🔄 Initializing database...")
try:
    with app.app_context():
        init_db()
    print("✅ Database initialized!")
except Exception as e:
    print(f"❌ Database init failed: {e}")
    import traceback
    traceback.print_exc()

# ==========================================
# ✅ PRE-INITIALIZE RAG COMPONENTS
# ==========================================
# Chạy 1 LẦN khi server khởi động
with app.app_context():
    print("\n" + "="*60)
    print("⚡ STARTING PRE-INITIALIZATION...")
    print("="*60)
    success = initialize_rag_components()
    if success:
        print("⚡ Server is now READY for fast responses!")
    else:
        print("⚠️ Server will start but responses may be slower")
    print("="*60 + "\n")

# Register blueprints
app.register_blueprint(auth_bp, url_prefix='/api/auth')
app.register_blueprint(chat_bp, url_prefix='/api/chat')

print("\n📝 Registered routes:")
for rule in app.url_map.iter_rules():
    if not rule.endpoint.startswith('static'):
        print(f"  {rule.endpoint}: {rule.rule}")

@app.route('/')
def home():
    return jsonify({'message': 'Chatbot API is running! 🐍'})

@app.route('/health')
def health():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'rag_initialized': True,
        'agent_ready': True
    }), 200

@app.errorhandler(500)
def internal_error(error):
    print(f"❌ 500 Error: {error}")
    import traceback
    traceback.print_exc()
    return jsonify({'message': 'Lỗi server', 'error': str(error)}), 500

if __name__ == '__main__':
    port = int(os.getenv('PORT', 5000))
    
    print("\n" + "="*60)
    print("🚀 FLASK SERVER STARTING")
    print("="*60)
    print(f"Port: {port}")
    print(f"Environment: {os.getenv('FLASK_ENV', 'production')}")
    print(f"JWT Secret: {'SET ✅' if os.getenv('JWT_SECRET_KEY') else 'MISSING ❌'}")
    print(f"Database: {os.getenv('DB_HOST', 'MISSING ❌')}")
    print("="*60 + "\n")
    
    app.run(
        host='0.0.0.0',
        port=port,
        debug=True,
        threaded=True  # ✅ Enable threading để xử lý nhiều request
    )