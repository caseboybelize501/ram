import React, { useEffect, useState } from 'react';

const Sources = () => {
  const [syncStatus, setSyncStatus] = useState({});

  useEffect(() => {
    fetch('http://localhost:8000/api/sync/status')
      .then(res => res.json())
      .then(data => setSyncStatus(data))
      .catch(err => console.error('Error fetching sync status:', err));
  }, []);

  const triggerSync = (source) => {
    fetch(`http://localhost:8000/api/sync/trigger`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ source })
    });
  };

  return (
    <div className="sources-container">
      <h2>Connected Sources</h2>
      <div className="source-list">
        {Object.entries(syncStatus).map(([source, status]) => (
          <div key={source} className="source-item">
            <span>{source}</span>
            <span className={`status ${status.status}`}>{status.status}</span>
            <button onClick={() => triggerSync(source)}>Sync Now</button>
          </div>
        ))}
      </div>
    </div>
  );
};

export default Sources;