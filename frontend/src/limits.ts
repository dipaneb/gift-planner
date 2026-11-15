// Keep in sync with backend/src/core/limits.py (the backend enforces them, these give clear messages).
export const MAX_AMOUNT = 1_000_000;
export const MAX_QUANTITY = 1000;
// Gift links are rendered as <a href>: only web links, never "javascript:" or "data:".
export const WEB_URL_PROTOCOL = /^https?$/;
