import React, { useEffect, useState } from 'react';

const Timeline = () => {
  const [timeline, setTimeline] = useState([]);

  useEffect(() => {
    fetch('http://localhost:8000/api/timeline')
      .then(res => res.json())
      .then(data => setTimeline(data.items))
      .catch(err => console.error('Error fetching timeline:', err));
  }, []);

  return (
    <div className="timeline-container">
      <h2>Memory Timeline</h2>
      <div className="timeline-items">
        {timeline.map((item, index) => (
          <div key={index} className="timeline-item">
            <div className="item-header">
              <span className="source">{item.source}</span>
              <span className="date">{new Date(item.date).toLocaleDateString()}</span>
            </div>
            <p>{item.text.substring(0, 150)}...</p>
          </div>
        ))}
      </div>
    </div>
  );
};

export default Timeline;