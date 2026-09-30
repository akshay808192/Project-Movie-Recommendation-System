/**
 * Loading Skeleton Components for Grids, Cards, and Hero
 */

import React from 'react';

export function MovieCardSkeleton() {
  return (
    <div className="glass-panel" style={{ overflow: 'hidden', padding: 12 }}>
      <div className="skeleton" style={{ width: '100%', aspectRatio: '2/3', borderRadius: '10px' }} />
      <div style={{ marginTop: 12 }}>
        <div className="skeleton" style={{ height: 18, width: '85%', marginBottom: 8 }} />
        <div className="skeleton" style={{ height: 14, width: '50%', marginBottom: 12 }} />
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
          <div className="skeleton" style={{ height: 16, width: 45 }} />
          <div className="skeleton" style={{ height: 20, width: 65, borderRadius: 99 }} />
        </div>
      </div>
    </div>
  );
}

export function MovieGridSkeleton({ count = 10 }) {
  return (
    <div className="movie-grid">
      {Array.from({ length: count }).map((_, i) => (
        <MovieCardSkeleton key={i} />
      ))}
    </div>
  );
}

export function HeroSkeleton() {
  return (
    <div
      className="glass-panel"
      style={{
        height: '420px',
        width: '100%',
        marginBottom: 40,
        padding: 40,
        display: 'flex',
        flexDirection: 'column',
        justifyContent: 'flex-end',
      }}
    >
      <div className="skeleton" style={{ height: 32, width: '40%', marginBottom: 16 }} />
      <div className="skeleton" style={{ height: 18, width: '65%', marginBottom: 12 }} />
      <div className="skeleton" style={{ height: 18, width: '50%', marginBottom: 24 }} />
      <div style={{ display: 'flex', gap: 16 }}>
        <div className="skeleton" style={{ height: 42, width: 140, borderRadius: 99 }} />
        <div className="skeleton" style={{ height: 42, width: 140, borderRadius: 99 }} />
      </div>
    </div>
  );
}
