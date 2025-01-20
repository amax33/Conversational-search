import React, { useEffect, useState } from 'react';
import axios from 'axios';
import SearchBar from './components/SearchBar';
import ProductList from './components/ProductList';
import Filters from './components/Filters';
import Chat from './components/Chat';
import './styles/App.css';

const exchangeRates = {
  QAR: 0.2740, // Qatari Riyal
  KWD: 3.2415, // Kuwaiti Dinar
  OMR: 2.6000, // Omani Rial
  AED: 0.2723, // UAE Dirham
  SAR: 0.2666, // Saudi Riyal
  BHD: 2.6596, // Bahraini Dinar
  USD: 1.0000, // US Dollar
};

function convertToUSD(price, currency) {
  const rate = exchangeRates[currency];
  return rate ? price * rate : price; // Convert price to USD or return original if no rate found
}

function App() {
  const [allProducts, setAllProducts] = useState([]);
  const [filteredProducts, setFilteredProducts] = useState([]);
  const [filters, setFilters] = useState({
    priceMin: null,
    priceMax: null,
    category: '',
    size: '',
  });

  useEffect(() => {
    fetchProducts('');
  }, []);

  const fetchProducts = async (query) => {
    try {
      const response = await axios.get(`http://127.0.0.1:8000/api/search?query=${query}`);
      const convertedProducts = response.data.hits.map((product) => ({
        ...product,
        current_price_usd: convertToUSD(product.current_price, product.currency),
        old_price_usd: product.old_price ? convertToUSD(product.old_price, product.currency) : null,
      }));
      setAllProducts(convertedProducts);
      applyFiltersToProducts(convertedProducts, filters); // Ensure filters are applied to new products
    } catch (error) {
      console.error('Error fetching products:', error);
    }
  };

  const applyFiltersToProducts = (products, activeFilters) => {
    let results = products;

    if (activeFilters.priceMin) {
      results = results.filter(
        (product) => product.current_price_usd >= activeFilters.priceMin
      );
    }

    if (activeFilters.priceMax) {
      results = results.filter(
        (product) => product.current_price_usd <= activeFilters.priceMax
      );
    }

    if (activeFilters.category) {
      results = results.filter((product) => product.category_name === activeFilters.category);
    }

    if (activeFilters.size) {
      results = results.filter((product) => product.sizes.includes(activeFilters.size));
    }

    setFilteredProducts(results);
  };

  const handleSearch = (query) => {
    fetchProducts(query); // Fetch products matching the query
  };

  const handleFiltersUpdate = (newFilters) => {
    const updatedFilters = { ...filters, ...newFilters };
    setFilters(updatedFilters);
    applyFiltersToProducts(allProducts, updatedFilters); // Apply filters to existing products
  };

  return (
    <div className="app-container">
      <div className="main-content">
        <div className="search-section">
          <SearchBar onSearch={handleSearch} />
        </div>
        <div className="filters-section">
          <Filters filters={filters} onApplyFilters={handleFiltersUpdate} />
        </div>
        <div className="results-section">
          <ProductList products={filteredProducts} />
        </div>
      </div>
      <div className="chat-section">
        <Chat onQuery={handleSearch} onFiltersUpdate={handleFiltersUpdate} />
      </div>
    </div>
  );
}

export default App;
