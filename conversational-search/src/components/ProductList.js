import React from 'react';
import '../styles/ProductList.css';

function ProductList({ products }) {
  const exchangeRates = {
    QAR: 0.2740, // Qatari Riyal
    KWD: 3.2415, // Kuwaiti Dinar
    OMR: 2.6000, // Omani Rial
    AED: 0.2723, // UAE Dirham
    SAR: 0.2666, // Saudi Riyal
    BHD: 2.6596, // Bahraini Dinar
    USD: 1.0000, // US Dollar
  };

  const convertToUSD = (price, currency) => {
    const rate = exchangeRates[currency];
    if (rate) {
      return (price * rate).toFixed(2); // Convert and format to 2 decimal places
    }
    return price; // If no rate is found, return the original price
  };

  return (
    <div className="product-list">
      {products.map((product, index) => (
        <div key={`${product.id}-${index}`} className="product-card">
          <img src={product.images[0]} alt={product.name} className="product-image" />
          <h3 className="product-name">{product.name}</h3>
          <div className="product-prices">
            {product.old_price && (
              <span className="product-old-price">
                USD {convertToUSD(product.old_price, product.currency)}
              </span>
            )}
            {product.off_percent && (
              <span className="product-discount">({product.off_percent}% Off)</span>
            )}
            <p className="product-price">
              USD {convertToUSD(product.current_price, product.currency)}
            </p>
          </div>
        </div>
      ))}
    </div>
  );
}

export default ProductList;

