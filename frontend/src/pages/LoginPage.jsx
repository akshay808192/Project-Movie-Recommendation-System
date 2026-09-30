import React from 'react';
import LoginForm from '../components/LoginForm';

export default function LoginPage({ onNavigateTab }) {
  return (
    <div className="container" style={{ padding: '60px 0 100px 0' }}>
      <LoginForm
        onSuccess={() => onNavigateTab('home')}
        onSwitchToRegister={() => onNavigateTab('register')}
      />
    </div>
  );
}
