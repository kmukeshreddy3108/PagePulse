const CODE_LABELS = {
  400: "Invalid URL",
  408: "Timeout",
  415: "Unsupported content",
  500: "Server error",
  0: "Connection error",
};

export default function ErrorBanner({ message, statusCode }) {
  const label = CODE_LABELS[statusCode] || "Scan failed";

  return (
    <div className="error-banner" role="alert">
      <svg
        className="error-icon"
        width="20"
        height="20"
        viewBox="0 0 24 24"
        fill="none"
        aria-hidden="true"
      >
        <circle cx="12" cy="12" r="9" stroke="currentColor" strokeWidth="2" />
        <path d="M12 8V13" stroke="currentColor" strokeWidth="2" strokeLinecap="round" />
        <circle cx="12" cy="16.2" r="1" fill="currentColor" />
      </svg>
      <div>
        <p className="error-title">
          {label}
          {statusCode ? <span className="error-code"> · {statusCode}</span> : null}
        </p>
        <p className="error-detail">{message}</p>
      </div>
    </div>
  );
}
