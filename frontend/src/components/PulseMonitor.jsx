const STATUS_COPY = {
  idle: "standing by",
  loading: "scanning…",
  ok: "healthy",
  warn: "needs attention",
  fail: "unreachable",
};

// A single waveform unit, repeated twice back to back and slid via CSS
// so it scrolls seamlessly regardless of container width.
function WaveformUnit({ color, spiky }) {
  const flat = "M0 44 H60 L72 44";
  const beat = spiky
    ? "L84 14 L96 74 L108 30 L120 44"
    : "L84 34 L96 54 L108 40 L120 44";
  const rest = "H400";
  return (
    <svg viewBox="0 0 400 88" preserveAspectRatio="none">
      <path
        d={`${flat}${beat}${rest}`}
        fill="none"
        stroke={color}
        strokeWidth="2.5"
        strokeLinecap="round"
        strokeLinejoin="round"
      />
    </svg>
  );
}

const COLORS = {
  idle: "#5b6478",
  loading: "#35e1a1",
  ok: "#35e1a1",
  warn: "#f5a623",
  fail: "#ff5c5c",
};

export default function PulseMonitor({ state, targetLabel }) {
  const color = COLORS[state] || COLORS.idle;
  const isAnimated = state === "idle" || state === "loading";
  const speedClass = state === "loading" ? "speed-loading" : "speed-idle";
  const spiky = state === "warn" || state === "fail";

  return (
    <div className="pulse-monitor" role="status" aria-live="polite">
      <div className="pulse-monitor-readout">
        <span>{targetLabel || "no target"}</span>
        <span className={`status-word ${state}`}>{STATUS_COPY[state]}</span>
      </div>
      <div className="pulse-monitor-canvas">
        <div className={`pulse-track ${isAnimated ? `animate ${speedClass}` : ""}`}>
          <WaveformUnit color={color} spiky={spiky} />
          <WaveformUnit color={color} spiky={spiky} />
        </div>
      </div>
    </div>
  );
}
