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
  const gifts = ref<Gift[]>([]);
  const paginationMeta = ref<PaginationMeta | null>(null);

  // Actions

  /**
   * Fetch all gifts for the current user
   */
  async function fetchAll(token: string, params?: FetchParams): Promise<void> {
    const response = await giftsApi.getAll(token, params);
    gifts.value = response.items;
    paginationMeta.value = response.meta;
  }

  /**
   * Fetch a specific gift by ID
   */
  async function fetchById(token: string, giftId: string): Promise<Gift> {
    const gift = await giftsApi.getById(token, giftId);

    const index = gifts.value.findIndex((g) => g.id === giftId);
    if (index !== -1) {
      gifts.value[index] = gift;
    } else {
      gifts.value.push(gift);
    }

    return gift;
  }

  /**
   * Create a new gift
   */
  async function create(token: string, data: GiftCreate): Promise<Gift> {
    const newGift = await giftsApi.create(token, data);
    gifts.value.push(newGift);
    return newGift;
  }

  /**
   * Update an existing gift
   */
  async function update(token: string, giftId: string, data: GiftUpdate): Promise<Gift> {
    const updatedGift = await giftsApi.update(token, giftId, data);

    const index = gifts.value.findIndex((g) => g.id === giftId);
    if (index !== -1) {
      gifts.value[index] = updatedGift;
    }

    return updatedGift;
  }

  /**
   * Delete a gift
   */
  async function remove(token: string, giftId: string): Promise<void> {
    await giftsApi.delete(token, giftId);
    gifts.value = gifts.value.filter((g) => g.id !== giftId);
  }

  /**
   * Clear all gifts from state
   */
  function clearGifts(): void {
    gifts.value = [];
  }

  return {
    // State
    gifts,
    paginationMeta,

    // Actions
    fetchAll,
    fetchById,
    create,
    update,
    remove,
    clearGifts,
  };
});
