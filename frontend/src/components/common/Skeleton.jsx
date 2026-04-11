import React from 'react';
import './Skeleton.css';

// ─── Primitive block ──────────────────────────────────────────────────────────
export const Sk = ({ className = '', style }) => (
  <div className={`skeleton-block ${className}`} style={style} />
);

// ─── ItemCard skeleton (used in grid lists) ───────────────────────────────────
export const ItemCardSkeleton = () => (
  <div className="sk-card">
    <Sk className="sk-card-img" />
    <div className="sk-card-body">
      <Sk className="sk-w-3-4 sk-h-6" />
      <Sk className="sk-w-1-2 sk-h-4" />
      <Sk className="sk-w-full sk-h-4" />
      <Sk className="sk-w-full sk-h-10" style={{ marginTop: '8px', borderRadius: '8px' }} />
    </div>
  </div>
);

// ─── ItemDetail skeleton ──────────────────────────────────────────────────────
export const ItemDetailSkeleton = () => (
  <div className="sk-detail-grid">
    {/* Left: image */}
    <div>
      <Sk className="sk-detail-img" />
    </div>

    {/* Right: info panel */}
    <div className="sk-detail-body">
      <Sk className="sk-w-1-2 sk-h-8" />
      <Sk className="sk-w-1-4 sk-h-4" />
      <div className="sk-specs-grid">
        {Array.from({ length: 6 }).map((_, i) => (
          <div key={i} style={{ display: 'flex', flexDirection: 'column', gap: '6px' }}>
            <Sk className="sk-w-1-2 sk-h-4" />
            <Sk className="sk-w-3-4 sk-h-5" />
          </div>
        ))}
      </div>
      <Sk className="sk-w-full sk-h-24" style={{ borderRadius: '8px' }} />
      <Sk className="sk-w-full sk-h-12" style={{ borderRadius: '8px', marginTop: '8px' }} />
    </div>
  </div>
);

// ─── Activity page skeleton (2-column: reports + claims) ─────────────────────
export const ActivitySkeleton = ({ rows = 3 }) => (
  <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(400px, 1fr))', gap: '1.5rem', marginTop: '1rem' }}>
    {[0, 1].map(col => (
      <div key={col} style={{ display: 'flex', flexDirection: 'column', gap: '1rem' }}>
        <Sk className="sk-w-1-3 sk-h-6" />
        {Array.from({ length: rows }).map((_, i) => (
          <div key={i} className="sk-activity-row">
            <div className="sk-activity-header">
              <Sk className="sk-w-1-2 sk-h-5" />
              <Sk className="sk-w-1-4 sk-h-4" />
            </div>
            <Sk className="sk-w-3-4 sk-h-4" />
            <Sk className="sk-w-1-2 sk-h-4" />
          </div>
        ))}
      </div>
    ))}
  </div>
);

// ─── Admin claim list skeleton ────────────────────────────────────────────────
export const ClaimListSkeleton = ({ rows = 4 }) => (
  <div style={{ display: 'flex', flexDirection: 'column', gap: '1rem' }}>
    {Array.from({ length: rows }).map((_, i) => (
      <div key={i} className="sk-claim-card">
        <div className="sk-claim-top">
          <div style={{ display: 'flex', flexDirection: 'column', gap: '8px', flex: 1 }}>
            <Sk className="sk-w-1-3 sk-h-6" />
            <Sk className="sk-w-1-2 sk-h-4" />
          </div>
          <Sk style={{ width: '110px', height: '38px', borderRadius: '8px' }} />
        </div>
        <div className="sk-claim-body">
          <Sk style={{ width: '100%', height: '100px', borderRadius: '6px' }} />
          <div style={{ display: 'flex', flexDirection: 'column', gap: '10px' }}>
            <Sk className="sk-w-full sk-h-4" />
            <Sk className="sk-w-full sk-h-4" />
            <Sk className="sk-w-3-4 sk-h-4" />
          </div>
        </div>
      </div>
    ))}
  </div>
);

// ─── Admin dashboard stats skeleton ──────────────────────────────────────────
export const DashboardSkeleton = () => (
  <div className="sk-stats-grid">
    {Array.from({ length: 4 }).map((_, i) => (
      <div key={i} className="sk-stat-card">
        <Sk className="sk-w-3-4 sk-h-4" />
        <Sk className="sk-w-1-3 sk-h-10" />
      </div>
    ))}
  </div>
);

// ─── Generic grid of card skeletons (shared by LostItems / ReturnedItems) ─────
export const ItemGridSkeleton = ({ count = 6 }) => (
  <div className="grid-layout">
    {Array.from({ length: count }).map((_, i) => (
      <ItemCardSkeleton key={i} />
    ))}
  </div>
);
