import React from 'react';
import RegisterForm from '../components/RegisterForm';

export default function RegisterPage({ onNavigateTab }) {
  return (
    <div className="container" style={{ padding: '60px 0 100px 0' }}>
      <RegisterForm
        onSuccess={() => onNavigateTab('onboarding')}
        onSwitchToLogin={() => onNavigateTab('login')}
      />
    </div>
  );
}
