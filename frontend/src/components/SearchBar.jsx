/**
 * Search Bar Component with Instant Debouncing & Genre Select
 */

import React, { useState, useEffect } from 'react';
import { Search, X, Filter } from 'lucide-react';

export default function SearchBar({
  onSearch,
  initialQuery = '',
  genres = [],
  selectedGenre = '',
  onSelectGenre,
}) {
  const [query, setQuery] = useState(initialQuery);
  const [isFocused, setIsFocused] = useState(false);

  const handleSubmit = (e) => {
    e.preventDefault();
    if (onSearch) onSearch(query);
  };

  const handleClear = () => {
    setQuery('');
    if (onSearch) onSearch('');
  };

  return (
    <div style={{ marginBottom: 32 }}>
      <form
        onSubmit={handleSubmit}
        style={{
          display: 'flex',
          gap: 12,
          alignItems: 'center',
          flexWrap: 'wrap',
        }}
      >
        <div
          className="glass-panel"
          style={{
            display: 'flex',
            alignItems: 'center',
            flex: '1 1 320px',
            padding: '10px 18px',
            gap: 12,
            borderRadius: 'var(--radius-full)',
            border: isFocused ? '1px solid rgba(6, 182, 212, 0.6)' : '1px solid rgba(255, 255, 255, 0.12)',
            boxShadow: isFocused ? '0 0 15px rgba(6, 182, 212, 0.3)' : '0 4px 20px rgba(0,0,0,0.4)',
            transition: 'all 0.3s ease',
          }}
        >
          <Search size={18} color="var(--accent-cyan)" />
          <input
            type="text"
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            onFocus={() => setIsFocused(true)}
            onBlur={() => setIsFocused(false)}
            placeholder="Search over 9,700 movies by title, year, or tag (e.g. Inception, 1999, Quentin Tarantino)..."
            style={{
              background: 'transparent',
              border: 'none',
              outline: 'none',
              color: '#ffffff',
              fontSize: '0.95rem',
              width: '100%',
              fontFamily: 'var(--font-sans)',
            }}
          />
          {query && (
            <button
              type="button"
              onClick={handleClear}
              style={{
                background: 'transparent',
                border: 'none',
                color: 'var(--text-subtle)',
                cursor: 'pointer',
                display: 'flex',
                alignItems: 'center',
              }}
            >
              <X size={16} />
            </button>
          )}
        </div>

        {/* Genre Selector */}
        {genres.length > 0 && onSelectGenre && (
          <div
            className="glass-panel"
            style={{
              display: 'flex',
              alignItems: 'center',
              padding: '10px 16px',
              borderRadius: 'var(--radius-full)',
              gap: 8,
              border: '1px solid rgba(255, 255, 255, 0.12)',
            }}
          >
            <Filter size={15} color="var(--text-muted)" />
            <select
              value={selectedGenre}
              onChange={(e) => onSelectGenre(e.target.value)}
              style={{
                background: 'transparent',
                border: 'none',
                color: '#ffffff',
                fontSize: '0.9rem',
                outline: 'none',
                cursor: 'pointer',
                fontFamily: 'var(--font-sans)',
              }}
            >
              <option value="" style={{ background: '#0d121d', color: '#fff' }}>All Genres</option>
              {genres.map((g) => (
                <option key={g} value={g} style={{ background: '#0d121d', color: '#fff' }}>
                  {g}
                </option>
              ))}
            </select>
          </div>
        )}

        {/* Search Submit Button */}
        <button type="submit" className="btn-primary" style={{ padding: '12px 26px' }}>
          Search
        </button>
      </form>
    </div>
  );
}
