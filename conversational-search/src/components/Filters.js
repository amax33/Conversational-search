import React, { useState } from 'react';
import '../styles/Filters.css';

const categories = [
  'tops', 'shirts', 'sweatshirts', 'bags', 'watches', 'shoes', 'earrings',
  'keychains', 'belts', 'headbands', 'dresses', 't-shirts', 'raincoats',
  'sunglasses', 'kimonos', 'blouses', 'shorts', 'hoodies', 'waistcoats',
  'scarves', 'anklets', 'scrunchies', 'rings', 'pants', 'skirts', 'jackets',
  'sweaters', 'bracelets', 'necklaces', 'socks', 'blazers', 'coats', 'ties',
  'hats', 'bodysuits', 'jalabiyas', 'jumpsuits', 'turbans', 'bras', 'swimwears',
  'slippers', 'briefs', 'abayas', 'shackets', 'suits', 'cases', 'patches',
  'gloves', 'capes', 'polo shirts', 'kaftans', 'jewelry sets'
];

const sizes = ['S', 'M', 'L', 'XL', '2XL'];

function Filters({ filters, onApplyFilters }) {
  const [localFilters, setLocalFilters] = useState(filters);

  const handleFilterChange = (e) => {
    const { name, value } = e.target;
    setLocalFilters({ ...localFilters, [name]: value });
  };

  const applyFilters = () => {
    onApplyFilters(localFilters);
  };

  return (
    <div className="filters">
      <div className="filter-group">
        <label>Min Price</label>
        <input
          type="number"
          name="priceMin"
          placeholder="Min price"
          value={localFilters.priceMin || ''}
          onChange={handleFilterChange}
        />
      </div>
      <div className="filter-group">
        <label>Max Price</label>
        <input
          type="number"
          name="priceMax"
          placeholder="Max price"
          value={localFilters.priceMax || ''}
          onChange={handleFilterChange}
        />
      </div>
      <div className="filter-group">
        <label>Category</label>
        <select name="category" value={localFilters.category} onChange={handleFilterChange}>
          <option value="">All Categories</option>
          {categories.map((category) => (
            <option key={category} value={category}>
              {category}
            </option>
          ))}
        </select>
      </div>
      <div className="filter-group">
        <label>Size</label>
        <select name="size" value={localFilters.size} onChange={handleFilterChange}>
          <option value="">All Sizes</option>
          {sizes.map((size) => (
            <option key={size} value={size}>
              {size}
            </option>
          ))}
        </select>
      </div>
      <button className="apply-filters-button" onClick={applyFilters}>
        Apply Filters
      </button>
    </div>
  );
}

export default Filters;

