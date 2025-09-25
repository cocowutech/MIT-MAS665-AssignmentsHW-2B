import React, { useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { useAuth } from '../contexts/AuthContext';
import { Menu, X, User, LogOut, Settings, BarChart3 } from 'lucide-react';

const Navbar = () => {
  const { isAuthenticated, user, logout } = useAuth();
  const navigate = useNavigate();
  const [isMenuOpen, setIsMenuOpen] = useState(false);

  const handleLogout = () => {
    logout();
    navigate('/');
    setIsMenuOpen(false);
  };

  return (
    <nav className="navbar">
      <div className="navbar-content">
        <Link to="/" className="navbar-brand">
          Vico Education Reading Placement
        </Link>

        <div className="navbar-nav">
          <Link to="/" onClick={() => setIsMenuOpen(false)}>Home</Link>
          
          {isAuthenticated ? (
            <>
              <Link to="/dashboard" onClick={() => setIsMenuOpen(false)}>Dashboard</Link>
              <Link to="/profile" onClick={() => setIsMenuOpen(false)}>Profile</Link>
              
              <div className="navbar-user">
                <span>Welcome, {user?.name}</span>
                <div className="dropdown">
                  <button className="btn btn-secondary">
                    <User size={16} />
                  </button>
                  <div className="dropdown-menu">
                    <Link to="/profile" className="dropdown-item">
                      <Settings size={16} />
                      Profile
                    </Link>
                    <button onClick={handleLogout} className="dropdown-item">
                      <LogOut size={16} />
                      Logout
                    </button>
                  </div>
                </div>
              </div>
            </>
          ) : (
            <>
              <Link to="/login" onClick={() => setIsMenuOpen(false)}>Login</Link>
              <Link to="/register" onClick={() => setIsMenuOpen(false)}>Register</Link>
            </>
          )}

          <button
            className="mobile-menu-btn"
            onClick={() => setIsMenuOpen(!isMenuOpen)}
          >
            {isMenuOpen ? <X size={24} /> : <Menu size={24} />}
          </button>
        </div>
      </div>

      {isMenuOpen && (
        <div className="mobile-menu">
          <Link to="/" onClick={() => setIsMenuOpen(false)}>Home</Link>
          {isAuthenticated ? (
            <>
              <Link to="/dashboard" onClick={() => setIsMenuOpen(false)}>Dashboard</Link>
              <Link to="/profile" onClick={() => setIsMenuOpen(false)}>Profile</Link>
              <button onClick={handleLogout}>Logout</button>
            </>
          ) : (
            <>
              <Link to="/login" onClick={() => setIsMenuOpen(false)}>Login</Link>
              <Link to="/register" onClick={() => setIsMenuOpen(false)}>Register</Link>
            </>
          )}
        </div>
      )}

      <style jsx>{`
        .navbar {
          position: fixed;
          top: 0;
          left: 0;
          right: 0;
          background: white;
          border-bottom: 1px solid #e2e8f0;
          z-index: 1000;
          padding: 1rem 0;
        }

        .navbar-content {
          max-width: 1200px;
          margin: 0 auto;
          padding: 0 1rem;
          display: flex;
          justify-content: space-between;
          align-items: center;
        }

        .navbar-brand {
          font-size: 1.5rem;
          font-weight: 700;
          color: #3b82f6;
          text-decoration: none;
        }

        .navbar-nav {
          display: flex;
          align-items: center;
          gap: 2rem;
          list-style: none;
        }

        .navbar-nav a {
          color: #64748b;
          text-decoration: none;
          font-weight: 500;
          transition: color 0.2s ease;
        }

        .navbar-nav a:hover {
          color: #3b82f6;
        }

        .navbar-user {
          display: flex;
          align-items: center;
          gap: 1rem;
        }

        .dropdown {
          position: relative;
          display: inline-block;
        }

        .dropdown-menu {
          position: absolute;
          top: 100%;
          right: 0;
          background: white;
          border: 1px solid #e2e8f0;
          border-radius: 0.5rem;
          box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
          min-width: 150px;
          z-index: 1000;
          display: none;
        }

        .dropdown:hover .dropdown-menu {
          display: block;
        }

        .dropdown-item {
          display: flex;
          align-items: center;
          gap: 0.5rem;
          padding: 0.75rem 1rem;
          color: #374151;
          text-decoration: none;
          border: none;
          background: none;
          width: 100%;
          text-align: left;
          cursor: pointer;
          transition: background-color 0.2s ease;
        }

        .dropdown-item:hover {
          background-color: #f3f4f6;
        }

        .mobile-menu-btn {
          display: none;
          background: none;
          border: none;
          cursor: pointer;
          color: #64748b;
        }

        .mobile-menu {
          display: none;
          position: absolute;
          top: 100%;
          left: 0;
          right: 0;
          background: white;
          border-bottom: 1px solid #e2e8f0;
          padding: 1rem;
          flex-direction: column;
          gap: 1rem;
        }

        @media (max-width: 768px) {
          .navbar-nav > a,
          .navbar-user {
            display: none;
          }

          .mobile-menu-btn {
            display: block;
          }

          .mobile-menu {
            display: flex;
          }
        }
      `}</style>
    </nav>
  );
};

export default Navbar;
