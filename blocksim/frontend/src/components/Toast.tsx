import React from 'react';

export const Toast: React.FC<{ message: string | null; onClose?: () => void }> = ({ message, onClose }) => {
  if (!message) return null;
  return (
    <div style={{ position: 'fixed', top: 16, right: 16, background: '#0f172a', color: '#e2e8f0', padding: '8px 12px', borderRadius: 6, boxShadow: '0 4px 12px rgba(0,0,0,0.2)' }}>
      <div>{message}</div>
      {onClose && <button onClick={onClose} style={{ marginLeft: 8 }}>Close</button>}
    </div>
  );
};
