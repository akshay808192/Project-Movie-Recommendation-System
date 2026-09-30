import React, { useState } from 'react';
import { Heart } from 'lucide-react';
import { api } from '../services/api';
import { useToast } from '../context/ToastContext';
import { useAuth } from '../context/AuthContext';

export default function LikeButton({ movieId, initialLiked = false, onToggle, size = 18 }) {
  const [isLiked, setIsLiked] = useState(initialLiked);
  const [isLoading, setIsLoading] = useState(false);
  const { showToast } = useToast();
  const { user, refreshSummary } = useAuth();

  const handleToggle = async (e) => {
    e.stopPropagation();
    if (isLoading) return;

    setIsLoading(true);
    const prevLiked = isLiked;
    setIsLiked(!prevLiked);

    try {
      const res = await api.interactions.toggleFavorite(movieId, user ? user.id : null);
      setIsLiked(res.is_liked);
      showToast(res.message, res.is_liked ? 'like' : 'info');
      if (refreshSummary) refreshSummary();
      if (onToggle) onToggle(res.is_liked);
    } catch (err) {
      setIsLiked(prevLiked);
      showToast(err.message || 'Failed to update favorite', 'error');
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <button
      onClick={handleToggle}
      disabled={isLoading}
      title={isLiked ? 'Remove from favorites' : 'Add to favorites'}
      className="like-btn"
      style={{
        display: 'inline-flex',
        alignItems: 'center',
        justifyContent: 'center',
        width: `${size + 16}px`,
        height: `${size + 16}px`,
        borderRadius: '50%',
        background: isLiked ? 'rgba(244, 63, 94, 0.25)' : 'rgba(15, 23, 42, 0.75)',
        backdropFilter: 'blur(8px)',
        WebkitBackdropFilter: 'blur(8px)',
        border: `1px solid ${isLiked ? 'rgba(244, 63, 94, 0.6)' : 'rgba(255, 255, 255, 0.15)'}`,
        cursor: 'pointer',
        transition: 'all 0.2s cubic-bezier(0.175, 0.885, 0.32, 1.275)',
        boxShadow: isLiked ? '0 0 15px rgba(244, 63, 94, 0.4)' : '0 4px 12px rgba(0,0,0,0.4)',
        transform: isLiked ? 'scale(1.05)' : 'scale(1)',
      }}
    >
      <Heart
        size={size}
        style={{
          color: isLiked ? '#f43f5e' : '#e2e8f0',
          fill: isLiked ? '#f43f5e' : 'none',
          transition: 'all 0.2s ease',
        }}
      />
    </button>
  );
}
