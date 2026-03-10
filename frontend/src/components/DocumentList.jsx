import React from "react";

export default function DocumentList({ documents, onClear }) {
  if (documents.length === 0) return null;

  return (
    <div className="doc-section">
      <h3>Indexed Documents</h3>
      <ul className="doc-list">
        {documents.map((doc, idx) => (
          <li key={idx}>{doc}</li>
        ))}
      </ul>
      <button className="clear-btn" onClick={onClear}>
        Clear All Documents
      </button>
    </div>
  );
}
