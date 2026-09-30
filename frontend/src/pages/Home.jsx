import React, { useState, useEffect } from 'react';
import HeroBanner from '../components/HeroBanner';
import MovieCarousel from '../components/MovieCarousel';
import PopularSection from '../components/PopularSection';
import { HeroSkeleton } from '../components/LoadingSkeleton';
import { useAuth } from '../context/AuthContext';
import { api } from '../services/api';

export default function Home({ onSelectMovie, onNavigateTab }) {
  const { summary } = useAuth();
  const [recommendations, setRecommendations] = useState([]);
  const [loadingRecs, setLoadingRecs] = useState(true);
  const [actionMovies, setActionMovies] = useState([]);
  const [comedyMovies, setComedyMovies] = useState([]);
  
  const isReturningUser = summary && summary.total_ratings > 0;
  
  // Load main recommendations
  useEffect(() => {
    let isMounted = true;
    async function fetchRecs() {
      setLoadingRecs(true);
      try {
        const res = await api.recommendations.getMine({ limit: 16 });
        if (isMounted) {
          setRecommendations(res.recommendations || []);
        }
      } catch (err) {
        console.error('Failed to load recommendations:', err);
      } finally {
        if (isMounted) setLoadingRecs(false);
      }
    }
    fetchRecs();
    return () => {
      isMounted = false;
    };
  }, [summary?.total_ratings]);

  // Load genre specific movies
  useEffect(() => {
    let isMounted = true;
    async function fetchGenres() {
      try {
        const [actionRes, comedyRes] = await Promise.all([
          api.movies.popular({ genre: 'Action', limit: 12 }),
          api.movies.popular({ genre: 'Comedy', limit: 12 })
        ]);
        if (isMounted) {
          setActionMovies(actionRes.movies || []);
          setComedyMovies(comedyRes.movies || []);
        }
      } catch (err) {
        console.error('Failed to load genre movies:', err);
      }
    }
    fetchGenres();
    return () => {
      isMounted = false;
    };
  }, []);

  const heroMovie = recommendations[0] || null;

  return (
    <div className="container" style={{ paddingTop: '24px', paddingBottom: '80px' }}>
      {/* Hero Section */}
      {loadingRecs && !heroMovie ? (
        <HeroSkeleton />
      ) : (
        <HeroBanner
          movie={heroMovie}
          onSelectMovie={onSelectMovie}
        />
      )}

      {/* Main Recommendation Section */}
      {recommendations.length > 0 && (
        <MovieCarousel
          title={isReturningUser ? "Recommended For You" : "Popular Movies For You"}
          movies={recommendations}
          loading={loadingRecs}
          onSelectMovie={onSelectMovie}
        />
      )}

      {/* Trending / Popular Section */}
      <PopularSection onSelectMovie={onSelectMovie} limit={12} />

      {/* Genre Sections */}
      {actionMovies.length > 0 && (
        <div style={{ marginTop: '40px' }}>
          <MovieCarousel
            title="Action Movies"
            movies={actionMovies}
            onSelectMovie={onSelectMovie}
          />
        </div>
      )}

      {comedyMovies.length > 0 && (
        <div style={{ marginTop: '40px' }}>
          <MovieCarousel
            title="Comedy Movies"
            movies={comedyMovies}
            onSelectMovie={onSelectMovie}
          />
        </div>
      )}
    </div>
  );
}
