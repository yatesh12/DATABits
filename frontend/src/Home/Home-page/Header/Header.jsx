import React, { useState } from 'react';
import { Link } from 'react-router-dom';
import { FaUser, FaSearch, FaBars, FaTimes } from 'react-icons/fa';
import Logo from '../../../assets/logo.png';
import './Header.css';

const Header = () => {
  const [navOpen, setNavOpen] = useState(false);
  const [searchInput, setSearchInput] = useState('');

  const toggleNav = () => {
    setNavOpen(!navOpen);
  };

  const handleSearchChange = (e) => {
    setSearchInput(e.target.value);
  };

  const handleSearchSubmit = (e) => {
    e.preventDefault();
    // Implement search functionality as needed
    alert(`Searching for: ${searchInput}`);
  };

  return (
    <header className="header">
    <div className="logo">
  <img src={Logo} alt="logo" />
  <span>DATABits</span>
</div>
      <nav>
        <ul className={navOpen ? 'active' : ''}>
          <li>
            <Link to="/">Home</Link>
          </li>
          <li>
            <Link to="/features">Features</Link>
          </li>
             <li>
            <Link to="/contact">Docs</Link>
          </li>
             <li>
            <Link to="/contact">Community</Link>
          </li>
             <li>
            <Link to="/contact">Enterprise</Link>
          </li>
          <li>
            <Link to="/pricing">Pricing</Link>
          </li>
        </ul>
      </nav>
      <div className="header-right">
        <form onSubmit={handleSearchSubmit} className="search-form">
          <input
            type="text"
            value={searchInput}
            onChange={handleSearchChange}
            className="search-input"
            placeholder="Search..."
          />
          <button type="submit" className="search-btn">
            <FaSearch />
          </button>
        </form>
        <div className="auth-buttons">
          <Link to="/register" className="register-btn">
            Sign up
          </Link>
          <Link to="/login" className="login-icon">
            <FaUser />
          </Link>
        </div>
        <button className="login-icon" onClick={toggleNav}>
          {navOpen ? <FaTimes /> : <FaBars />}
        </button>
      </div>
    </header>
  );
};

export default Header;
