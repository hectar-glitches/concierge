import React from 'react';
import './FilterBar.css';

const TAGS = ['Required', 'Career', 'Capstone', 'Social', 'Deadline', 'General'];

const FilterBar = ({ selectedTags, onTagToggle, onClearFilters }) => {
  return (
    <div className="filter-bar">
      <div className="filter-header">
        <h3>Filter by Tag</h3>
        {selectedTags.length > 0 && (
          <button onClick={onClearFilters} className="clear-button">
            Clear All
          </button>
        )}
      </div>
      <div className="filter-tags">
        {TAGS.map((tag) => (
          <button
            key={tag}
            onClick={() => onTagToggle(tag)}
            className={`filter-tag ${
              selectedTags.includes(tag) ? 'active' : ''
            }`}
          >
            {tag}
          </button>
        ))}
      </div>
    </div>
  );
};

export default FilterBar;
