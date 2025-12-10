# -*- coding: utf-8 -*-
"""
VieMedChat Backend - Flask Application
"""

import os
import sys
import traceback
import logging

# Fix Windows console UTF-8 encoding
if sys.platform == "win32":
    import io

    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding="utf-8", errors="replace")
from datetime import timedelta
from dotenv import load_dotenv
from flask import Flask, jsonify
from flask_cors import CORS
from flask_jwt_extended import JWTManager
from config.database import init_db
from routes.api.auth_routes import auth_bp
from routes.api.chat_routes import chat_bp

# IMPORT PRE-INITIALIZATION (relative import)
from utils.start_up import initialize_rag_components

load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

# Initialize Flask app
app = Flask(__name__)
app.config["JWT_SECRET_KEY"] = os.getenv("JWT_SECRET_KEY")
app.config["JWT_TOKEN_LOCATION"] = ["headers"]
app.config["JWT_HEADER_NAME"] = "Authorization"
app.config["JWT_HEADER_TYPE"] = "Bearer"
app.config["JWT_ACCESS_TOKEN_EXPIRES"] = timedelta(days=7)
app.config["PROPAGATE_EXCEPTIONS"] = True
app.config["JSON_AS_ASCII"] = False  # Enable proper UTF-8 in JSON responses

# CORS Configuration
# NOTE: In production, replace wildcards with specific domains for security
CORS(
    app,
    resources={
        r"/api/*": {
            "origins": [
                "http://localhost:3000",
                "https://*.ngrok.io",
                "https://*.ngrok-free.app",
                "https://*.vercel.app",
            ],
            "methods": ["GET", "POST", "PUT", "DELETE", "OPTIONS"],
            "allow_headers": [
                "Content-Type",
                "Authorization",
                "ngrok-skip-browser-warning",
            ],
        }
    },
)

jwt = JWTManager(app)


# JWT Error Handlers
@jwt.expired_token_loader
def expired_token_callback(jwt_header, jwt_payload):
    print("Token expired!")
    return jsonify({"message": "Token da het han", "error": "token_expired"}), 401


@jwt.invalid_token_loader
def invalid_token_callback(error):
    print(f"Invalid token: {error}")
    return jsonify({"message": "Token khong hop le", "error": "invalid_token"}), 401


@jwt.unauthorized_loader
def missing_token_callback(error):
    print(f"Missing token: {error}")
    return (
        jsonify({"message": "Thieu token xac thuc", "error": "authorization_required"}),
        401,
    )


# Initialize Database
print("Initializing database...")
try:
    with app.app_context():
        init_db()
    print("Database initialized!")
except Exception as e:
    print(f"Database init failed: {e}")
    traceback.print_exc()

# ==========================================
# PRE-INITIALIZE RAG COMPONENTS
# ==========================================
_rag_initialized = False
_agent_ready = False

logger.info("=" * 60)
logger.info("STARTING PRE-INITIALIZATION...")
logger.info("=" * 60)

_initialized = initialize_rag_components()
_rag_initialized = _initialized
_agent_ready = _initialized

if _initialized:
    logger.info("Server is now READY for fast responses!")
else:
    logger.warning("Server will start but responses may be slower")
logger.info("=" * 60)

# Register blueprints
app.register_blueprint(auth_bp, url_prefix="/api/auth")
app.register_blueprint(chat_bp, url_prefix="/api/chat")

# Print registered routes
print("\nRegistered routes:")
for rule in app.url_map.iter_rules():
    if rule.endpoint != "static":
        print(f"  {rule.endpoint}: {rule.rule}")


# Health check endpoint
@app.route("/")
def home():
    return jsonify({"message": "VieMedChat API is running", "status": "ok"})


@app.route("/health")
def health():
    status_code = 200 if (_rag_initialized and _agent_ready) else 503
    return (
        jsonify(
            {
                "status": "healthy" if status_code == 200 else "degraded",
                "rag_initialized": _rag_initialized,
                "agent_ready": _agent_ready,
            }
        ),
        status_code,
    )


@app.errorhandler(500)
def internal_error(error):
    print(f"500 Error: {error}")
    import traceback

    traceback.print_exc()
    return jsonify({"message": "Loi server", "error": str(error)}), 500


if __name__ == "__main__":
    port = int(os.getenv("PORT", 5000))

    print("\n" + "=" * 60)
    print("FLASK SERVER STARTING")
    print("=" * 60)
    print(f"Port: {port}")
    print(f"Environment: {os.getenv('FLASK_ENV', 'production')}")
    print(f"JWT Secret: {'SET' if os.getenv('JWT_SECRET_KEY') else 'MISSING'}")
    print(f"Database: {os.getenv('DB_HOST', 'MISSING')}")
    print("=" * 60 + "\n")

    app.run(
        host="0.0.0.0",
        port=port,
        debug=True,
        threaded=True,
    )
