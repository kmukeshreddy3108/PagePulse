import axios from "axios";

const rawApiUrl = import.meta.env.VITE_API_BASE_URL;

if (!rawApiUrl && import.meta.env.PROD) {
  console.warn(
    "[Page Pulse] VITE_API_BASE_URL is not defined in environment variables. Falling back to default backend URL."
  );
}

const API_BASE_URL = (rawApiUrl || "http://127.0.0.1:8000").replace(
  /\/+$/,
  ""
);

const API_TIMEOUT = Number(import.meta.env.VITE_API_TIMEOUT) || 45000;

/**
 * Axios instance configured for Page Pulse API
 */
const auditApi = axios.create({
  baseURL: API_BASE_URL,
  timeout: API_TIMEOUT,
  headers: {
    "Content-Type": "application/json",
    Accept: "application/json",
  },
});

/**
 * Performs a health audit scan for a given target URL.
 *
 * @param {string} url - Validated HTTP/HTTPS URL to scan
 * @returns {Promise<Object>} Backend audit result matching AuditResponse schema
 */
export const runAudit = async (url) => {
  try {
    const response = await auditApi.post("/api/audit", { url });
    return response.data;
  } catch (error) {
    if (error.code === "ECONNABORTED") {
      throw new Error(
        "The request timed out. The backend server might be starting up (cold start) or taking too long to audit the target site."
      );
    }

    if (error.response) {
      const detail = error.response.data?.detail;
      if (Array.isArray(detail)) {
        throw new Error(detail.map((err) => err.msg).join(", "));
      }
      throw new Error(
        detail || `Server returned error (${error.response.status})`
      );
    }

    if (error.request) {
      throw new Error(
        "Could not reach the Page Pulse API. Please check your internet connection or backend URL."
      );
    }

    throw new Error(error.message || "An unexpected error occurred.");
  }
};

export default auditApi;