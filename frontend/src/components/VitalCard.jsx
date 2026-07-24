export function NumberVital({ label, value, unit, tone = "neutral", span2 = false }) {
  return (
    <div className={`vital-card ${span2 ? "span-2" : ""}`}>
      <div className="vital-label-row">
        <span className="vital-label">{label}</span>
        <span className={`vital-indicator ${tone}`} aria-hidden="true" />
      </div>
      <div className={`vital-value ${tone !== "neutral" ? `value-${tone}` : ""}`}>
        {value}
        {unit ? <span className="vital-unit">{unit}</span> : null}
      </div>
    </div>
  );
}

export function TextVital({ label, value, span2 = false }) {
  const hasValue = Boolean(value && value.trim());
  return (
    <div className={`vital-card ${span2 ? "span-2" : ""}`}>
      <div className="vital-label-row">
        <span className="vital-label">{label}</span>
        <span className="vital-indicator neutral" aria-hidden="true" />
      </div>
      <div className={`vital-text-value ${hasValue ? "" : "empty"}`}>
        {hasValue ? value : "Not found on this page"}
      </div>
    </div>
  );
}
