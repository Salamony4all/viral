import React, { useState } from 'react';
import ReactMarkdown from 'react-markdown';
import {
  DollarSign,
  TrendingUp,
  Target,
  Download,
  ChevronDown,
  ChevronUp,
} from 'lucide-react';
import type { Product, EarningsProjection } from '../types';
import './MonetizationBrief.css';

interface MonetizationBriefProps {
  brief?: string;
  products?: Product[];
  earnings_projection?: EarningsProjection;
}

export const MonetizationBrief: React.FC<MonetizationBriefProps> = ({
  brief,
  products = [],
  earnings_projection,
}) => {
  const [briefOpen, setBriefOpen] = useState(false);

  const handleDownloadBrief = () => {
    if (!brief) return;
    const blob = new Blob([brief], { type: 'text/markdown' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = 'PROFIT_BRIEF.md';
    a.click();
    URL.revokeObjectURL(url);
  };

  return (
    <div className="monetization-brief">
      {/* Header */}
      <div className="brief-header">
        <DollarSign size={22} />
        <h3>Monetization Strategy</h3>
      </div>

      {/* Earnings projection */}
      {earnings_projection && (
        <div className="earnings-card">
          <TrendingUp size={22} />
          <div className="earnings-info">
            <span className="earnings-label">Estimated Earnings Potential</span>
            <div className="earnings-rows">
              <div className="earnings-row">
                <span className="earnings-scenario">Conservative</span>
                <span className="earnings-value">{earnings_projection.conservative}</span>
              </div>
              <div className="earnings-row">
                <span className="earnings-scenario">Viral Scenario</span>
                <span className="earnings-value viral">{earnings_projection.viral}</span>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Products */}
      {products.length > 0 && (
        <div className="products-section">
          <h4>
            <Target size={16} /> Recommended Products ({products.length})
          </h4>
          <div className="products-grid">
            {products.map((product, idx) => (
              <div key={idx} className="product-card">
                <div className="product-card-top">
                  <h5>{product.name}</h5>
                  {product.affiliate_network && (
                    <span className="product-network">{product.affiliate_network}</span>
                  )}
                </div>
                <div className="product-details">
                  {product.price && <span className="product-price">{product.price}</span>}
                  {product.commission && (
                    <span className="product-commission">{product.commission} commission</span>
                  )}
                </div>
                {product.rating != null && product.rating > 0 && (
                  <div className="product-rating">
                    {'★'.repeat(Math.round(product.rating))}
                    {'☆'.repeat(5 - Math.round(product.rating))}{' '}
                    <span>{product.rating.toFixed(1)}</span>
                  </div>
                )}
                {product.reason && <p className="product-reason">{product.reason}</p>}
                {product.url && (
                  <a
                    href={product.url}
                    target="_blank"
                    rel="noopener noreferrer"
                    className="product-link"
                  >
                    View Product &rarr;
                  </a>
                )}
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Full brief (collapsible) */}
      {brief && (
        <div className="brief-section">
          <div className="brief-section-header">
            <button
              className="brief-toggle"
              onClick={() => setBriefOpen((o) => !o)}
            >
              <h4>Full Monetization Brief</h4>
              {briefOpen ? <ChevronUp size={16} /> : <ChevronDown size={16} />}
            </button>
            <button className="brief-download-btn" onClick={handleDownloadBrief}>
              <Download size={14} />
              Download .md
            </button>
          </div>
          {briefOpen && (
            <div className="brief-content markdown-body">
              <ReactMarkdown>{brief}</ReactMarkdown>
            </div>
          )}
        </div>
      )}
    </div>
  );
};
