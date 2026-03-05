import React, { useEffect, useState } from 'react';

const Graph = () => {
  const [entities, setEntities] = useState([]);
  
  useEffect(() => {
    fetch('http://localhost:8000/api/graph/entities')
      .then(res => res.json())
      .then(data => setEntities(data))
      .catch(err => console.error('Error fetching entities:', err));
  }, []);

  return (
    <div className="graph-container">
      <h2>Knowledge Graph</h2>
      <div className="entities-grid">
        {entities.map((entity, index) => (
          <div key={index} className="entity-card">
            <h3>{entity}</h3>
          </div>
        ))}
      </div>
    </div>
  );
};

export default Graph;