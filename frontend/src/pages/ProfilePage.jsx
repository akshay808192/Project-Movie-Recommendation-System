import React from 'react';
import UserProfile from '../components/UserProfile';
import LoginForm from '../components/LoginForm';
import { useAuth } from '../context/AuthContext';

export default function ProfilePage({ onSelectMovie, onNavigateTab }) {
  const { isAuthenticated } = useAuth();

  if (!isAuthenticated) {
    return (
      <div className="container" style={{ padding: '60px 0 100px 0' }}>
        <div style={{ textAlign: 'center', marginBottom: '32px' }}>
          <h2 style={{ fontSize: '1.8rem', fontWeight: 800, color: '#f8fafc', marginBottom: '8px' }}>
            Account Profile
          </h2>
          <p style={{ color: '#94a3b8' }}>Please sign in to view your profile and recommendation stats</p>
        </div>
        <LoginForm
          onSuccess={() => onNavigateTab('profile')}
          onSwitchToRegister={() => onNavigateTab('register')}
        />
      </div>
    );
  }

  return (
    <div style={{ paddingTop: '20px' }}>
      <UserProfile onSelectMovie={onSelectMovie} />
    </div>
  );
}
