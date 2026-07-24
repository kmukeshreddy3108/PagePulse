import { NumberVital, TextVital } from "./VitalCard.jsx";

function statusTone(status) {
  if (status >= 200 && status < 300) return "ok";
  if (status >= 300 && status < 500) return "warn";
  return "fail";
}

function altTone(missing) {
  if (missing === 0) return "ok";
  if (missing <= 5) return "warn";
  return "fail";
}

function speedTone(seconds) {
  if (seconds <= 1) return "ok";
  if (seconds <= 3) return "warn";
  return "fail";
}

export default function ResultsPanel({ result, targetUrl }) {
  return (
    <section className="results-section">
      <div className="results-heading-row">
        <h2 className="results-heading">Vitals</h2>
        <span className="results-target">{targetUrl}</span>
      </div>
      <div className="vitals-grid">
        <NumberVital
          label="HTTP status"
          value={result.status}
          tone={statusTone(result.status)}
        />
        <NumberVital
          label="Response time"
          value={result.response_time.toFixed(3)}
          unit="s"
          tone={speedTone(result.response_time)}
        />
        <NumberVital label="H1 headings" value={result.h1_count} tone="neutral" />
        <NumberVital
          label="Images missing alt"
          value={result.images_missing_alt}
          tone={altTone(result.images_missing_alt)}
        />
        <NumberVital label="Word count" value={result.word_count} tone="neutral" />
        <TextVital label="Page title" value={result.page_title} />
        <TextVital label="Meta description" value={result.meta_description} span2 />
      </div>
    </section>
  );
}
