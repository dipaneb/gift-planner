import { type FetchParams } from ".";
import type { PaginationMeta } from "@/api/index";

const API_BASE_URL = import.meta.env.VITE_BACKEND_URL;

export type GiftStatus =
  | "idee"
  | "achete"
  | "commande"
  | "en_cours_livraison"
  | "livre"
  | "recupere"
  | "emballe"
  | "offert";

export const GIFT_STATUS_LABELS: Record<GiftStatus, string> = {
  idee: "Idée",
  achete: "Acheté",
  commande: "Commandé",
  en_cours_livraison: "En livraison",
  livre: "Livré",
  recupere: "Récupéré",
  emballe: "Emballé",
  offert: "Offert",
};

export const GIFT_STATUS_COLORS: Record<GiftStatus, { bg: string; text: string; border: string }> =
  {
    idee: { bg: "#eff6ff", text: "#1d4ed8", border: "#bfdbfe" },
    achete: { bg: "#fefce8", text: "#a16207", border: "#fde68a" },
    commande: { bg: "#fff7ed", text: "#c2410c", border: "#fed7aa" },
    en_cours_livraison: { bg: "#fdf4ff", text: "#9333ea", border: "#e9d5ff" },
    livre: { bg: "#f0fdf4", text: "#15803d", border: "#bbf7d0" },
    recupere: { bg: "#ecfeff", text: "#0e7490", border: "#a5f3fc" },
    emballe: { bg: "#fdf2f8", text: "#be185d", border: "#fbcfe8" },
    offert: { bg: "#f0f9ff", text: "#0369a1", border: "#bae6fd" },
  };

export interface GiftCreate {
  name: string;
  url?: string | null;
  price?: number | null;
  status?: GiftStatus;
  quantity?: number;
  recipient_ids?: string[];
}

export interface GiftUpdate {
  name?: string | null;
  url?: string | null;
  price?: number | null;
  status?: GiftStatus | null;
  quantity?: number | null;
  recipient_ids?: string[] | null;
}

export interface Gift {
  id: string;
  user_id: string;
  name: string;
  url: string | null;
  price: string | null;
  status: GiftStatus;
  quantity: number;
  recipient_ids: string[];
}

export interface PaginatedGiftsResponse {
  items: Gift[];
  meta: PaginationMeta;
}

async function handleResponse<T>(response: Response): Promise<T> {
  if (!response.ok) {
    const error = await response.json().catch(() => ({ message: "An error occurred" }));
    throw new Error(error.detail || error.message || `HTTP error! status: ${response.status}`);
  }
  if (response.status === 204) {
    return undefined as T;
  }
  return response.json();
}

export const giftsApi = {
  async create(token: string, data: GiftCreate): Promise<Gift> {
    const response = await fetch(`${API_BASE_URL}/gifts`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        Authorization: `Bearer ${token}`,
      },
      credentials: "include",
      body: JSON.stringify(data),
    });
    return handleResponse<Gift>(response);
  },

  async getAll(token: string, params?: FetchParams): Promise<PaginatedGiftsResponse> {
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
    const url = queryString ? `${API_BASE_URL}/gifts?${queryString}` : `${API_BASE_URL}/gifts`;

    const response = await fetch(url, {
      method: "GET",
      headers: {
        "Content-Type": "application/json",
        Authorization: `Bearer ${token}`,
      },
      credentials: "include",
    });
    return handleResponse<PaginatedGiftsResponse>(response);
  },

  async getById(token: string, giftId: string): Promise<Gift> {
    const response = await fetch(`${API_BASE_URL}/gifts/${giftId}`, {
      method: "GET",
      headers: {
        "Content-Type": "application/json",
        Authorization: `Bearer ${token}`,
      },
      credentials: "include",
    });
    return handleResponse<Gift>(response);
  },

  async update(token: string, giftId: string, data: GiftUpdate): Promise<Gift> {
    const response = await fetch(`${API_BASE_URL}/gifts/${giftId}`, {
      method: "PATCH",
      headers: {
        "Content-Type": "application/json",
        Authorization: `Bearer ${token}`,
      },
      credentials: "include",
      body: JSON.stringify(data),
    });
    return handleResponse<Gift>(response);
  },

  async delete(token: string, giftId: string): Promise<void> {
    const response = await fetch(`${API_BASE_URL}/gifts/${giftId}`, {
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
