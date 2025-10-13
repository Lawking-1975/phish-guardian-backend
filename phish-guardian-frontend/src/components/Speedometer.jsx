// src/components/Speedometer.jsx
import { motion, AnimatePresence } from "framer-motion";
import React from "react";

/**
 * props:
 *  - value: 0..100 (percent confidence)
 *  - size: px (default 160)
 */
export default function Speedometer({ value = 0, size = 160 }) {
  const clamp = (v) => Math.max(0, Math.min(100, v));
  const val = clamp(value);

  // Map 0..100 to -120deg..120deg (needle sweep)
  const angle = -120 + (val / 100) * 240;

  const center = size / 2;
  const radius = size * 0.38;

  return (
    <div style={{ width: size, height: size / 2 }} className="mx-auto">
      <svg viewBox={`0 0 ${size} ${size / 2}`} width={size} height={size / 2}>
        {/* background arc */}
        <path
          d={describeArc(center, center, radius, -120, 120)}
          fill="none"
          stroke="#e6e6e6"
          strokeWidth={8}
          strokeLinecap="round"
        />
        {/* colored arc segments (green/yellow/red) */}
        <path
          d={describeArc(center, center, radius, -120, -20)}
          fill="none"
          stroke="#ef4444" // red
          strokeWidth={8}
          strokeLinecap="round"
        />
        <path
          d={describeArc(center, center, radius, -20, 40)}
          fill="none"
          stroke="#f59e0b" // amber
          strokeWidth={8}
          strokeLinecap="round"
        />
        <path
          d={describeArc(center, center, radius, 40, 120)}
          fill="none"
          stroke="#10b981" // green
          strokeWidth={8}
          strokeLinecap="round"
        />

        {/* ticks */}
        {Array.from({ length: 11 }).map((_, i) => {
          const a = -120 + (i / 10) * 240;
          const inner = polarToCartesian(center, center, radius - 8, a);
          const outer = polarToCartesian(center, center, radius + 2, a);
          return (
            <line
              key={i}
              x1={inner.x}
              y1={inner.y}
              x2={outer.x}
              y2={outer.y}
              stroke="#444"
              strokeWidth={i % 5 === 0 ? 2.5 : 1}
              strokeLinecap="round"
            />
          );
        })}

        {/* needle pivot */}
        <circle cx={center} cy={center} r={6} fill="#111827" />

        {/* animated needle using framer-motion */}
        <motion.g
          style={{ transformOrigin: `${center}px ${center}px` }}
          animate={{ rotate: angle }}
          transition={{ type: "spring", stiffness: 200, damping: 20 }}
        >
          <line
            x1={center}
            y1={center}
            x2={center}
            y2={center - radius + 6}
            stroke="#111827"
            strokeWidth={3.5}
            strokeLinecap="round"
          />
        </motion.g>
      </svg>

      <div className="text-center mt-1 text-sm font-medium">
        <span className="text-gray-700">{val}%</span>
      </div>
    </div>
  );
}

/* Helper functions for arcs and coordinates */
function polarToCartesian(cx, cy, r, deg) {
  const rad = ((deg - 90) * Math.PI) / 180.0;
  return { x: cx + r * Math.cos(rad), y: cy + r * Math.sin(rad) };
}

function describeArc(cx, cy, r, startAngle, endAngle) {
  var start = polarToCartesian(cx, cy, r, endAngle);
  var end = polarToCartesian(cx, cy, r, startAngle);
  var largeArcFlag = endAngle - startAngle <= 180 ? "0" : "1";
  var d = ["M", start.x, start.y, "A", r, r, 0, largeArcFlag, 0, end.x, end.y].join(" ");
  return d;
}
