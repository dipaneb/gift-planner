import { ref } from "vue";

import { type FetchParams } from "@/api";
import { getErrorMessage } from "./utils";
import { useGiftsStore } from "@/stores/gifts";
import { useAuthStore } from "@/stores/auth";
import type { GiftCreate, GiftUpdate } from "@/api/gifts";

/**
 * Composable for gifts actions with component-scoped loading and error states.
 * Uses the gifts store for global state management but provides local UI state.
 *
 * This separates concerns:
 * - Store: Global state (gifts list)
 * - Composable: Local UI state (loading, error)
 */
export function useGifts() {
  const giftsStore = useGiftsStore();
  const authStore = useAuthStore();

  const loading = ref(false);
  const error = ref<string | null>(null);

  /**
   * Fetch gifts (paginated)
   */
  async function fetchPaginated(params?: FetchParams): Promise<boolean> {
    loading.value = true;
    error.value = null;

    try {
      await giftsStore.fetchPaginated(params);
      return true;
    } catch (err) {
      error.value = getErrorMessage(err, "Failed to fetch gifts");
      return false;
    } finally {
      loading.value = false;
    }
  }

  /**
   * Fetch every gift (pages through the backend automatically).
   * Results available via giftsStore.allGifts.
   */
  async function fetchAll(): Promise<boolean> {
    loading.value = true;
    error.value = null;

    try {
      await giftsStore.fetchAll();
      return true;
    } catch (err) {
      error.value = getErrorMessage(err, "Failed to fetch all gifts");
      return false;
    } finally {
      loading.value = false;
    }
  }

  /**
   * Fetch a specific gift by ID
   */
  async function fetchById(giftId: string): Promise<boolean> {
    loading.value = true;
    error.value = null;

    try {
      await giftsStore.fetchById(giftId);
      return true;
    } catch (err) {
      error.value = getErrorMessage(err, "Failed to fetch gift");
      return false;
    } finally {
      loading.value = false;
    }
  }

  /**
   * Create a new gift
   */
  async function createGift(data: GiftCreate): Promise<boolean> {
    loading.value = true;
    error.value = null;

    try {
      await giftsStore.create(data);
      await authStore.refreshUser();
      return true;
    } catch (err) {
      error.value = getErrorMessage(err, "Failed to create gift");
      return false;
    } finally {
      loading.value = false;
    }
  }

  /**
   * Update an existing gift
   */
  async function updateGift(giftId: string, data: GiftUpdate): Promise<boolean> {
    loading.value = true;
    error.value = null;

    try {
      await giftsStore.update(giftId, data);
      await authStore.refreshUser();
      return true;
    } catch (err) {
      error.value = getErrorMessage(err, "Failed to update gift");
      return false;
    } finally {
      loading.value = false;
    }
  }

  /**
   * Quick-update gift status only
   */
  async function updateGiftStatus(
    giftId: string,
    status: GiftUpdate["status"],
  ): Promise<boolean> {
    return updateGift(giftId, { status });
  }

  /**
   * Delete a gift
   */
  async function deleteGift(giftId: string): Promise<boolean> {
    loading.value = true;
    error.value = null;

    try {
      await giftsStore.remove(giftId);
      await authStore.refreshUser();
      return true;
    } catch (err) {
      error.value = getErrorMessage(err, "Failed to delete gift");
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
    createGift,
    updateGift,
    updateGiftStatus,
    deleteGift,
  };
}
