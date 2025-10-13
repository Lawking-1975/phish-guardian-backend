// src/components/ResultCard.jsx
import { motion } from "framer-motion";
import Speedometer from "./Speedometer";
import { FaThumbsUp, FaExclamationTriangle, FaArrowRight } from "react-icons/fa";

export default function ResultCard({ result }) {
  if (!result) return null;

  const isLegit = result.status === "legit";
  const conf = result.confidence ?? null;

  return (
    <motion.div
      initial={{ opacity: 0, y: 8 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.35 }}
      className={`w-full max-w-2xl mt-6 p-6 rounded-xl shadow-lg ${
        isLegit ? "bg-green-50/80 border border-green-200" : "bg-red-50/80 border border-red-200"
      }`}
    >
      <div className="flex items-start gap-6">
        <div className="w-48">
          <Speedometer value={typeof conf === "number" ? conf : 0} />
        </div>

        <div className="flex-1">
          <div className="flex items-start justify-between mb-2">
            <div>
              <h3 className="text-2xl font-semibold">
                {isLegit ? "✅ Legit Website" : "🚨 Phishing Detected"}
              </h3>
              <p className="text-sm text-gray-600 mt-1">{result.normalized || result.url}</p>
            </div>
            <div className="text-right">
              {/* Animated icon */}
              {isLegit ? (
                <motion.div
                  initial={{ scale: 0.6 }}
                  animate={{ scale: 1 }}
                  transition={{ duration: 0.35, type: "spring" }}
                  className="text-green-700"
                >
                  <FaThumbsUp size={36} />
                </motion.div>
              ) : (
                <motion.div
                  initial={{ scale: 0.8 }}
                  animate={{ rotate: [0, -8, 8, -8, 8, 0] }}
                  transition={{ duration: 1.2, repeat: Infinity }}
                  className="text-red-600"
                >
                  <FaExclamationTriangle size={36} />
                </motion.div>
              )}
            </div>
          </div>

          <div className="mb-4">
            <p className="text-sm text-gray-700">
              Confidence:{" "}
              <span className="font-medium">{conf ?? "N/A"}{typeof conf === "number" ? "%" : ""}</span>
            </p>
            <p className="text-sm text-gray-500 mt-1">Reason: {result.reason || "ml_prediction"}</p>
          </div>

          {result.suggestion && (
            <div className="mt-2">
              <a
                href={result.suggestion.suggested_url}
                target="_blank"
                rel="noopener noreferrer"
                className="inline-flex items-center gap-2 px-4 py-2 bg-blue-600 text-white rounded-md shadow hover:bg-blue-700 transform hover:-translate-y-0.5 transition"
                title="Open suggested official URL"
              >
                <FaArrowRight />
                Go to suggested site
                <span className="ml-2 text-xs opacity-80">({result.suggestion.similarity}% match)</span>
              </a>
            </div>
          )}
        </div>
      </div>
    </motion.div>
  );
}
