import { visitsApi } from "@/api/visits";

// URL to put on the CV: https://<site>/?ref=cv
const REF_QUERY_PARAM = "ref";
const CV_REF = "cv";

const VISITOR_ID_KEY = "visitor_id";
const VISIT_RECORDED_KEY = "visit_recorded";

// Storage can be unavailable (private browsing, blocked site data): tracking must never break the app.
function readStorage(storage: () => Storage, key: string): string | null {
  try {
    return storage().getItem(key);
  } catch {
    return null;
  }
}

function writeStorage(storage: () => Storage, key: string, value: string) {
  try {
    storage().setItem(key, value);
  } catch {
    // ignore
  }
}

function getVisitorId(): string {
  let visitorId = readStorage(() => localStorage, VISITOR_ID_KEY);
  if (!visitorId) {
    visitorId = crypto.randomUUID();
    writeStorage(() => localStorage, VISITOR_ID_KEY, visitorId);
  }
  return visitorId;
}

let landedFromCv = false;

/**
 * Read `?ref=cv` from the landing URL, then remove it so it isn't carried into redirects,
 * shared or bookmarked. Must run before the router is created, since the router reads the URL.
 */
export function captureLandingRef() {
  const url = new URL(window.location.href);
  landedFromCv = url.searchParams.get(REF_QUERY_PARAM) === CV_REF;

  if (url.searchParams.has(REF_QUERY_PARAM)) {
    url.searchParams.delete(REF_QUERY_PARAM);
    window.history.replaceState(window.history.state, "", url);
  }
}

/** Record one visit per browser session, flagged when the visitor came from the CV link. */
export async function trackVisit() {
  if (readStorage(() => sessionStorage, VISIT_RECORDED_KEY)) return;
  writeStorage(() => sessionStorage, VISIT_RECORDED_KEY, "1");

  try {
    await visitsApi.recordVisit({ from_cv: landedFromCv, visitor_id: getVisitorId() });
  } catch {
    // Analytics only: never surface an error to the visitor.
  }
}
