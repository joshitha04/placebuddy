import React, { useState } from 'react';
import LoginPage from './components/login/LoginPage';
import Dashboard from './components/dashboard/Dashboard';


function App() {
  const [user, setUser] = useState(null);
  const [showRegister, setShowRegister] = useState(false);

  if (user) {
    return <Dashboard user={user} setUser={setUser} />;
  }

  return (
    <LoginPage 
      setUser={setUser} 
      showRegister={showRegister} 
      setShowRegister={setShowRegister} 
    />
  );
}

export default App;