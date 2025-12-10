from flask import jsonify, request
from config.database import get_db_connection, release_db_connection
from config.constants import ChatConfig
from utils.rag_service import call_rag_gemini
import traceback
import logging

logger = logging.getLogger(__name__)


def create_conversation(user_id):
    """Create a new conversation"""
    logger.info(f"Creating conversation for user {user_id}")

    conn = None
    cursor = None

    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        cursor.execute(
            """
            INSERT INTO conversations (user_id, title)
            VALUES (%s, %s)
            RETURNING id, user_id, title, created_at, updated_at
            """,
            (user_id, "New Chat"),
        )

        conversation = cursor.fetchone()
        conn.commit()

        cursor.close()
        release_db_connection(conn)

        result = {
            "id": conversation[0],
            "user_id": conversation[1],
            "title": conversation[2],
            "created_at": conversation[3].isoformat(),
            "updated_at": conversation[4].isoformat(),
        }

        logger.info(f"Conversation created: {result}")
        return jsonify(result), 201

    except Exception as e:
        logger.error(f"Error creating conversation: {e}")
        traceback.print_exc()

        if conn:
            conn.rollback()
        if cursor:
            cursor.close()
        if conn:
            release_db_connection(conn)

        return (
            jsonify({"message": "Lỗi khi tạo cuộc trò chuyện.", "error": str(e)}),
            500,
        )


def get_conversations(user_id):
    """Get all conversations for a user"""
    logger.info(f"Getting conversations for user {user_id}")

    conn = None
    cursor = None

    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        cursor.execute(
            """
            SELECT id, user_id, title, created_at, updated_at
            FROM conversations
            WHERE user_id = %s
            ORDER BY updated_at DESC
            """,
            (user_id,),
        )

        conversations = cursor.fetchall()
        cursor.close()
        release_db_connection(conn)

        results = []
        for conv in conversations:
            results.append(
                {
                    "id": conv[0],
                    "user_id": conv[1],
                    "title": conv[2],
                    "created_at": conv[3].isoformat(),
                    "updated_at": conv[4].isoformat(),
                }
            )

        logger.info(f"Found {len(results)} conversations")
        return jsonify(results), 200

    except Exception as e:
        logger.error(f"Error getting conversations: {e}")
        traceback.print_exc()

        if cursor:
            cursor.close()
        if conn:
            release_db_connection(conn)

        return (
            jsonify({"message": "Lỗi khi lấy cuộc trò chuyện.", "error": str(e)}),
            500,
        )


def send_message(user_id):
    """Send a message in a conversation and get AI response"""
    logger.info(f"Sending message from user {user_id}")

    conn = None
    cursor = None

    try:
        data = request.get_json()
        logger.debug(f"Data received: {data}")

        # Frontend gửi 'conversationId' (camelCase)
        conversation_id = data.get("conversationId")
        content = data.get("content")

        if not conversation_id or not content:
            return jsonify({"message": "Thiếu thông tin."}), 400

        conn = get_db_connection()
        cursor = conn.cursor()

        # Insert user message
        logger.info(f"Inserting user message to conversation {conversation_id}")
        cursor.execute(
            """
            INSERT INTO messages (conversation_id, sender, content)
            VALUES (%s, %s, %s)
            RETURNING id, conversation_id, sender, content, timestamp
            """,
            (conversation_id, "user", content),
        )

        user_message = cursor.fetchone()
        conn.commit()
        logger.info(f"User message saved with ID: {user_message[0]}")

        # Fetch conversation history (using config constant)
        logger.info("Fetching conversation history...")
        cursor.execute(
            """
            SELECT sender, content
            FROM messages
            WHERE conversation_id = %s
            ORDER BY timestamp DESC
            LIMIT %s
            """,
            (conversation_id, ChatConfig.CHAT_HISTORY_LIMIT),
        )

        history = cursor.fetchall()
        history.reverse()  # Reverse to chronological order

        # Build messages for Gemini API
        messages = []
        for msg in history:
            messages.append(
                {"role": "user" if msg[0] == "user" else "assistant", "content": msg[1]}
            )

        logger.info(f"Calling Gemini with {len(messages)} messages...")

        # Call RAG API
        ai_response_content = call_rag_gemini(messages)
        logger.info(f"Gemini response received: {ai_response_content[:50]}...")

        # Save AI response
        cursor.execute(
            """
            INSERT INTO messages (conversation_id, sender, content)
            VALUES (%s, %s, %s)
            RETURNING id, conversation_id, sender, content, timestamp
            """,
            (conversation_id, "bot", ai_response_content),
        )

        bot_message = cursor.fetchone()

        # Update conversation timestamp
        cursor.execute(
            """
            UPDATE conversations
            SET updated_at = CURRENT_TIMESTAMP
            WHERE id = %s
            """,
            (conversation_id,),
        )

        conn.commit()
        logger.info(f"Bot message saved with ID: {bot_message[0]}")

        cursor.close()
        release_db_connection(conn)

        # Return format matches frontend expectations (camelCase)
        result = {
            "userMessage": {
                "id": user_message[0],
                "conversation_id": user_message[1],
                "sender": user_message[2],
                "content": user_message[3],
                "timestamp": user_message[4].isoformat(),
            },
            "botMessage": {
                "id": bot_message[0],
                "conversation_id": bot_message[1],
                "sender": bot_message[2],
                "content": bot_message[3],
                "timestamp": bot_message[4].isoformat(),
            },
        }

        logger.info("Message sent successfully with RAG!")
        return jsonify(result), 200

    except Exception as e:
        logger.error(f"Error sending message: {e}")
        traceback.print_exc()

        if conn:
            conn.rollback()
        if cursor:
            cursor.close()
        if conn:
            release_db_connection(conn)

        return jsonify({"message": "Lỗi khi gửi tin nhắn.", "error": str(e)}), 500


