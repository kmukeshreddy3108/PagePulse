export class AuditApiError extends Error {
  constructor(message, statusCode = null) {
    super(message);
    this.name = "AuditApiError";
    this.statusCode = statusCode;
  }
}

/**
 * Determines the target API endpoint.
 * Always targets the relative /api/audit route on the current server.
 */
function getEndpoint() {
  const envUrl = import.meta.env.VITE_API_BASE_URL;
  if (!envUrl) return "/api/audit";

  try {
    const urlObj = new URL(envUrl, window.location.origin);
    if (urlObj.origin !== window.location.origin) {
      return "/api/audit";
    }
    return `${urlObj.pathname.replace(/\/+$/, "")}/api/audit`;
  } catch {
    return "/api/audit";
  }
}

/**
 * Performs a health audit scan for a given target URL.
 *
 * @param {string} url - Validated HTTP/HTTPS URL to scan
 * @returns {Promise<Object>} Audit result object
 */
export const runAudit = async (url) => {
  const endpoint = getEndpoint();

  try {
    const controller = new AbortController();
    const timeoutId = setTimeout(() => controller.abort(), 45000);

    const response = await fetch(endpoint, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        Accept: "application/json",
      },
      body: JSON.stringify({ url }),
      signal: controller.signal,
    });

    clearTimeout(timeoutId);

    const data = await response.json().catch(() => ({}));

    if (!response.ok) {
      let msg = "Server error occurred.";
      if (Array.isArray(data.detail)) {
        msg = data.detail.map((err) => err.msg || err.message || JSON.stringify(err)).join(", ");
      } else if (typeof data.detail === "string") {
        msg = data.detail;
      } else if (data.detail?.message) {
        msg = data.detail.message;
      } else if (data.message) {
        msg = data.message;
      } else {
        msg = `Server returned status ${response.status}`;
      }
      throw new AuditApiError(msg, response.status);
    }

    return data;
  } catch (error) {
    if (error instanceof AuditApiError) {
      throw error;
    }
    if (error.name === "AbortError") {
      throw new AuditApiError(
        "The request timed out while auditing the target site.",
        408
      );
    }
    throw new AuditApiError(
      error.message || "Could not reach the Page Pulse API.",
      0
    );
  }
};

export default { runAudit };