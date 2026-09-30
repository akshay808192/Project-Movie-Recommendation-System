/**
 * Dynamic Recommendation Section with Real-Time Strategy Banner & Explainability
 */

import React, { useState } from 'react';
import { Sparkles, Info, Filter, ArrowRight } from 'lucide-react';
import MovieGrid from './MovieGrid';

export default function RecommendationSection({
  recommendations = [],
  strategy = 'COLD_START_POPULARITY',
  strategyBadge = 'Cold-Start Popularity',
  strategyDescription = '',
  loading = false,
  onSelectMovie,
  genres = [],
  selectedGenre = '',
  onSelectGenre,
  onViewAll = null,
}) {
  const getBannerGradient = () => {
    if (strategy === 'COLLABORATIVE_FILTERING') {
      return 'linear-gradient(135deg, rgba(16, 185, 129, 0.15) 0%, rgba(6, 182, 212, 0.1) 100%)';
    }
    if (strategy === 'HYBRID_TRANSITION') {
      return 'linear-gradient(135deg, rgba(245, 158, 11, 0.15) 0%, rgba(139, 92, 246, 0.1) 100%)';
    }
    return 'linear-gradient(135deg, rgba(6, 182, 212, 0.15) 0%, rgba(59, 130, 246, 0.1) 100%)';
  };

  const getBorderColor = () => {
    if (strategy === 'COLLABORATIVE_FILTERING') return 'rgba(16, 185, 129, 0.3)';
    if (strategy === 'HYBRID_TRANSITION') return 'rgba(245, 158, 11, 0.3)';
    return 'rgba(6, 182, 212, 0.3)';
  };

  return (
    <section style={{ marginBottom: 54 }}>
      {/* Strategy Explanatory Glass Banner */}
      <div
        className="glass-panel"
        style={{
          background: getBannerGradient(),
          borderColor: getBorderColor(),
          padding: '24px 28px',
          marginBottom: 28,
          borderRadius: 'var(--radius-md)',
          boxShadow: '0 10px 30px -10px rgba(0,0,0,0.5)',
        }}
      >
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', flexWrap: 'wrap', gap: 16 }}>
          <div style={{ maxWidth: 850 }}>
            <div style={{ display: 'flex', alignItems: 'center', gap: 10, marginBottom: 8 }}>
              <span style={{ fontSize: '1.4rem' }}>
                {strategy === 'COLLABORATIVE_FILTERING' ? '🎯' : strategy === 'HYBRID_TRANSITION' ? '⚡' : '❄️'}
              </span>
              <h2 className="font-display" style={{ fontSize: '1.35rem', fontWeight: 800, color: '#ffffff' }}>
                {strategyBadge}
              </h2>
            </div>
            <p style={{ color: '#cbd5e1', fontSize: '0.92rem', lineHeight: 1.5 }}>
              {strategyDescription}
            </p>
          </div>

          {onViewAll && (
            <button
              onClick={onViewAll}
              className="btn-secondary"
              style={{ padding: '8px 16px', fontSize: '0.85rem' }}
            >
              Dedicated Dashboard <ArrowRight size={15} />
            </button>
          )}
        </div>
      </div>

      {/* Genre Filter Pills */}
      {genres.length > 0 && onSelectGenre && (
        <div
          style={{
            display: 'flex',
            alignItems: 'center',
            gap: 8,
            overflowX: 'auto',
            paddingBottom: 12,
            marginBottom: 20,
          }}
        >
          <button
            onClick={() => onSelectGenre('')}
            style={{
              padding: '6px 16px',
              borderRadius: 99,
              fontSize: '0.82rem',
              fontWeight: 700,
              cursor: 'pointer',
              whiteSpace: 'nowrap',
              border: selectedGenre === '' ? '1px solid var(--accent-cyan)' : '1px solid rgba(255, 255, 255, 0.1)',
              background: selectedGenre === '' ? 'var(--accent-cyan)' : 'rgba(255, 255, 255, 0.04)',
              color: selectedGenre === '' ? '#07090e' : 'var(--text-muted)',
              transition: 'all 0.2s',
            }}
          >
            All Genres
          </button>

          {genres.slice(0, 10).map((g) => (
            <button
              key={g}
              onClick={() => onSelectGenre(g)}
              style={{
                padding: '6px 14px',
                borderRadius: 99,
                fontSize: '0.82rem',
                fontWeight: 600,
                cursor: 'pointer',
                whiteSpace: 'nowrap',
                border: selectedGenre === g ? '1px solid var(--accent-cyan)' : '1px solid rgba(255, 255, 255, 0.1)',
                background: selectedGenre === g ? 'rgba(6, 182, 212, 0.15)' : 'rgba(255, 255, 255, 0.04)',
                color: selectedGenre === g ? 'var(--accent-cyan)' : 'var(--text-muted)',
                transition: 'all 0.2s',
              }}
            >
              {g}
            </button>
          ))}
        </div>
      )}

      {/* Recommended Movies Grid */}
      <MovieGrid
        movies={recommendations}
        loading={loading}
        onSelectMovie={onSelectMovie}
        showExplanation={true}
        emptyMessage="No recommendations generated yet for this genre."
      />
    </section>
  );
}
