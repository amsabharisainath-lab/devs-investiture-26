const API_BASE_URL =
  import.meta.env.VITE_API_BASE_URL ||
  "http://localhost:8000/api/v1";

export { API_BASE_URL };

async function apiRequest<T>(
  path: string,
  options: RequestInit = {},
): Promise<T> {
  const token = localStorage.getItem("devs_access_token");

  const headers = new Headers(options.headers);

  if (!headers.has("Content-Type") && options.body) {
    headers.set("Content-Type", "application/json");
  }

  if (token) {
    headers.set("Authorization", `Bearer ${token}`);
  }

  const response = await fetch(`${API_BASE_URL}${path}`, {
    ...options,
    headers,
  });

  const contentType = response.headers.get("content-type");

  const data = contentType?.includes("application/json")
    ? await response.json()
    : null;

  if (!response.ok) {
    const message =
      data?.detail ||
      data?.message ||
      `Request failed with status ${response.status}`;

    throw new Error(message);
  }

  return data as T;
}

/* =========================
   TYPES
========================= */

export interface SessionUser {
  id: number;
  email: string;
  name: string;
  role: string;
  roll_no: string | null;
  department: string | null;
  year: number | null;
  is_active: boolean;
}

export interface MeResponse {
  authenticated: boolean;
  user: SessionUser | null;
}

export interface QRCodeResponse {
  action: "ENTRY" | "EXIT";
  token: string;
  expires_at: string;
}

export interface RegistrationResponse {
  id: number;
  event_id: number;
  user_id: number;
  status: string;
  registered_at: string;
  entry_qr: QRCodeResponse;
}

/* =========================
   GOOGLE OAUTH
========================= */

export function getGoogleOAuthURL(): string {
  return `${API_BASE_URL}/auth/google/start`;
}

/* =========================
   AUTH
========================= */

export async function getMe(): Promise<MeResponse> {
  return apiRequest<MeResponse>("/auth/me");
}

/* =========================
   PROFILE
========================= */

export async function completeProfile(payload: {
  name: string;
  roll_no: string;
  department: string;
  year: number;
}): Promise<SessionUser> {
  return apiRequest<SessionUser>("/auth/profile", {
    method: "PUT",
    body: JSON.stringify(payload),
  });
}

/* =========================
   EVENT REGISTRATION
========================= */

export async function registerForEvent(
  eventId: number,
): Promise<RegistrationResponse> {
  return apiRequest<RegistrationResponse>(
    `/events/${eventId}/registration`,
    {
      method: "POST",
    },
  );
}

/* =========================
   ENTRY QR
========================= */

export async function getEntryQR(
  eventId: number,
): Promise<{ entry_qr: QRCodeResponse }> {
  return apiRequest<{ entry_qr: QRCodeResponse }>(
    `/events/${eventId}/registration/entry-qr`,
    {
      method: "POST",
    },
  );
}