def get_messages(user_id, conversation_id):
    """Get all messages in a conversation"""
    logger.info(f"Getting messages for conversation {conversation_id}")

    conn = None
    cursor = None

    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        cursor.execute(
            """
            SELECT id, conversation_id, sender, content, timestamp
            FROM messages
            WHERE conversation_id = %s
            ORDER BY timestamp ASC
            """,
            (conversation_id,),
        )

        messages = cursor.fetchall()
        cursor.close()
        release_db_connection(conn)

        results = []
        for msg in messages:
            results.append(
                {
                    "id": msg[0],
                    "conversation_id": msg[1],
                    "sender": msg[2],
                    "content": msg[3],
                    "timestamp": msg[4].isoformat(),
                }
            )

        logger.info(f"Found {len(results)} messages")
        return jsonify(results), 200

    except Exception as e:
        logger.error(f"Error getting messages: {e}")
        traceback.print_exc()

        if cursor:
            cursor.close()
        if conn:
            release_db_connection(conn)

        return jsonify({"message": "Lỗi khi lấy tin nhắn.", "error": str(e)}), 500


def update_conversation(user_id, conversation_id):
    """Update conversation title"""
    logger.info(f"Updating conversation {conversation_id} for user {user_id}")

    conn = None
    cursor = None

    try:
        data = request.get_json()
        new_title = data.get("title")

        if not new_title or not new_title.strip():
            return jsonify({"message": "Tiêu đề không được để trống"}), 400

        conn = get_db_connection()
        cursor = conn.cursor()

        # Verify user owns this conversation
        cursor.execute(
            """
            SELECT id FROM conversations
            WHERE id = %s AND user_id = %s
            """,
            (conversation_id, user_id),
        )

        if not cursor.fetchone():
            cursor.close()
            release_db_connection(conn)
            return jsonify({"message": "Không tìm thấy cuộc trò chuyện"}), 404

        # Update title
        cursor.execute(
            """
            UPDATE conversations
            SET title = %s, updated_at = CURRENT_TIMESTAMP
            WHERE id = %s AND user_id = %s
            RETURNING id, user_id, title, created_at, updated_at
            """,
            (new_title.strip(), conversation_id, user_id),
        )

        updated = cursor.fetchone()
        conn.commit()

        cursor.close()
        release_db_connection(conn)

        result = {
            "id": updated[0],
            "user_id": updated[1],
            "title": updated[2],
            "created_at": updated[3].isoformat(),
            "updated_at": updated[4].isoformat(),
        }

        logger.info(f"Conversation updated: {result['title']}")
        return jsonify(result), 200

    except Exception as e:
        logger.error(f"Error updating conversation: {e}")
        traceback.print_exc()

        if conn:
            conn.rollback()
        if cursor:
            cursor.close()
        if conn:
            release_db_connection(conn)

        return (
            jsonify({"message": "Lỗi khi cập nhật cuộc trò chuyện", "error": str(e)}),
            500,
        )


def delete_conversation(user_id, conversation_id):
    """Delete a conversation"""
    logger.info(f"Deleting conversation {conversation_id} for user {user_id}")

    conn = None
    cursor = None

    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        # Verify ownership and delete
        cursor.execute(
            """
            DELETE FROM conversations
            WHERE id = %s AND user_id = %s
            RETURNING id
            """,
            (conversation_id, user_id),
        )

        deleted = cursor.fetchone()

        if not deleted:
            cursor.close()
            release_db_connection(conn)
            return jsonify({"message": "Không tìm thấy cuộc trò chuyện"}), 404

        conn.commit()
        cursor.close()
        release_db_connection(conn)

        logger.info(f"Conversation {conversation_id} deleted")
        return jsonify({"message": "Đã xóa cuộc trò chuyện"}), 200

    except Exception as e:
        logger.error(f"Error deleting conversation: {e}")
        traceback.print_exc()

        if conn:
            conn.rollback()
        if cursor:
            cursor.close()
        if conn:
            release_db_connection(conn)

        return jsonify({"message": "Lỗi khi xóa cuộc trò chuyện", "error": str(e)}), 500
