
import { type FetchParams, type PaginationMeta } from ".";

const API_BASE_URL = import.meta.env.VITE_BACKEND_URL;

export interface RecipientCreate {
  name: string;
  notes?: string | null;
}

export interface RecipientUpdate {
  name?: string | null;
  notes?: string | null;
}

export interface Recipient {
  id: string;
  user_id: string;
  name: string;
  notes: string | null;
}

export interface PaginatedRecipientsResponse {
  items: Recipient[];
  meta: PaginationMeta;
}

async function handleResponse<T>(response: Response): Promise<T> {
  if (!response.ok) {
    const error = await response.json().catch(() => ({ message: "An error occurred" }));
    throw new Error(error.message || `HTTP error! status: ${response.status}`);
  }
  if (response.status === 204) {
    return undefined as T;
  }
  return response.json();
}

export const recipientsApi = {
  async create(token: string, data: RecipientCreate): Promise<Recipient> {
    const response = await fetch(`${API_BASE_URL}/recipients`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        Authorization: `Bearer ${token}`,
      },
      credentials: "include",
      body: JSON.stringify(data),
    });
    return handleResponse<Recipient>(response);
  },

  async getAll(token: string, params?: FetchParams): Promise<PaginatedRecipientsResponse> {
    const queryParams = new URLSearchParams();
    if (params?.sort !== undefined) {
      queryParams.append("sort", params.sort);
    }
    if (params?.limit !== undefined) {
      queryParams.append("limit", params.limit.toString());
    }
    if (params?.page !== undefined) {
      queryParams.append("page", params.page.toString());
    }
    const queryString = queryParams.toString();
    const url = queryString
      ? `${API_BASE_URL}/recipients?${queryString}`
      : `${API_BASE_URL}/recipients`;

    const response = await fetch(url, {
      method: "GET",
      headers: {
        "Content-Type": "application/json",
        Authorization: `Bearer ${token}`,
      },
      credentials: "include",
    });
    return handleResponse<PaginatedRecipientsResponse>(response);
  },

  async getById(token: string, recipientId: string): Promise<Recipient> {
    const response = await fetch(`${API_BASE_URL}/recipients/${recipientId}`, {
      method: "GET",
      headers: {
        "Content-Type": "application/json",
        Authorization: `Bearer ${token}`,
      },
      credentials: "include",
    });
    return handleResponse<Recipient>(response);
  },

  async update(token: string, recipientId: string, data: RecipientUpdate): Promise<Recipient> {
    const response = await fetch(`${API_BASE_URL}/recipients/${recipientId}`, {
      method: "PATCH",
      headers: {
        "Content-Type": "application/json",
        Authorization: `Bearer ${token}`,
      },
      credentials: "include",
      body: JSON.stringify(data),
    });
    return handleResponse<Recipient>(response);
  },

  async delete(token: string, recipientId: string): Promise<void> {
    const response = await fetch(`${API_BASE_URL}/recipients/${recipientId}`, {
      method: "DELETE",
      headers: {
        "Content-Type": "application/json",
        Authorization: `Bearer ${token}`,
      },
      credentials: "include",
    });
    return handleResponse<void>(response);
  },
};
