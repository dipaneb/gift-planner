import axios from 'axios'

/**
 * Extract a user-facing, translated error message.
 *
 * Raw backend `detail` strings are **never** returned — only the translated
 * fallback or a status-code-specific i18n string from `statusMap`.
 *
 * @param err        The caught error
 * @param fallback   Generic translated fallback (always safe to show)
 * @param statusMap  Optional mapping of HTTP status codes to translated strings
 */
export function getErrorMessage(
  err: unknown,
  fallback: string,
  statusMap?: Record<number, string>,
): string {
  if (axios.isAxiosError(err) && err.response && statusMap) {
    const mapped = statusMap[err.response.status]
    if (mapped) return mapped
  }
  return fallback
}
