from flask import Blueprint
from controllers.chat_controller import (
    create_conversation,
    get_conversations,
    send_message,
    get_messages,
    update_conversation,
    delete_conversation 
)

from middleware.auth_middleware import token_required

chat_bp = Blueprint('chat', __name__)

# All routes here require authentication
chat_bp.route('/conversations', methods=['POST'])(token_required(create_conversation))
chat_bp.route('/conversations', methods=['GET'])(token_required(get_conversations))
chat_bp.route('/messages', methods=['POST'])(token_required(send_message))
# chat_bp.route('/messages', methods=['GET'])(token_required(get_messages))
chat_bp.route('/messages/<int:conversation_id>', methods=['GET'])(token_required(get_messages))

chat_bp.route('/conversations/<int:conversation_id>', methods=['PUT'])(token_required(update_conversation))
chat_bp.route('/conversations/<int:conversation_id>', methods=['DELETE'])(token_required(delete_conversation))