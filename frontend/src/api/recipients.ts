import api, { type FetchParams, type PaginationMeta } from ".";

export interface RecipientCreate {
  name: string;
  notes?: string | null;
  gift_ids?: string[];
}

export interface RecipientUpdate {
  name?: string | null;
  notes?: string | null;
  gift_ids?: string[] | null;
}

export interface Recipient {
  id: string;
  user_id: string;
  name: string;
  notes: string | null;
  gift_ids: string[];
}

export interface PaginatedRecipientsResponse {
  items: Recipient[];
  meta: PaginationMeta;
}

export const recipientsApi = {
  async create(data: RecipientCreate): Promise<Recipient> {
    const response = await api.post<Recipient>("/recipients", data);
    return response.data;
  },

  async getAll(params?: FetchParams): Promise<PaginatedRecipientsResponse> {
    const response = await api.get<PaginatedRecipientsResponse>("/recipients", {
      params: {
        sort: params?.sort,
        limit: params?.limit,
        page: params?.page,
      },
    });
    return response.data;
  },

  async getById(recipientId: string): Promise<Recipient> {
    const response = await api.get<Recipient>(`/recipients/${recipientId}`);
    return response.data;
  },

  async update(recipientId: string, data: RecipientUpdate): Promise<Recipient> {
    const response = await api.patch<Recipient>(`/recipients/${recipientId}`, data);
    return response.data;
  },

  async delete(recipientId: string): Promise<void> {
    await api.delete(`/recipients/${recipientId}`);
  },
};
