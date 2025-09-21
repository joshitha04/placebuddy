import json
import logging
from datetime import datetime
from flask import request
from flask_socketio import emit, disconnect
from database.models import CompanyModel
from services.llm_service import LLMService
from services.company_service import CompanyService

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def register_websocket_events(socketio):
    """Register all WebSocket events for native WebSocket and SocketIO compatibility"""
    
    @socketio.on('connect')
    def handle_connect():
        logger.info(f"Client connected: {request.sid}")
        # Send connection confirmation
        emit('message', json.dumps({
            'type': 'status',
            'message': 'Connected to server successfully'
        }))

    @socketio.on('disconnect')
    def handle_disconnect():
        logger.info(f"Client disconnected: {request.sid}")

    @socketio.on('message')
    def handle_message(data):
        """Handle native WebSocket messages"""
        try:
            # Parse JSON message
            if isinstance(data, str):
                message = json.loads(data)
            else:
                message = data
                
            message_type = message.get('type')
            message_data = message.get('data', {})
            
            logger.info(f"Received message type: {message_type}")
            
            if message_type == 'process_text':
                handle_process_text(message_data)
            else:
                logger.warning(f"Unknown message type: {message_type}")
                
        except json.JSONDecodeError as e:
            logger.error(f"Invalid JSON received: {e}")
            emit('message', json.dumps({
                'type': 'processing_error',
                'error': 'Invalid message format'
            }))
        except Exception as e:
            logger.error(f"Error handling message: {e}")
            emit('message', json.dumps({
                'type': 'processing_error',
                'error': 'Server error occurred'
            }))

    def handle_process_text(data):
        """Process text input using LLM and save to database"""
        try:
            text = data.get('text', '').strip()
            user_id = data.get('user_id')
            timestamp = data.get('timestamp')
            
            if not text:
                emit('message', json.dumps({
                    'type': 'processing_error',
                    'error': 'No text provided'
                }))
                return
                
            if not user_id:
                emit('message', json.dumps({
                    'type': 'processing_error',
                    'error': 'User ID required'
                }))
                return
            
            # Send processing status
            emit('message', json.dumps({
                'type': 'status',
                'message': 'Extracting company information...'
            }))
            
            # Extract company information using LLM service
            llm_service = LLMService()
            company_data = llm_service.extract_company_info(text)
            
            if not company_data:
                emit('message', json.dumps({
                    'type': 'processing_error',
                    'error': 'Could not extract company information from text'
                }))
                return
            
            # Process company data using company service
            company_service = CompanyService()
            result = company_service.process_company(company_data, user_id)
            
            # Send success response
            emit('message', json.dumps({
                'type': 'processing_complete',
                'success': True,
                'result': {
                    'company_id': result['company_id'],
                    'company_name': company_data.get('name'),
                    'tier': company_data.get('tier'),
                    'is_duplicate': result.get('is_duplicate', False),
                    'created_at': datetime.now().isoformat()
                },
                'originalText': text
            }))
            
            logger.info(f"Successfully processed company: {company_data.get('name')}")
            
        except Exception as e:
            logger.error(f"Error processing text: {str(e)}")
            emit('message', json.dumps({
                'type': 'processing_error',
                'error': f'Processing failed: {str(e)}'
            }))

