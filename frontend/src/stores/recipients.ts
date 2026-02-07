import { ref, computed } from "vue";
import { defineStore } from "pinia";

import { type FetchParams } from "@/api";
import {
  recipientsApi,
  type Recipient,
  type RecipientCreate,
  type RecipientUpdate,
  type PaginationMeta,
} from "@/api/recipients";

export const useRecipientsStore = defineStore("recipients", () => {
  // State
  const recipients = ref<Recipient[]>([]);
  const paginationMeta = ref<PaginationMeta | null>(null);


  // Actions

  /**
   * Fetch all recipients for the current user
   */
  async function fetchAll(
    token: string,
    params?: FetchParams,
  ): Promise<void> {
    const response = await recipientsApi.getAll(token, params);
    recipients.value = response.items;
    paginationMeta.value = response.meta;
  }

  /**
   * Fetch a specific recipient by ID
   */
  async function fetchById(token: string, recipientId: string): Promise<Recipient> {
    const recipient = await recipientsApi.getById(token, recipientId);

    const index = recipients.value.findIndex((r) => r.id === recipientId);
    if (index !== -1) {
      recipients.value[index] = recipient;
    } else {
      recipients.value.push(recipient);
    }

    return recipient;
  }

  /**
   * Create a new recipient
   */
  async function create(token: string, data: RecipientCreate): Promise<Recipient> {
    const newRecipient = await recipientsApi.create(token, data);
    recipients.value.push(newRecipient);
    return newRecipient;
  }

  /**
   * Update an existing recipient
   */
  async function update(
    token: string,
    recipientId: string,
    data: RecipientUpdate,
  ): Promise<Recipient> {
    const updatedRecipient = await recipientsApi.update(token, recipientId, data);

    const index = recipients.value.findIndex((r) => r.id === recipientId);
    if (index !== -1) {
      recipients.value[index] = updatedRecipient;
    }

    return updatedRecipient;
  }

  /**
   * Delete a recipient
   */
  async function remove(token: string, recipientId: string): Promise<void> {
    await recipientsApi.delete(token, recipientId);
    recipients.value = recipients.value.filter((r) => r.id !== recipientId);
  }

  /**
   * Clear all recipients from state
   */
  function clearRecipients(): void {
    recipients.value = [];
  }

  return {
    // State
    recipients,
    paginationMeta,

    // Actions
    fetchAll,
    fetchById,
    create,
    update,
    remove,
    clearRecipients,
  };
});
