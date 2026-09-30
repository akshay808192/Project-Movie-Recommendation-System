/**
 * Dedicated Watch History Page
 */

import React, { useState, useEffect } from 'react';
import { History, Film } from 'lucide-react';
import { api } from '../services/api';
import { useAuth } from '../context/AuthContext';

export default function WatchHistoryPage({ onSelectMovie }) {
  const { isAuthenticated } = useAuth();
  const [historyList, setHistoryList] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    async function loadHistory() {
      if (!isAuthenticated) {
        setLoading(false);
        return;
      }
      setLoading(true);
      try {
        const data = await api.interactions.getHistory();
        setHistoryList(data || []);
      } catch (err) {
        console.error(err);
      } finally {
        setLoading(false);
      }
    }
    loadHistory();
  }, [isAuthenticated]);

  return (
    <div className="container" style={{ paddingTop: 30, paddingBottom: 60 }}>
      <div style={{ display: 'flex', alignItems: 'center', gap: 10, marginBottom: 8 }}>
        <History size={24} color="var(--accent-cyan)" />
        <h1 className="font-display" style={{ fontSize: '2rem', fontWeight: 800, color: '#ffffff' }}>
          Your Watch History
        </h1>
      </div>
      <p style={{ color: 'var(--text-muted)', fontSize: '0.95rem', marginBottom: 32 }}>
        Chronological record of movies you have viewed or evaluated.
      </p>

      {loading ? (
        <p style={{ color: 'var(--text-subtle)' }}>Loading watch history...</p>
      ) : !isAuthenticated ? (
        <div className="glass-panel" style={{ padding: '50px 20px', textAlign: 'center' }}>
          <p style={{ color: 'var(--text-muted)' }}>
            Please sign in to track and view your personalized watch history.
          </p>
        </div>
      ) : historyList.length === 0 ? (
        <div className="glass-panel" style={{ padding: '60px 20px', textAlign: 'center' }}>
          <Film size={44} color="var(--text-subtle)" style={{ marginBottom: 16 }} />
          <h3 style={{ fontSize: '1.2rem', color: 'var(--text-muted)', marginBottom: 8 }}>
            No watch history recorded yet.
          </h3>
          <p style={{ color: 'var(--text-subtle)', fontSize: '0.9rem' }}>
            Click on any movie to view its details, or rate movies to build your watch log.
          </p>
        </div>
      ) : (
        <div style={{ display: 'flex', flexDirection: 'column', gap: 12 }}>
          {historyList.map((item, idx) => (
            <div
              key={idx}
              onClick={() => onSelectMovie({ movieId: item.movie_id })}
              className="glass-panel glass-panel-hover"
              style={{
                padding: '16px 24px',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'space-between',
                cursor: 'pointer',
              }}
            >
              <div style={{ display: 'flex', alignItems: 'center', gap: 18 }}>
                <div
                  style={{
                    width: 48,
                    height: 64,
                    borderRadius: 6,
                    overflow: 'hidden',
                    background: '#07090e',
                    flexShrink: 0,
                  }}
                >
                  {item.poster_url ? (
                    <img src={item.poster_url} alt={item.title} style={{ width: '100%', height: '100%', objectFit: 'cover' }} />
                  ) : (
                    <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'center', height: '100%' }}>
                      <Film size={18} color="var(--accent-cyan)" />
                    </div>
                  )}
                </div>

                <div>
                  <h4 style={{ fontSize: '1.05rem', color: '#fff', fontWeight: 700, marginBottom: 4 }}>
                    {item.title}
                  </h4>
                  <div style={{ fontSize: '0.82rem', color: 'var(--text-muted)' }}>
                    {item.year && <span>{item.year} • </span>}
                    <span>{item.genres_list?.join(', ')}</span>
                  </div>
                </div>
              </div>

              <div style={{ textAlign: 'right' }}>
                <span style={{ fontSize: '0.82rem', color: 'var(--text-subtle)' }}>
                  {item.watched_at}
                </span>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
