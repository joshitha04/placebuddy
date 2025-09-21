from flask import Flask, request, jsonify, render_template_string
from flask_socketio import SocketIO
from flask_cors import CORS
import logging
from datetime import datetime

# Import your existing modules
from routes.auth import auth_bp
from database.connection import init_db
from websocket.events import register_websocket_events  # Fixed import path

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Initialize Flask app
app = Flask(__name__)
app.config['SECRET_KEY'] = 'your-secret-key-here'  # Change this in production

# Enable CORS
CORS(app, resources={
    r"/api/*": {"origins": "*"},
    r"/socket.io/*": {"origins": "*"}
})

# Initialize SocketIO
socketio = SocketIO(
    app, 
    cors_allowed_origins="*", 
    logger=True, 
    engineio_logger=False  # Set to True for more detailed logs
)

# HTML template for the root route
HTML_TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
    <title>PlaceBuddy Backend Server</title>
    <style>
        body { font-family: Arial, sans-serif; margin: 40px; }
        .status { padding: 10px; margin: 10px 0; border-radius: 5px; }
        .success { background-color: #d4edda; color: #155724; }
        .info { background-color: #d1ecf1; color: #0c5460; }
        ul { margin: 10px 0; }
        li { margin: 5px 0; }
        button { padding: 10px 20px; margin: 5px; cursor: pointer; }
        #log { border: 1px solid #ccc; padding: 10px; height: 200px; overflow-y: scroll; font-family: monospace; font-size: 12px; }
    </style>
</head>
<body>
    <h1>🚀 PlaceBuddy Backend Server</h1>
    
    <div class="status success">
        <strong>✅ Server Status:</strong> Running Successfully
    </div>
    
    <div class="status info">
        <strong>🕐 Server Time:</strong> {{ current_time }}
    </div>
    
    <!-- Quick WebSocket Test -->
    <h2>🧪 Quick WebSocket Test</h2>
    <button onclick="testConnection()">Test Connection</button>
    <button onclick="sendTestMessage()">Send Test Message</button>
    <button onclick="clearLog()">Clear Log</button>
    
    <div id="log" style="margin: 10px 0;"></div>
    
    <h2>📡 Available Endpoints</h2>
    <ul>
        <li><strong>GET /</strong> - This status page</li>
        <li><strong>GET /health</strong> - Health check endpoint</li>
        <li><strong>POST /api/auth/register</strong> - User registration</li>
        <li><strong>POST /api/auth/login</strong> - User login</li>
    </ul>
    
    <h2>🔌 WebSocket Connection</h2>
    <p><strong>WebSocket URL:</strong> ws://localhost:5000/socket.io/</p>
    <p>Use Socket.IO client to connect for real-time company processing</p>
    
    <script src="https://cdnjs.cloudflare.com/ajax/libs/socket.io/4.7.2/socket.io.js"></script>
    <script>
        let socket = null;
        
        function log(message) {
            const logDiv = document.getElementById('log');
            const timestamp = new Date().toLocaleTimeString();
            logDiv.innerHTML += `[${timestamp}] ${message}<br>`;
            logDiv.scrollTop = logDiv.scrollHeight;
        }
        
        function testConnection() {
            if (socket) {
                socket.disconnect();
            }
            
            log('🔄 Connecting to WebSocket...');
            socket = io('http://localhost:5000');
            
            socket.on('connect', () => {
                log('✅ Connected successfully!');
            });
            
            socket.on('disconnect', () => {
                log('❌ Disconnected');
            });
            
            socket.on('message', (data) => {
                log(`📨 Received: ${data}`);
            });
            
            socket.on('connect_error', (error) => {
                log(`❌ Connection error: ${error}`);
            });
        }
        
        function sendTestMessage() {
            if (!socket || !socket.connected) {
                log('❌ Not connected. Please test connection first.');
                return;
            }
            
            const testMessage = {
                type: 'process_text',
                data: {
                    text: 'Google is hiring software engineers in San Francisco',
                    user_id: 'test_user',
                    timestamp: new Date().toISOString()
                }
            };
            
            log('📤 Sending test message...');
            socket.emit('message', JSON.stringify(testMessage));
        }
        
        function clearLog() {
            document.getElementById('log').innerHTML = '';
        }
    </script>
</body>
</html>
"""

# Register blueprints
app.register_blueprint(auth_bp, url_prefix='/api/auth')

# Register WebSocket events
register_websocket_events(socketio)

@app.route('/')
def index():
    """Main route - server status page"""
    return render_template_string(
        HTML_TEMPLATE,
        current_time=datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    )

@app.route('/health')
def health_check():
    """Health check endpoint"""
    try:
        # Test database connection
        from database.connection import get_db_connection
        conn = get_db_connection()
        conn.close()
        db_status = "connected"
    except Exception as e:
        logger.error(f"Database connection failed: {e}")
        db_status = "disconnected"
    
    return jsonify({
        'status': 'healthy',
        'timestamp': datetime.now().isoformat(),
        'database': db_status,
        'websocket': 'enabled',
        'version': '1.0.0'
    })

# Error handlers
@app.errorhandler(404)
def not_found_error(error):
    return jsonify({
        'error': 'Not found',
        'message': 'The requested resource was not found',
        'available_endpoints': [
            '/',
            '/health',
            '/api/auth/login',
            '/api/auth/register'
        ]
    }), 404

@app.errorhandler(500)
def internal_error(error):
    return jsonify({
        'error': 'Internal server error',
        'message': 'An internal server error occurred'
    }), 500

if __name__ == '__main__':
    try:
        # Test database connection
        init_db()
        logger.info("✅ Database connection verified")
        
        logger.info("🚀 Starting PlaceBuddy server...")
        logger.info("📡 Server will be available at: http://localhost:5000")
        logger.info("🔌 WebSocket endpoint: ws://localhost:5000/socket.io/")
        
        # Run the application with SocketIO
        socketio.run(
            app, 
            host='0.0.0.0', 
            port=5000, 
            debug=True,
            allow_unsafe_werkzeug=True  # Only for development
        )
        
    except Exception as e:
        logger.error(f"❌ Failed to start server: {e}")
        exit(1)