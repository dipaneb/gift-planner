import { ref, computed } from "vue";
import { defineStore } from "pinia";

import { type FetchParams, type PaginationMeta, } from "@/api";
import {
  recipientsApi,
  type Recipient,
  type RecipientCreate,
  type RecipientUpdate,
} from "@/api/recipients";

export const useRecipientsStore = defineStore("recipients", () => {
  // State
  const paginatedRecipients = ref<Recipient[]>([]);
  const allRecipients = ref<Recipient[]>([]);
  const paginationMeta = ref<PaginationMeta | null>(null);


  // Actions

  /**
   * Fetch recipients for the current user (paginated)
   */
  async function fetchPaginated(params?: FetchParams): Promise<void> {
    const response = await recipientsApi.getAll(params);
    paginatedRecipients.value = response.items;
    paginationMeta.value = response.meta;
  }

  /**
   * Fetch every recipient by paging through the backend.
   * Results are stored in `allRecipients` (separate from `paginatedRecipients`).
   */
  async function fetchAll(): Promise<void> {
    const pageSize = 100;
    let page = 1;
    let all: Recipient[] = [];
    let totalPages = 1;

    do {
      const response = await recipientsApi.getAll({ page, limit: pageSize });
      all = all.concat(response.items);
      totalPages = response.meta.totalPages;
      page++;
    } while (page <= totalPages);

    allRecipients.value = all;
  }

  /**
   * Fetch a specific recipient by ID
   */
  async function fetchById(recipientId: string): Promise<Recipient> {
    const recipient = await recipientsApi.getById(recipientId);

    const index = paginatedRecipients.value.findIndex((r) => r.id === recipientId);
    if (index !== -1) {
      paginatedRecipients.value[index] = recipient;
    } else {
      paginatedRecipients.value.push(recipient);
    }

    return recipient;
  }

  /**
   * Create a new recipient
   */
  async function create(data: RecipientCreate): Promise<Recipient> {
    const newRecipient = await recipientsApi.create(data);
    paginatedRecipients.value.push(newRecipient);
    return newRecipient;
  }

  /**
   * Update an existing recipient
   */
  async function update(
    recipientId: string,
    data: RecipientUpdate,
  ): Promise<Recipient> {
    const updatedRecipient = await recipientsApi.update(recipientId, data);

    const index = paginatedRecipients.value.findIndex((r) => r.id === recipientId);
    if (index !== -1) {
      paginatedRecipients.value[index] = updatedRecipient;
    }

    return updatedRecipient;
  }

  /**
   * Delete a recipient
   */
  async function remove(recipientId: string): Promise<void> {
    await recipientsApi.delete(recipientId);
    paginatedRecipients.value = paginatedRecipients.value.filter((r) => r.id !== recipientId);
  }

  /**
   * Clear all recipients from state
   */
  function clearRecipients(): void {
    paginatedRecipients.value = [];
  }

  return {
    // State
    paginatedRecipients,
    allRecipients,
    paginationMeta,

    // Actions
    fetchPaginated,
    fetchAll,
    fetchById,
    create,
    update,
    remove,
    clearRecipients,
  };
});
