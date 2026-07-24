import { useState } from "react";
import Header from "./components/Header.jsx";
import PulseMonitor from "./components/PulseMonitor.jsx";
import ScanForm from "./components/ScanForm.jsx";
import ResultsPanel from "./components/ResultsPanel.jsx";
import ErrorBanner from "./components/ErrorBanner.jsx";
import EmptyState from "./components/EmptyState.jsx";
import Footer from "./components/Footer.jsx";
import { runAudit, AuditApiError } from "./api/auditApi.js";

function monitorState({ isLoading, error, result }) {
  if (isLoading) return "loading";
  if (error) return "fail";
  if (result) {
    if (result.status >= 200 && result.status < 300) return "ok";
    if (result.status >= 300) return "warn";
  }
  return "idle";
}

export default function App() {
  const [targetUrl, setTargetUrl] = useState("");
  const [isLoading, setIsLoading] = useState(false);
  const [result, setResult] = useState(null);
  const [error, setError] = useState(null);

  async function handleScan(url) {
    setIsLoading(true);
    setError(null);
    setResult(null);
    setTargetUrl(url);

    try {
      const data = await runAudit(url);
      setResult(data);
    } catch (err) {
      if (err instanceof AuditApiError) {
        setError({ message: err.message, statusCode: err.statusCode });
      } else {
        setError({ message: "Something unexpected happened. Please try again.", statusCode: null });
      }
    } finally {
      setIsLoading(false);
    }
  }

  const state = monitorState({ isLoading, error, result });
  const hasRun = Boolean(result || error || isLoading);

  return (
    <div className="app-shell">
      <Header />

      <main className="main-content">
        <section className="hero">
          <p className="hero-eyebrow">Instant webpage diagnostics</p>
          <h1 className="hero-heading">Give any page a check-up.</h1>
          <p className="hero-sub">
            Page Pulse fetches a URL and reads its vitals: status, response time,
            heading structure, missing image alt text, and word count, in a
            single scan.
          </p>

          <ScanForm onSubmit={handleScan} isLoading={isLoading} />

          <PulseMonitor state={state} targetLabel={targetUrl || null} />
        </section>

        {error && <ErrorBanner message={error.message} statusCode={error.statusCode} />}

        {result && !error && <ResultsPanel result={result} targetUrl={targetUrl} />}

        {!hasRun && <EmptyState />}
      </main>

      <Footer />
    </div>
  );
}