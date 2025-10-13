// src/App.jsx
import { useState } from "react";
import UrlInput from "./components/UrlInput";
import ResultCard from "./components/ResultCard";
import { predictUrl } from "./api";
import { motion } from "framer-motion";

export default function App() {
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState(null);
  const [error, setError] = useState(null);

  async function handleSubmit(url) {
    setError(null);
    setResult(null);
    setLoading(true);
    try {
      const res = await predictUrl(url);
      // Normalize confidence to 0..100 (backend already sends percent)
      if (res.confidence !== undefined && res.confidence !== null) {
        // backend returns 100 etc — keep as-is
      }
      setResult(res);
    } catch (err) {
      console.error(err);
      setError("Could not reach backend. Ensure backend is running and CORS allows this origin.");
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="min-h-screen bg-gray-50 flex items-start justify-center py-10">
      <div className="w-full px-4">
        <div className="max-w-2xl mx-auto">
          <motion.h1
            className="text-4xl font-bold text-center mb-6"
            initial={{ opacity: 0, y: -6 }}
            animate={{ opacity: 1, y: 0 }}
          >
            Phish Guardian
          </motion.h1>

          <div className="bg-white p-6 rounded-xl shadow-sm">
            <UrlInput onSubmit={handleSubmit} loading={loading} />
            {error && <p className="text-red-600 mt-3">{error}</p>}
            <div className="mt-4">
              <ResultCard result={result} />
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
