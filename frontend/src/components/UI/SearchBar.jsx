import React from 'react';
import './SearchBar.css';

const SearchBar = ({ onSearch, onFilter }) => {
    return (
        <div className="search-section">
            <div className="search-bar-container">
                <div className="search-input-wrapper">
                    <span className="search-icon">🔍</span>
                    <input
                        type="text"
                        placeholder="Search lost items by name, color, or location..."
                        className="search-input"
                        onChange={(e) => onSearch(e.target.value)}
                    />
                </div>

                <div className="filter-dropdown-container">
                    <select className="filter-select" onChange={(e) => onFilter(e.target.value)}>
                        <option value="">Sort By</option>
                        <option value="item_type">Item Type</option>
                        <option value="found_datetime">Date Found</option>
                        <option value="created_at">Date Reported</option>
                        <option value="found_location">Location Found</option>
                    </select>
                </div>
            </div>
        </div>
    );
};

export default SearchBar;

