import api, { type FetchParams } from ".";
import type { PaginationMeta } from "@/api/index";

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

export const giftsApi = {
  async create(data: GiftCreate): Promise<Gift> {
    const response = await api.post<Gift>("/gifts", data);
    return response.data;
  },

  async getAll(params?: FetchParams): Promise<PaginatedGiftsResponse> {
    const response = await api.get<PaginatedGiftsResponse>("/gifts", {
      params: {
        sort: params?.sort,
        limit: params?.limit,
        page: params?.page,
      },
    });
    return response.data;
  },

  async getById(giftId: string): Promise<Gift> {
    const response = await api.get<Gift>(`/gifts/${giftId}`);
    return response.data;
  },

  async update(giftId: string, data: GiftUpdate): Promise<Gift> {
    const response = await api.patch<Gift>(`/gifts/${giftId}`, data);
    return response.data;
  },

  async delete(giftId: string): Promise<void> {
    await api.delete(`/gifts/${giftId}`);
  },
};
