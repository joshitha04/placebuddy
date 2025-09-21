import React, { useState, useEffect, useRef } from 'react';
import { LogOut, Send, Loader2, CheckCircle, AlertCircle } from 'lucide-react';
import io from 'socket.io-client';

const Dashboard = ({ user, setUser }) => {
  const [textInput, setTextInput] = useState('');
  const [isProcessing, setIsProcessing] = useState(false);
  const [connectionStatus, setConnectionStatus] = useState('disconnected');
  const [statusMessage, setStatusMessage] = useState('');
  const [submissions, setSubmissions] = useState([]);
  const socketRef = useRef(null);

  // Initialize Socket.IO connection
  useEffect(() => {
    // Connect to the Socket.IO server
    const socket = io('http://localhost:5000');
    socketRef.current = socket;

    socket.on('connect', () => {
      setConnectionStatus('connected');
      setStatusMessage('Connected to server successfully');
    });

    socket.on('disconnect', () => {
      setConnectionStatus('disconnected');
      setStatusMessage('Disconnected from server');
      setIsProcessing(false);
    });

    socket.on('connect_error', (error) => {
      console.error('Connection error:', error);
      setConnectionStatus('disconnected');
      setStatusMessage('Connection failed. Server might be down.');
      setIsProcessing(false);
    });

    socket.on('message', (data) => {
      const message = JSON.parse(data);
      console.log('Received message:', message);

      if (message.type === 'status') {
        setStatusMessage(message.message);
      } else if (message.type === 'processing_complete') {
        setIsProcessing(false);
        setStatusMessage('Text processed successfully!');
        setSubmissions(prev => [
          {
            id: Date.now(),
            text: message.originalText,
            result: {
              company_name: message.result.company_name,
              tier: message.result.tier,
              is_duplicate: message.result.is_duplicate,
            },
            timestamp: new Date(message.result.created_at),
            status: 'success'
          },
          ...prev
        ]);
        setTextInput(''); // Clear input on success
      } else if (message.type === 'processing_error') {
        setIsProcessing(false);
        setStatusMessage(`Error: ${message.error}`);
      }
    });

    // Cleanup on unmount
    return () => {
      if (socketRef.current) {
        socketRef.current.disconnect();
      }
    };
  }, [user]);

  const handleLogout = () => {
    if (socketRef.current) {
      socketRef.current.disconnect();
    }
    setUser(null);
  };

  const handleSubmit = () => {
    if (!textInput.trim()) {
      setStatusMessage('Please enter some text to process');
      return;
    }

    if (connectionStatus !== 'connected') {
      setStatusMessage('Not connected to server. Please wait...');
      return;
    }

    if (isProcessing) {
      return;
    }

    setIsProcessing(true);
    setStatusMessage('Processing your text...');

    socketRef.current.emit('message', JSON.stringify({
      type: 'process_text',
      data: {
        text: textInput,
        user_id: user?.id || user?.username,
        timestamp: new Date().toISOString()
      }
    }));
  };

  const getStatusIcon = () => {
    switch (connectionStatus) {
      case 'connected':
        return <CheckCircle className="w-4 h-4 text-green-500" />;
      case 'disconnected':
        return <AlertCircle className="w-4 h-4 text-red-500" />;
      default:
        return <Loader2 className="w-4 h-4 text-yellow-500 animate-spin" />;
    }
  };

  const getStatusColor = () => {
    switch (connectionStatus) {
      case 'connected':
        return 'text-green-600 bg-green-50';
      case 'disconnected':
        return 'text-red-600 bg-red-50';
      default:
        return 'text-yellow-600 bg-yellow-50';
    }
  };

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <div className="bg-white shadow-sm border-b">
        <div className="max-w-7xl mx-auto px-4 py-4 flex justify-between items-center">
          <h1 className="text-xl font-bold text-gray-900">PlaceBuddy</h1>
          <div className="flex items-center space-x-4">
            <div className="flex items-center space-x-2">
              {getStatusIcon()}
              <span className={`px-2 py-1 rounded-full text-xs font-medium ${getStatusColor()}`}>
                {connectionStatus}
              </span>
            </div>
            <span className="text-gray-600">Welcome, {user?.username}!</span>
            <button
              onClick={handleLogout}
              className="flex items-center text-gray-500 hover:text-gray-700 transition-colors"
            >
              <LogOut className="w-4 h-4 mr-1" />
              Logout
            </button>
          </div>
        </div>
      </div>

      <div className="max-w-7xl mx-auto px-4 py-8 space-y-6">
        {/* Status Message */}
        {statusMessage && (
          <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
            <p className="text-blue-800 text-sm">{statusMessage}</p>
          </div>
        )}

        {/* Text Input Section */}
        <div className="bg-white rounded-lg shadow p-6">
          <h2 className="text-lg font-semibold mb-4">Add Company Information</h2>
          <div className="space-y-4">
            <div>
              <label htmlFor="textInput" className="block text-sm font-medium text-gray-700 mb-2">
                Enter company information or job posting text:
              </label>
              <textarea
                id="textInput"
                value={textInput}
                onChange={(e) => setTextInput(e.target.value)}
                placeholder="Paste company information, job posting, or any text containing company details here..."
                rows={6}
                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500 resize-vertical"
                disabled={isProcessing}
              />
            </div>
            
            <div className="flex items-center justify-between">
              <div className="text-sm text-gray-500">
                {textInput.length} characters
              </div>
              <button
                onClick={handleSubmit}
                disabled={isProcessing || connectionStatus !== 'connected' || !textInput.trim()}
                className="inline-flex items-center px-4 py-2 bg-blue-600 text-white font-medium rounded-md hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
              >
                {isProcessing ? (
                  <>
                    <Loader2 className="w-4 h-4 mr-2 animate-spin" />
                    Processing...
                  </>
                ) : (
                  <>
                    <Send className="w-4 h-4 mr-2" />
                    Process Text
                  </>
                )}
              </button>
            </div>
          </div>
        </div>

        {/* Recent Submissions */}
        {submissions.length > 0 && (
          <div className="bg-white rounded-lg shadow p-6">
            <h3 className="text-lg font-semibold mb-4">Recent Submissions</h3>
            <div className="space-y-3">
              {submissions.slice(0, 5).map((submission) => (
                <div key={submission.id} className="border rounded-lg p-3">
                  <div className="flex items-center justify-between mb-2">
                    <span className={`inline-flex items-center px-2 py-1 rounded-full text-xs font-medium ${
                      submission.status === 'success' 
                        ? 'bg-green-100 text-green-800' 
                        : 'bg-red-100 text-red-800'
                    }`}>
                      {submission.status === 'success' ? (
                        <CheckCircle className="w-3 h-3 mr-1" />
                      ) : (
                        <AlertCircle className="w-3 h-3 mr-1" />
                      )}
                      {submission.status}
                    </span>
                    <span className="text-xs text-gray-500">
                      {submission.timestamp.toLocaleString()}
                    </span>
                  </div>
                  <p className="text-sm text-gray-600 line-clamp-2">
                    {submission.text.substring(0, 100)}...
                  </p>
                  {submission.result && (
                    <div className="mt-2 text-xs text-green-600">
                      Company processed: {submission.result.company_name || 'Unknown'}
                    </div>
                  )}
                </div>
              ))}
            </div>
          </div>
        )}
      </div>
    </div>
  );
};

export default Dashboard;