import React, { useState } from 'react';
import './LazyImage.css';

const LazyImage = ({ src, alt, className }) => {
  const [loaded, setLoaded] = useState(false);

  return (
    <div className={`lazy-image-wrapper ${className || ''}`}>
      {!loaded && <div className="lazy-image-placeholder" />}
      <img
        src={src}
        alt={alt}
        loading="lazy"
        onLoad={() => setLoaded(true)}
        className={loaded ? 'lazy-image-img loaded' : 'lazy-image-img hidden'}
      />
    </div>
  );
};

export default LazyImage;