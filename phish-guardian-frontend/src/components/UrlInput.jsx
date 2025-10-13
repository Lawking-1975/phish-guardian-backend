// src/components/UrlInput.jsx
import { useState } from "react";

export default function UrlInput({ onSubmit, loading }) {
  const [url, setUrl] = useState("");

  function handleSubmit(e) {
    e?.preventDefault();
    if (!url.trim()) return;
    onSubmit(url.trim());
  }

  return (
    <form onSubmit={handleSubmit} className="w-full max-w-xl">
      <div className="flex gap-3 items-center">
        <input
          value={url}
          onChange={(e) => setUrl(e.target.value)}
          placeholder="Enter URL (example: klnce.com)"
          className="flex-1 px-4 py-3 rounded-lg border border-gray-300 focus:outline-none focus:ring-2 focus:ring-blue-400 bg-white"
        />
        <button
          type="submit"
          onClick={handleSubmit}
          disabled={loading}
          className="px-4 py-2 rounded-lg bg-blue-600 text-white font-semibold hover:bg-blue-700 disabled:opacity-50"
        >
          {loading ? "Checking..." : "Check URL"}
        </button>
      </div>
    </form>
  );
}
