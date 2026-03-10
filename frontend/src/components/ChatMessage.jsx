import React from "react";

export default function ChatMessage({ message }) {
  const { role, content, sources } = message;

  return (
    <div className={`message ${role}`}>
      <div className="message-content">{content}</div>
      {sources && sources.length > 0 && (
        <div className="sources">
          <div className="sources-title">Sources:</div>
          {sources.map((src, idx) => (
            <span key={idx} className="source-tag">
              {src.source} — p.{src.page}
            </span>
          ))}
        </div>
      )}
    </div>
  );
}
