from flask import jsonify, request
from flask_bcrypt import Bcrypt
from flask_jwt_extended import create_access_token
from config.database import get_db_connection, release_db_connection
import traceback
import logging

bcrypt = Bcrypt()
logger = logging.getLogger(__name__)


def register():
    print("\n" + "=" * 60)
    print(" REGISTER REQUEST")
    print("=" * 60)

    conn = None
    cursor = None

    try:
        data = request.get_json()
        print(f" Data received: {data}")

        email = data.get("email")
        password = data.get("password")
        name = data.get("name")  # ✅ SỬA: từ 'username' → 'name'

        print(f" Email: {email}, Name: {name}")

        # ✅ SỬA: Check đầy đủ
        if not email or not password or not name:
            return jsonify({"message": "Thiếu thông tin bắt buộc."}), 400

        conn = get_db_connection()
        cursor = conn.cursor()
        print(" Database connected")

        # Check if email already exists
        cursor.execute("SELECT id FROM users WHERE email = %s", (email,))
        if cursor.fetchone():
            cursor.close()
            release_db_connection(conn)
            return jsonify({"message": "Email đã tồn tại."}), 400

        print(" Email available")

        # Hash the password
        hashed_password = bcrypt.generate_password_hash(password).decode("utf-8")
        print(" Password hashed")

        # ✅ SỬA: VALUES (không phải VALUE)
        cursor.execute(
            """
            INSERT INTO users (email, password, username)
            VALUES (%s, %s, %s)
            RETURNING id, email, username
            """,
            (email, hashed_password, name),
        )

        user = cursor.fetchone()
        conn.commit()
        print(f" User created with ID: {user[0]}")

        # Generate JWT token (expiration configured in app.config)
        access_token = create_access_token(identity=str(user[0]))
        logger.info("Token created for user %s", user[0])

        cursor.close()
        release_db_connection(conn)

        # ✅ SỬA: Return 'token' (không phải 'access_token')
        response = {
            "message": "Đăng ký thành công!",
            "token": access_token,  # ✅ Frontend expect 'token'
            "user": {
                "id": user[0],
                "email": user[1],
                "name": user[2],  # ✅ Frontend expect 'name'
            },
        }

        print("✅ SUCCESS!")
        print("=" * 60 + "\n")
        return jsonify(response), 201

    except Exception as e:
        print(f"\n ERROR: {e}")
        traceback.print_exc()
        print("=" * 60 + "\n")

        if conn:
            conn.rollback()
        if cursor:
            cursor.close()
        if conn:
            release_db_connection(conn)

        return jsonify({"message": "Lỗi máy chủ", "error": str(e)}), 500


def login():
    print("\n LOGIN REQUEST")

    conn = None
    cursor = None

    try:
        data = request.get_json()
        email = data.get("email")
        password = data.get("password")

        if not email or not password:
            return jsonify({"message": "Thiếu email hoặc password."}), 400

        conn = get_db_connection()
        cursor = conn.cursor()

        # Fetch user by email
        cursor.execute(
            "SELECT id, email, username, password FROM users WHERE email = %s", (email,)
        )
        user = cursor.fetchone()

        cursor.close()
        release_db_connection(conn)

        if not user or not bcrypt.check_password_hash(user[3], password):
            return jsonify({"message": "Email hoặc mật khẩu không đúng."}), 401

        # Generate JWT token (expiration configured in app.config)
        access_token = create_access_token(identity=str(user[0]))

        return (
            jsonify(
                {
                    "message": "Đăng nhập thành công!",
                    "token": access_token,  # ✅ Frontend expect 'token'
                    "user": {
                        "id": user[0],
                        "email": user[1],
                        "name": user[2],  # ✅ Frontend expect 'name'
                    },
                }
            ),
            200,
        )

    except Exception as e:
        print(f"Login Error: {e}")
        traceback.print_exc()

        if conn:
            conn.rollback()
        if cursor:
            cursor.close()
        if conn:
            release_db_connection(conn)

        return jsonify({"message": "Lỗi máy chủ", "error": str(e)}), 500
