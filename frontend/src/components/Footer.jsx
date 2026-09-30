/**
 * Footer Component with System Architecture Details & Dataset Attribution
 */

import React from 'react';
import { Film, Cpu, Database, Award } from 'lucide-react';

export default function Footer() {
  return (
    <footer
      style={{
        marginTop: 80,
        borderTop: '1px solid rgba(255, 255, 255, 0.08)',
        backgroundColor: 'rgba(7, 9, 14, 0.95)',
        padding: '48px 0 36px 0',
      }}
    >
      <div className="container">
        <div
          style={{
            display: 'grid',
            gridTemplateColumns: 'repeat(auto-fit, minmax(260px, 1fr))',
            gap: 36,
            marginBottom: 36,
          }}
        >
          {/* Brand & Project Summary */}
          <div>
            <div style={{ display: 'flex', alignItems: 'center', gap: 10, marginBottom: 14 }}>
              <div
                style={{
                  width: 32,
                  height: 32,
                  borderRadius: 10,
                  background: 'linear-gradient(135deg, #06b6d4, #3b82f6)',
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'center',
                }}
              >
                <Film size={18} color="#ffffff" />
              </div>
              <span className="font-display" style={{ fontSize: '1.2rem', fontWeight: 800, color: '#ffffff' }}>
                CineMatch<span style={{ color: 'var(--accent-cyan)' }}>AI</span>
              </span>
            </div>
            <p style={{ color: 'var(--text-muted)', fontSize: '0.85rem', lineHeight: 1.6 }}>
              Production-ready Full Stack Movie Recommendation System implementing Item-Item Collaborative
              Filtering with Bayesian Popularity Cold-Start solving user onboarding challenges.
            </p>
          </div>

          {/* Machine Learning Pipeline */}
          <div>
            <div style={{ display: 'flex', alignItems: 'center', gap: 8, marginBottom: 12 }}>
              <Cpu size={18} color="var(--accent-cyan)" />
              <h4 style={{ fontSize: '0.95rem', fontWeight: 700, color: '#ffffff' }}>
                Machine Learning Algorithms
              </h4>
            </div>
            <ul style={{ listStyle: 'none', color: 'var(--text-muted)', fontSize: '0.82rem', lineHeight: 1.8 }}>
              <li>• <strong>Cold Start:</strong> IMDB Bayesian Weighted Rating (WR)</li>
              <li>• <strong>Personalization:</strong> Normalized Item-Item Cosine Similarity</li>
              <li>• <strong>Transition:</strong> Adaptive Hybrid Alpha Blending</li>
              <li>• <strong>Evaluation:</strong> Precision@K, Recall@K, NDCG@K, HitRate</li>
            </ul>
          </div>

          {/* Full-Stack Architecture */}
          <div>
            <div style={{ display: 'flex', alignItems: 'center', gap: 8, marginBottom: 12 }}>
              <Database size={18} color="var(--accent-amber)" />
              <h4 style={{ fontSize: '0.95rem', fontWeight: 700, color: '#ffffff' }}>
                Technology Stack
              </h4>
            </div>
            <ul style={{ listStyle: 'none', color: 'var(--text-muted)', fontSize: '0.82rem', lineHeight: 1.8 }}>
              <li>• <strong>Frontend:</strong> React 19, Vite, Lucide Icons, Modern CSS</li>
              <li>• <strong>Backend:</strong> Python, FastAPI, Pydantic, REST API</li>
              <li>• <strong>Machine Learning:</strong> Scikit-Learn, SciPy, Pandas, NumPy</li>
              <li>• <strong>Storage:</strong> SQLite DB + Serialized Pickle Artifacts</li>
            </ul>
          </div>
        </div>

        {/* Bottom Credits */}
        <div
          style={{
            borderTop: '1px solid rgba(255, 255, 255, 0.05)',
            paddingTop: 24,
            display: 'flex',
            justifyContent: 'space-between',
            alignItems: 'center',
            flexWrap: 'wrap',
            gap: 12,
            fontSize: '0.8rem',
            color: 'var(--text-subtle)',
          }}
        >
          <div>
            Dataset: MovieLens 100K provided by GroupLens Research (9,742 movies, 100,836 ratings).
          </div>
          <div>
            Movie Recommendation System © 2026. Production Full-Stack Academic Project.
          </div>
        </div>
      </div>
    </footer>
  );
}
