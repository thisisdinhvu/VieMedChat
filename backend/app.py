# # from flask import Flask, jsonify
# # from flask_cors import CORS
# # from flask_jwt_extended import JWTManager
# # from dotenv import load_dotenv
# # import os

# # from config.database import init_db
# # from routes.api.authentication import auth_bp
# # from routes.api.chat import chat_bp

# # load_dotenv()

# # app = Flask(__name__)

# # app.config['JWT_SECRET_KEY'] = os.getenv('JWT_SECRET_KEY')
# # app.config['JWT_TOKEN_LOCATION'] = ['headers']
# # app.config['JWT_HEADER_NAME'] = 'Authorization'
# # app.config['JWT_HEADER_TYPE'] = 'Bearer'

# # CORS(app)

# # jwt = JWTManager(app)

# # # Initialize Database
# # with app.app_context():
# #     init_db()

# # # Register blueprints
# # app.register_blueprint(auth_bp, url_prefix='/api/auth')
# # app.register_blueprint(chat_bp, url_prefix='/api/chat')

# # # Health check route
# # @app.route('/')
# # def home():
# #     return jsonify({'message': 'Chatbot API is running with Python! 🐍'})

# # # Error handlers
# # @app.errorhandler(404)
# # def not_found(error):
# #     return jsonify({'message': 'Route không tồn tại'}), 404

# # @app.errorhandler(500)
# # def internal_error(error):
# #     return jsonify({'message': 'Lỗi server', 'error': str(error)}), 500

# # if __name__ == '__main__':
# #     port = int(os.getenv('PORT', 5000))
# #     app.run(
# #         host='0.0.0.0',
# #         port=port,
# #         debug=os.getenv('FLASK_ENV') == 'development'
# #     )

# from flask import Flask, jsonify
# from flask_cors import CORS
# from flask_jwt_extended import JWTManager
# from dotenv import load_dotenv
# import os

# # Load .env TRƯỚC KHI import database
# load_dotenv()

# from config.database import init_db
# from routes.api.auth_routes import auth_bp
# from routes.api.chat_routes import chat_bp

# app = Flask(__name__)

# # Config
# app.config['JWT_SECRET_KEY'] = os.getenv('JWT_SECRET_KEY')
# app.config['JWT_TOKEN_LOCATION'] = ['headers']
# app.config['JWT_HEADER_NAME'] = 'Authorization'
# app.config['JWT_HEADER_TYPE'] = 'Bearer'

# app.config['JWT_ACCESS_TOKEN_EXPIRES'] = False  # Không hết hạn (hoặc timedelta(days=7))
# app.config['PROPAGATE_EXCEPTIONS'] = True

# # CORS - cho phép tất cả origins trong dev
# CORS(app, resources={r"/api/*": {"origins": "*"}})

# jwt = JWTManager(app)

# # Initialize Database
# print("🔄 Initializing database...")
# try:
#     with app.app_context():
#         init_db()
#     print("✅ Database initialized successfully!")
# except Exception as e:
#     print(f"❌ Database initialization failed: {e}")
#     import traceback
#     traceback.print_exc()

# # Register blueprints
# app.register_blueprint(auth_bp, url_prefix='/api/auth')
# app.register_blueprint(chat_bp, url_prefix='/api/chat')

# print("📝 Registered routes:")
# for rule in app.url_map.iter_rules():
#     print(f"  {rule.endpoint}: {rule.rule}")

# # Health check route
# @app.route('/')
# def home():
#     return jsonify({'message': 'Chatbot API is running with Python! 🐍'})

# # Error handlers
# @app.errorhandler(404)
# def not_found(error):
#     return jsonify({'message': 'Route không tồn tại'}), 404

# @app.errorhandler(500)
# def internal_error(error):
#     print(f"❌ 500 Error: {error}")
#     import traceback
#     traceback.print_exc()
#     return jsonify({'message': 'Lỗi server', 'error': str(error)}), 500

# if __name__ == '__main__':
#     port = int(os.getenv('PORT', 5000))
#     print(f"\n🚀 Starting server on http://localhost:{port}")
#     print(f"📚 Environment: {os.getenv('FLASK_ENV', 'production')}")
#     print(f"🔑 JWT Secret: {'SET ✅' if os.getenv('JWT_SECRET_KEY') else 'MISSING ❌'}")
#     print(f"🗄️  Database Host: {os.getenv('DB_HOST', 'MISSING ❌')}")
#     print(f"🗄️  Database Name: {os.getenv('DB_NAME', 'MISSING ❌')}\n")
    
#     app.run(
#         host='0.0.0.0',
#         port=port,
#         debug=True
#     )

from flask import Flask, jsonify
from flask_cors import CORS
from flask_jwt_extended import JWTManager
from dotenv import load_dotenv
import os

load_dotenv()

from config.database import init_db
from routes.api.auth_routes import auth_bp
from routes.api.chat_routes import chat_bp

app = Flask(__name__)

# ✅ JWT Configuration - QUAN TRỌNG!
app.config['JWT_SECRET_KEY'] = os.getenv('JWT_SECRET_KEY')
app.config['JWT_TOKEN_LOCATION'] = ['headers']
app.config['JWT_HEADER_NAME'] = 'Authorization'
app.config['JWT_HEADER_TYPE'] = 'Bearer'

# ✅ Thêm các config này:
app.config['JWT_ACCESS_TOKEN_EXPIRES'] = False  # Không hết hạn (hoặc timedelta(days=7))
app.config['PROPAGATE_EXCEPTIONS'] = True

# CORS
CORS(app, resources={
    r"/api/*": {
        "origins": "*",
        "methods": ["GET", "POST", "PUT", "DELETE", "OPTIONS"],
        "allow_headers": ["Content-Type", "Authorization"]
    }
})

# ✅ Initialize JWT AFTER config
jwt = JWTManager(app)

# ✅ JWT Error Handlers
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
        debug=True
    )
