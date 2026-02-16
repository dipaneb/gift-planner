import { ref } from "vue";

import { type FetchParams } from "@/api";
import { useRecipientsStore } from "@/stores/recipients";
import { useAuthStore } from "@/stores/auth";
import type { RecipientCreate, RecipientUpdate } from "@/api/recipients";

/**
 * Composable for recipients actions with component-scoped loading and error states.
 * Uses the recipients store for global state management but provides local UI state.
 *
 * This separates concerns:
 * - Store: Global state (recipients list)
 * - Composable: Local UI state (loading, error)
 */
export function useRecipients() {
  const recipientsStore = useRecipientsStore();

  const loading = ref(false);
  const error = ref<string | null>(null);

  /**
   * Fetch recipients (paginated)
   */
  async function fetchPaginated(params?: FetchParams): Promise<boolean> {
    loading.value = true;
    error.value = null;

    try {
      await recipientsStore.fetchPaginated(params);
      return true;
    } catch (err) {
      error.value = err instanceof Error ? err.message : "Failed to fetch recipients";
      return false;
    } finally {
      loading.value = false;
    }
  }

  /**
   * Fetch every recipient (pages through the backend automatically).
   * Results available via recipientsStore.allRecipients.
   */
  async function fetchAll(): Promise<boolean> {
    loading.value = true;
    error.value = null;

    try {
      await recipientsStore.fetchAll();
      return true;
    } catch (err) {
      error.value = err instanceof Error ? err.message : "Failed to fetch all recipients";
      return false;
    } finally {
      loading.value = false;
    }
  }

  /**
   * Fetch a specific recipient by ID
   */
  async function fetchById(recipientId: string): Promise<boolean> {
    loading.value = true;
    error.value = null;

    try {
      await recipientsStore.fetchById(recipientId);
      return true;
    } catch (err) {
      error.value = err instanceof Error ? err.message : "Failed to fetch recipient";
      return false;
    } finally {
      loading.value = false;
    }
  }

  /**
   * Create a new recipient
   */
  async function createRecipient(data: RecipientCreate): Promise<boolean> {
    loading.value = true;
    error.value = null;

    try {
      await recipientsStore.create(data);
      return true;
    } catch (err) {
      error.value = err instanceof Error ? err.message : "Failed to create recipient";
      return false;
    } finally {
      loading.value = false;
    }
  }

  /**
   * Update an existing recipient
   */
  async function updateRecipient(recipientId: string, data: RecipientUpdate): Promise<boolean> {
    loading.value = true;
    error.value = null;

    try {
      await recipientsStore.update(recipientId, data);
      return true;
    } catch (err) {
      error.value = err instanceof Error ? err.message : "Failed to update recipient";
      return false;
    } finally {
      loading.value = false;
    }
  }

  /**
   * Delete a recipient
   */
  async function deleteRecipient(recipientId: string): Promise<boolean> {
    loading.value = true;
    error.value = null;

    try {
      await recipientsStore.remove(recipientId);
      return true;
    } catch (err) {
      error.value = err instanceof Error ? err.message : "Failed to delete recipient";
      return false;
    } finally {
      loading.value = false;
    }
  }

  return {
    loading,
    error,
    fetchPaginated,
    fetchAll,
    fetchById,
    createRecipient,
    updateRecipient,
    deleteRecipient,
  };
}
