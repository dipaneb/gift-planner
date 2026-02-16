import { ref } from "vue";
import { defineStore } from "pinia";

import { type FetchParams } from "@/api";
import {
  giftsApi,
  type Gift,
  type GiftCreate,
  type GiftUpdate,
  type PaginatedGiftsResponse,
} from "@/api/gifts";
import type { PaginationMeta } from "@/api/index";

export const useGiftsStore = defineStore("gifts", () => {
  // State
  const paginatedGifts = ref<Gift[]>([]);
  const allGifts = ref<Gift[]>([]);
  const paginationMeta = ref<PaginationMeta | null>(null);

  // Actions

  /**
   * Fetch gifts for the current user (paginated)
   */
  async function fetchPaginated(params?: FetchParams): Promise<void> {
    const response = await giftsApi.getAll(params);
    paginatedGifts.value = response.items;
    paginationMeta.value = response.meta;
  }

  /**
   * Fetch every gift by paging through the backend.
   * Results are stored in `allGifts` (separate from `paginatedGifts`).
   */
  async function fetchAll(): Promise<void> {
    const pageSize = 100;
    let page = 1;
    let all: Gift[] = [];
    let totalPages = 1;

    do {
      const response = await giftsApi.getAll({ page, limit: pageSize });
      all = all.concat(response.items);
      totalPages = response.meta.totalPages;
      page++;
    } while (page <= totalPages);

    allGifts.value = all;
  }

  /**
   * Fetch a specific gift by ID
   */
  async function fetchById(giftId: string): Promise<Gift> {
    const gift = await giftsApi.getById(giftId);

    const index = paginatedGifts.value.findIndex((g) => g.id === giftId);
    if (index !== -1) {
      paginatedGifts.value[index] = gift;
    } else {
      paginatedGifts.value.push(gift);
    }

    return gift;
  }

  /**
   * Create a new gift
   */
  async function create(data: GiftCreate): Promise<Gift> {
    const newGift = await giftsApi.create(data);
    paginatedGifts.value.push(newGift);
    return newGift;
  }

  /**
   * Update an existing gift
   */
  async function update(giftId: string, data: GiftUpdate): Promise<Gift> {
    const updatedGift = await giftsApi.update(giftId, data);

    const index = paginatedGifts.value.findIndex((g) => g.id === giftId);
    if (index !== -1) {
      paginatedGifts.value[index] = updatedGift;
    }

    return updatedGift;
  }

  /**
   * Delete a gift
   */
  async function remove(giftId: string): Promise<void> {
    await giftsApi.delete(giftId);
    paginatedGifts.value = paginatedGifts.value.filter((g) => g.id !== giftId);
  }

  /**
   * Clear all gifts from state
   */
  function clearGifts(): void {
    paginatedGifts.value = [];
  }

  return {
    // State
    paginatedGifts,
    allGifts,
    paginationMeta,

    // Actions
    fetchPaginated,
    fetchAll,
    fetchById,
    create,
    update,
    remove,
    clearGifts,
  };
});
