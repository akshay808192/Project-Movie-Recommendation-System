import React, { useState } from 'react';
import {
  Film, Sparkles, Compass, Search, Heart, History, User,
  LogIn, LogOut, Menu, X, ArrowRight
} from 'lucide-react';
import { useAuth } from '../context/AuthContext';

export default function Navbar({ activeTab, onSelectTab, onOpenAuthModal }) {
  const { user, isAuthenticated, logout, summary } = useAuth();
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false);

  const getStrategyBadgeClass = () => {
    if (!summary) return 'strategy-badge-cold';
    if (summary.active_strategy === 'COLLABORATIVE_FILTERING') return 'strategy-badge-cf';
    if (summary.active_strategy === 'HYBRID_TRANSITION') return 'strategy-badge-hybrid';
    return 'strategy-badge-cold';
  };

  const getStrategyIcon = () => {
    if (!summary || summary.active_strategy === 'COLD_START_POPULARITY') return '❄️';
    if (summary.active_strategy === 'HYBRID_TRANSITION') return '⚡';
    return '🎯';
  };

  const handleNavClick = (tab) => {
    onSelectTab(tab);
    setMobileMenuOpen(false);
  };

  const navLinks = [
    { id: 'home', label: 'Home' },
    { id: 'discover', label: 'Discover', icon: Compass },
    { id: 'search', label: 'Search', icon: Search },
    { id: 'favorites', label: 'My Favorites', icon: Heart },
    { id: 'history', label: 'Watch History', icon: History },
  ];

  return (
    <header
      className="navbar-enter"
      style={{
        position: 'sticky',
        top: 0,
        zIndex: 50,
        backdropFilter: 'blur(20px)',
        WebkitBackdropFilter: 'blur(20px)',
        backgroundColor: 'rgba(7, 9, 14, 0.85)',
        borderBottom: '1px solid rgba(255, 255, 255, 0.08)',
        transition: 'all 0.3s ease',
      }}
    >
      <div
        className="container"
        style={{
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'space-between',
          height: '74px',
        }}
      >
        {/* Brand Logo */}
        <div
          onClick={() => handleNavClick('home')}
          style={{
            display: 'flex',
            alignItems: 'center',
            gap: '12px',
            cursor: 'pointer',
            userSelect: 'none',
          }}
        >
          <div
            style={{
              width: '42px',
              height: '42px',
              borderRadius: '14px',
              background: 'linear-gradient(135deg, #06b6d4 0%, #3b82f6 100%)',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              boxShadow: '0 0 20px rgba(6, 182, 212, 0.45)',
            }}
          >
            <Film size={22} color="#ffffff" />
          </div>
          <div>
            <div style={{ display: 'flex', alignItems: 'center', gap: '6px' }}>
              <span
                style={{
                  fontSize: '1.3rem',
                  fontWeight: 800,
                  letterSpacing: '-0.5px',
                  color: '#ffffff',
                  fontFamily: 'var(--font-display)',
                }}
              >
                CineMatch<span style={{ color: '#06b6d4' }}>AI</span>
              </span>
            </div>
          </div>
        </div>

        {/* Desktop Navigation Links */}
        <nav
          className="desktop-nav"
          style={{
            display: 'flex',
            alignItems: 'center',
            gap: '6px',
          }}
        >
          {navLinks.map((link) => {
            const Icon = link.icon;
            const isActive = activeTab === link.id;
            return (
              <button
                key={link.id}
                onClick={() => handleNavClick(link.id)}
                style={{
                  background: isActive ? 'rgba(255, 255, 255, 0.1)' : 'transparent',
                  color: isActive ? '#ffffff' : '#94a3b8',
                  border: isActive ? '1px solid rgba(255, 255, 255, 0.15)' : '1px solid transparent',
                  padding: '8px 16px',
                  borderRadius: '9999px',
                  cursor: 'pointer',
                  fontWeight: 600,
                  fontSize: '0.88rem',
                  display: 'flex',
                  alignItems: 'center',
                  gap: '6px',
                  transition: 'all 0.2s ease',
                }}
              >
                {Icon && <Icon size={15} style={{ color: isActive ? '#06b6d4' : '#64748b' }} />}
                {link.label}
              </button>
            );
          })}
        </nav>

        {/* Right Section: Auth Controls */}
        <div style={{ display: 'flex', alignItems: 'center', gap: '14px' }}>          {/* User Session Profile / Auth Buttons */}
          {isAuthenticated ? (
            <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
              <button
                onClick={() => handleNavClick('profile')}
                className="btn-secondary"
                style={{
                  padding: '7px 14px',
                  fontSize: '0.85rem',
                  gap: '6px',
                }}
                title="View user profile and recommendation stats"
              >
                <User size={15} style={{ color: '#06b6d4' }} />
                <span>{user?.username || 'Profile'}</span>
              </button>

              <button
                onClick={logout}
                style={{
                  background: 'rgba(255, 255, 255, 0.05)',
                  border: '1px solid rgba(255, 255, 255, 0.1)',
                  borderRadius: '50%',
                  width: '36px',
                  height: '36px',
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'center',
                  color: '#94a3b8',
                  cursor: 'pointer',
                  transition: 'all 0.2s',
                }}
                title="Sign out"
              >
                <LogOut size={16} />
              </button>
            </div>
          ) : (
            <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
              <button
                onClick={() => onOpenAuthModal ? onOpenAuthModal() : handleNavClick('login')}
                className="btn-secondary"
                style={{ padding: '7px 16px', fontSize: '0.85rem' }}
              >
                <LogIn size={15} /> Sign In
              </button>
              <button
                onClick={() => handleNavClick('register')}
                className="btn-primary"
                style={{ padding: '7px 16px', fontSize: '0.85rem' }}
              >
                Register
              </button>
            </div>
          )}

          {/* Mobile Hamburger Toggle */}
          <button
            onClick={() => setMobileMenuOpen(!mobileMenuOpen)}
            className="mobile-toggle"
            style={{
              display: 'none',
              background: 'none',
              border: 'none',
              color: '#f8fafc',
              cursor: 'pointer',
              padding: '6px',
            }}
          >
            {mobileMenuOpen ? <X size={24} /> : <Menu size={24} />}
          </button>
        </div>
      </div>

      {/* Mobile Drawer */}
      {mobileMenuOpen && (
        <div
          style={{
            background: 'rgba(7, 9, 14, 0.98)',
            backdropFilter: 'blur(20px)',
            borderBottom: '1px solid rgba(255, 255, 255, 0.1)',
            padding: '20px',
            display: 'flex',
            flexDirection: 'column',
            gap: '12px',
          }}
        >
          {navLinks.map((link) => (
            <button
              key={link.id}
              onClick={() => handleNavClick(link.id)}
              style={{
                textAlign: 'left',
                padding: '12px 16px',
                borderRadius: '12px',
                background: activeTab === link.id ? 'rgba(6, 182, 212, 0.15)' : 'transparent',
                color: activeTab === link.id ? '#06b6d4' : '#cbd5e1',
                border: 'none',
                fontWeight: 600,
                fontSize: '0.95rem',
                cursor: 'pointer',
              }}
            >
              {link.label}
            </button>
          ))}
        </div>
      )}
    </header>
  );
}
