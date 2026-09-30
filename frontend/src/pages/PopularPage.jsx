/**
 * Dedicated Popular Movies Page with Pagination & Genre Filters
 */

import React, { useState, useEffect } from 'react';
import PopularMovies from '../components/PopularMovies';
import { api } from '../services/api';

export default function PopularPage({ onSelectMovie }) {
  const [movies, setMovies] = useState([]);
  const [genres, setGenres] = useState([]);
  const [selectedGenre, setSelectedGenre] = useState('');
  const [page, setPage] = useState(1);
  const [total, setTotal] = useState(0);
  const [loading, setLoading] = useState(true);
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

  useEffect(() => {
    async function fetchPopular() {
      setLoading(true);
      try {
        const res = await api.movies.popular({
          genre: selectedGenre,
          page,
          limit,
        });
        setMovies(res.movies || []);
        setTotal(res.total || 0);
      } catch (err) {
        console.error(err);
      } finally {
        setLoading(false);
      }
    }
    fetchPopular();
  }, [selectedGenre, page]);

  const handleGenreChange = (g) => {
    setSelectedGenre(g);
    setPage(1);
  };

  return (
    <div className="container" style={{ paddingTop: 30, paddingBottom: 60 }}>
      <PopularMovies
        movies={movies}
        loading={loading}
        page={page}
        total={total}
        limit={limit}
        onPageChange={setPage}
        onSelectMovie={onSelectMovie}
        genres={genres}
        selectedGenre={selectedGenre}
        onSelectGenre={handleGenreChange}
      />
    </div>
  );
}
