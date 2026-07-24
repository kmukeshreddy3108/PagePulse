import axios from "axios";

const API_BASE_URL = (import.meta.env.VITE_API_BASE_URL || "http://127.0.0.1:8000").replace(
  /\/+$/,
  ""
);

const API_TIMEOUT = Number(import.meta.env.VITE_API_TIMEOUT) || 15000;

/**
 * Axios instance configured for Page Pulse API
 */
export const apiClient = axios.create({
  baseURL: API_BASE_URL,
  timeout: API_TIMEOUT,
  headers: {
    "Content-Type": "application/json",
  },
});

/**
 * Normalized error class for consistent UI error reporting
 */
export class AuditApiError extends Error {
  constructor(message, statusCode) {
    super(message);
    this.name = "AuditApiError";
    this.statusCode = statusCode;
  }
}

/**
 * Helper to convert Axios errors into normalized AuditApiError instances
 */
function handleAxiosError(error) {
  if (error.response) {
    // Server responded with a status code outside 2xx
    const status = error.response.status;
    const detail = error.response.data?.detail;

    if (detail) {
      return new AuditApiError(detail, status);
    }

    switch (status) {
      case 400:
        return new AuditApiError("Invalid request. Please check your URL.", 400);
      case 404:
        return new AuditApiError("Endpoint or resource not found.", 404);
      case 408:
        return new AuditApiError("Request timed out on the server.", 408);
      case 500:
        return new AuditApiError("Internal server error. Please try again later.", 500);
      default:
        return new AuditApiError(`Server error (${status}). Please try again.`, status);
    }
  } else if (error.code === "ECONNABORTED" || error.message.includes("timeout")) {
    // Request timeout
    return new AuditApiError("Request timed out. The server took too long to respond.", 408);
  } else if (error.request) {
    // Network failure or CORS error
    return new AuditApiError(
      "Could not reach the Page Pulse API. Please check your internet connection or backend URL.",
      0
    );
  } else {
    // Unexpected error during request setup
    return new AuditApiError(error.message || "An unexpected error occurred.", 0);
  }
}

/**
 * Calls POST /audit on the Page Pulse backend using Axios.
 * @param {string} url - Target URL to scan
 * @returns {Promise<Object>} Audit response metrics
 */
export async function runAudit(url) {
  try {
    const response = await apiClient.post("/audit", { url });
    return response.data;
  } catch (error) {
    throw handleAxiosError(error);
  }
}