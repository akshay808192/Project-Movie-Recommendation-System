/**
 * Main Application Orchestrator & View Switcher
 * Supporting 9 Cinematic Streaming Pages, Toast Notifications & Global Glass Modals
 */

import React, { useState } from 'react';
import { ToastProvider } from './context/ToastContext';
import { AuthProvider, useAuth } from './context/AuthContext';
import Navbar from './components/Navbar';
import Footer from './components/Footer';
import MovieDetails from './components/MovieDetails';
import AuthModal from './components/AuthModal';

// 9 Cinematic Pages
import Home from './pages/Home';
import DiscoverPage from './pages/DiscoverPage';
import SearchPage from './pages/SearchPage';
import MovieDetailsPage from './pages/MovieDetailsPage';
import LoginPage from './pages/LoginPage';
import RegisterPage from './pages/RegisterPage';
import ProfilePage from './pages/ProfilePage';
import WatchHistoryPage from './pages/WatchHistoryPage';
import FavoritesPage from './pages/FavoritesPage';
import OnboardingPage from './pages/OnboardingPage';

// Additional feature views
import RecommendationsPage from './pages/RecommendationsPage';
import PopularPage from './pages/PopularPage';

function MainLayout() {
  const [activeTab, setActiveTab] = useState('home');
  const [selectedMovieId, setSelectedMovieId] = useState(null);
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [isAuthModalOpen, setIsAuthModalOpen] = useState(false);
  const { isAuthenticated } = useAuth();

  // Handle card click across any page
  const handleSelectMovie = (movie) => {
    const id = movie.movieId || movie.id;
    setSelectedMovieId(id);
    setIsModalOpen(true);
  };

  // Switch to dedicated full-page movie details view
  const handleViewFullPage = (movieId) => {
    setSelectedMovieId(movieId);
    setIsModalOpen(false);
    setActiveTab('details');
    window.scrollTo({ top: 0, behavior: 'smooth' });
  };

  const handleCloseModal = () => {
    setIsModalOpen(false);
  };

  const handleSelectTab = (tab) => {
    if ((tab === 'profile' || tab === 'history' || tab === 'favorites') && !isAuthenticated) {
      setIsAuthModalOpen(true);
      return;
    }
    setActiveTab(tab);
    window.scrollTo({ top: 0, behavior: 'smooth' });
  };

  return (
    <div style={{ display: 'flex', flexDirection: 'column', minHeight: '100vh' }}>
      <Navbar
        activeTab={activeTab}
        onSelectTab={handleSelectTab}
        onOpenAuthModal={() => setIsAuthModalOpen(true)}
      />

      <main style={{ flex: 1 }} className="page-transition" key={activeTab}>
        {/* Page 1: Home */}
        {activeTab === 'home' && (
          <Home
            onSelectMovie={handleSelectMovie}
            onNavigateTab={handleSelectTab}
          />
        )}

        {/* Page 2: Discover (Catalog & Genres) */}
        {activeTab === 'discover' && (
          <DiscoverPage onSelectMovie={handleSelectMovie} />
        )}

        {/* Page 3: Search (Real-time live search) */}
        {activeTab === 'search' && (
          <SearchPage onSelectMovie={handleSelectMovie} />
        )}

        {/* Page 4: Movie Details (Dedicated Full-Page View) */}
        {activeTab === 'details' && (
          <MovieDetailsPage
            movieId={selectedMovieId}
            onBack={() => handleSelectTab('home')}
            onSelectMovie={handleSelectMovie}
          />
        )}

        {/* Page 5: Login */}
        {activeTab === 'login' && (
          <LoginPage onNavigateTab={handleSelectTab} />
        )}

        {/* Page 6: Register */}
        {activeTab === 'register' && (
          <RegisterPage onNavigateTab={handleSelectTab} />
        )}

        {/* Onboarding */}
        {activeTab === 'onboarding' && (
          <OnboardingPage onComplete={() => handleSelectTab('home')} />
        )}

        {/* Page 7: Profile */}
        {activeTab === 'profile' && (
          <ProfilePage
            onSelectMovie={handleSelectMovie}
            onNavigateTab={handleSelectTab}
          />
        )}

        {/* Page 8: Watch History */}
        {activeTab === 'history' && (
          <WatchHistoryPage onSelectMovie={handleSelectMovie} />
        )}

        {/* Page 9: My Favorites */}
        {activeTab === 'favorites' && (
          <FavoritesPage
            onSelectMovie={handleSelectMovie}
            onNavigateTab={handleSelectTab}
          />
        )}

        {/* Recommendations & Popular deep-dive views */}
        {activeTab === 'recommendations' && (
          <RecommendationsPage onSelectMovie={handleSelectMovie} />
        )}

        {activeTab === 'popular' && (
          <PopularPage onSelectMovie={handleSelectMovie} />
        )}
      </main>

      <Footer />

      {/* Global Quick-Preview Glass Modal */}
      {isModalOpen && selectedMovieId && (
        <MovieDetails
          movieId={selectedMovieId}
          onClose={handleCloseModal}
          onSelectMovie={handleSelectMovie}
          onViewFullPage={handleViewFullPage}
        />
      )}

      {/* Global Sign In / Register Glass Modal */}
      <AuthModal
        isOpen={isAuthModalOpen}
        onClose={() => setIsAuthModalOpen(false)}
      />
    </div>
  );
}

export default function App() {
  return (
    <ToastProvider>
      <AuthProvider>
        <MainLayout />
      </AuthProvider>
    </ToastProvider>
  );
}
