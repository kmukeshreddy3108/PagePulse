/**
 * Lightweight client-side check so obviously malformed input is caught
 * before a network round-trip. The backend remains the source of truth
 * for validation.
 */
export function looksLikeValidUrl(value) {
  const trimmed = value.trim();
  if (!trimmed) return false;

  let parsed;
  try {
    parsed = new URL(trimmed);
  } catch {
    return false;
  }

  if (!["http:", "https:"].includes(parsed.protocol)) return false;
  if (!parsed.hostname) return false;
  if (!parsed.hostname.includes(".") && parsed.hostname !== "localhost") return false;

  return true;
}
