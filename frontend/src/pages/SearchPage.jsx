/**
 * Search & Catalog Exploration Page
 */

import React, { useState, useEffect } from 'react';
import SearchBar from '../components/SearchBar';
import MovieGrid from '../components/MovieGrid';
import { api } from '../services/api';

export default function SearchPage({ onSelectMovie }) {
  const [query, setQuery] = useState('');
  const [selectedGenre, setSelectedGenre] = useState('');
  const [genres, setGenres] = useState([]);
  const [movies, setMovies] = useState([]);
  const [page, setPage] = useState(1);
  const [total, setTotal] = useState(0);
  const [loading, setLoading] = useState(false);
  const limit = 24;

  useEffect(() => {
    async function loadGenres() {
      try {
        const gList = await api.movies.genres();
        setGenres(gList || []);
      } catch (e) {
        console.error(e);
      }
    }
    loadGenres();
  }, []);

  const executeSearch = async (q, g, p = 1) => {
    setLoading(true);
    try {
      const res = await api.movies.list({
        q,
        genre: g,
        page: p,
        limit,
      });
      setMovies(res.movies || []);
      setTotal(res.total || 0);
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    executeSearch(query, selectedGenre, page);
  }, [query, selectedGenre, page]);

  const handleSearchSubmit = (newQuery) => {
    setQuery(newQuery);
    setPage(1);
  };

  const handleGenreChange = (newGenre) => {
    setSelectedGenre(newGenre);
    setPage(1);
  };

  return (
    <div className="container" style={{ paddingTop: 30, paddingBottom: 60 }}>
      <h1 className="font-display" style={{ fontSize: '2rem', fontWeight: 800, color: '#ffffff', marginBottom: 20 }}>
        Search Catalog & Discover
      </h1>

      <SearchBar
        onSearch={handleSearchSubmit}
        initialQuery={query}
        genres={genres}
        selectedGenre={selectedGenre}
        onSelectGenre={handleGenreChange}
      />

      <div style={{ marginBottom: 20, color: 'var(--text-muted)', fontSize: '0.9rem' }}>
        {loading ? (
          'Searching movie catalog...'
        ) : (
          <span>
            Found <strong style={{ color: '#ffffff' }}>{total}</strong> movies
            {query && <span> for "<strong style={{ color: 'var(--accent-cyan)' }}>{query}</strong>"</span>}
            {selectedGenre && <span> in <strong style={{ color: 'var(--accent-amber)' }}>{selectedGenre}</strong></span>}
          </span>
        )}
      </div>

      <MovieGrid
        movies={movies}
        loading={loading}
        page={page}
        total={total}
        limit={limit}
        onPageChange={setPage}
        onSelectMovie={onSelectMovie}
        showExplanation={false}
        emptyMessage={query ? `No movies found matching "${query}".` : 'No movies found.'}
      />
    </div>
  );
}
