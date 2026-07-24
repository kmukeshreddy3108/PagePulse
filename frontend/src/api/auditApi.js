const API_BASE_URL = (import.meta.env.VITE_API_BASE_URL || "http://127.0.0.1:8000").replace(
  /\/+$/,
  ""
);

/**
 * A normalized error shape thrown by runAudit so components never have to
 * branch on fetch failures vs. API error responses.
 */
export class AuditApiError extends Error {
  constructor(message, statusCode) {
    super(message);
    this.name = "AuditApiError";
    this.statusCode = statusCode;
  }
}

/**
 * Calls POST /audit on the Page Pulse backend.
 * Throws AuditApiError with the backend's `detail` message on any failure.
 */
export async function runAudit(url) {
  let response;
  try {
    response = await fetch(`${API_BASE_URL}/audit`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ url }),
    });
  } catch (networkErr) {
    throw new AuditApiError(
      "Could not reach the Page Pulse API. Check your connection and try again.",
      0
    );
  }

  let payload = null;
  try {
    payload = await response.json();
  } catch {
    // Non-JSON body; fall through to generic handling below.
  }

  if (!response.ok) {
    const detail = payload?.detail || "The audit could not be completed.";
    throw new AuditApiError(detail, response.status);
  }

  return payload;
}
