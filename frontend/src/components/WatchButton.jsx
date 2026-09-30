import React, { useState } from 'react';
import { Film, Check } from 'lucide-react';
import { api } from '../services/api';
import { useToast } from '../context/ToastContext';
import { useAuth } from '../context/AuthContext';

export default function WatchButton({ movieId, initialWatched = false, onWatched, size = 18 }) {
  const [watched, setWatched] = useState(initialWatched);
  const [isLoading, setIsLoading] = useState(false);
  const { showToast } = useToast();
  const { user, refreshSummary } = useAuth();

  const handleWatch = async (e) => {
    e.stopPropagation();
    if (isLoading) return;

    setIsLoading(true);
    try {
      const res = await api.interactions.recordWatch(movieId, user ? user.id : null);
      setWatched(true);
      showToast(res.message || 'Marked as watched', 'watch');
      if (refreshSummary) refreshSummary();
      if (onWatched) onWatched();
    } catch (err) {
      showToast(err.message || 'Failed to record watch history', 'error');
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <button
      onClick={handleWatch}
      disabled={isLoading}
      title={watched ? 'Watched' : 'Mark as watched'}
      className="watch-btn"
      style={{
        display: 'inline-flex',
        alignItems: 'center',
        justifyContent: 'center',
        width: `${size + 16}px`,
        height: `${size + 16}px`,
        borderRadius: '50%',
        background: watched ? 'rgba(6, 182, 212, 0.25)' : 'rgba(15, 23, 42, 0.75)',
        backdropFilter: 'blur(8px)',
        WebkitBackdropFilter: 'blur(8px)',
        border: `1px solid ${watched ? 'rgba(6, 182, 212, 0.6)' : 'rgba(255, 255, 255, 0.15)'}`,
        cursor: 'pointer',
        transition: 'all 0.2s cubic-bezier(0.175, 0.885, 0.32, 1.275)',
        boxShadow: watched ? '0 0 15px rgba(6, 182, 212, 0.4)' : '0 4px 12px rgba(0,0,0,0.4)',
      }}
    >
      {watched ? (
        <Check size={size} style={{ color: '#06b6d4' }} />
      ) : (
        <Film size={size} style={{ color: '#e2e8f0' }} />
      )}
    </button>
  );
}
