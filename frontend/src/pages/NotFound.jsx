import React from 'react';
import { Link } from 'react-router-dom';

export default function NotFound() {
  return (
    <div className="glass-card notfound">
      <h2>404: Not Found</h2>
      <p>Sorry, this page doesn&rsquo;t exist. Return to the <Link to="/">dashboard</Link>?</p>
    </div>
  );
}
