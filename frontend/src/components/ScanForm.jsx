import { useState } from "react";
import { looksLikeValidUrl } from "../utils/validateUrl.js";

export default function ScanForm({ onSubmit, isLoading }) {
  const [value, setValue] = useState("");
  const [touched, setTouched] = useState(false);

  const isEmpty = value.trim() === "";
  const isInvalid = touched && !isEmpty && !looksLikeValidUrl(value);

  function handleSubmit(e) {
    e.preventDefault();
    setTouched(true);
    if (!looksLikeValidUrl(value)) return;
    onSubmit(value.trim());
  }

  return (
    <form className="scan-form" onSubmit={handleSubmit} noValidate>
      <div className="scan-row">
        <div className={`scan-input-wrap ${isInvalid ? "has-error" : ""}`}>
          <svg
            className="scan-input-icon"
            width="16"
            height="16"
            viewBox="0 0 24 24"
            fill="none"
            aria-hidden="true"
          >
            <circle cx="11" cy="11" r="7" stroke="currentColor" strokeWidth="2" />
            <path d="M21 21L16.65 16.65" stroke="currentColor" strokeWidth="2" strokeLinecap="round" />
          </svg>
          <input
            className="scan-input"
            type="text"
            inputMode="url"
            autoComplete="off"
            spellCheck="false"
            placeholder="https://example.com"
            aria-label="Webpage URL to audit"
            value={value}
            onChange={(e) => setValue(e.target.value)}
            onBlur={() => setTouched(true)}
          />
        </div>
        <button className="scan-button" type="submit" disabled={isLoading}>
          {isLoading ? "Scanning…" : "Run scan"}
        </button>
      </div>
      <p className="field-hint" role="alert">
        {isInvalid ? "Enter a full URL starting with http:// or https://." : ""}
      </p>
    </form>
  );
}
