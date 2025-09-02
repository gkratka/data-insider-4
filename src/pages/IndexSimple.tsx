/**
 * Simple Index page for debugging
 */
import React from 'react';

const IndexSimple = () => {
  return (
    <div className="min-h-screen bg-gray-50 flex items-center justify-center">
      <div className="text-center">
        <h1 className="text-2xl font-bold mb-4">Data Intelligence Platform</h1>
        <p className="text-gray-600">Frontend is working!</p>
        <div className="mt-4">
          <button 
            className="bg-blue-500 text-white px-4 py-2 rounded hover:bg-blue-600"
            onClick={() => alert('Button clicked!')}
          >
            Test Button
          </button>
        </div>
      </div>
    </div>
  );
};

export default IndexSimple;