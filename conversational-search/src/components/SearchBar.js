import React, { useState } from 'react';
import '../styles/SearchBar.css';

function SearchBar({ onSearch }) {
  const [localQuery, setLocalQuery] = useState('');

  const handleInputChange = (e) => {
    setLocalQuery(e.target.value);
  };

  const handleSearchClick = () => {
    onSearch(localQuery); // Trigger search only when the button is clicked
  };
  const handleKeyDown = (e) => {
     if (e.key === 'Enter') {
        onSearch(localQuery);
     }
  };


  return (
    <div className="search-bar">
      <input
        type="text"
        placeholder="Search for products..."
        value={localQuery}
        onChange={handleInputChange}
        className="search-input"
      />
      <button className="search-button" onClick={handleSearchClick}>
        Search
      </button>
    </div>
  );
}

export default SearchBar;

