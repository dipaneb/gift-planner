<template>
  <div>
    <div class="page-header">
      <div>
        <h1>Gifts</h1>
        <p>Track your gift ideas through their lifecycle.</p>
      </div>
      <button class="btn btn-primary" @click="isAddModalOpen = true">+ Add gift</button>
    </div>

    <div v-if="error" class="error">{{ error }}</div>

    <!-- Toolbar: filters + sort -->
    <div class="toolbar">
      <GiftStatusFilter v-model="statusFilter" />

      <div class="sort-control">
        <label for="sort-select">Sort:</label>
        <select id="sort-select" v-model="sortOrder" @change="loadGifts">
          <option value="default">Default</option>
          <option value="asc">Name A → Z</option>
          <option value="desc">Name Z → A</option>
        </select>
      </div>
    </div>

    <!-- Loading -->
    <div v-if="loading" class="loading-state">Loading gifts...</div>

    <!-- Empty state -->
    <div v-else-if="store.gifts.length === 0 && !statusFilter" class="empty-state">
      <div class="empty-icon">🎁</div>
      <h2>No gifts yet</h2>
      <p>Start tracking your gift ideas by adding your first one.</p>
      <button class="btn btn-primary" @click="isAddModalOpen = true">Add your first gift</button>
    </div>

    <!-- Filtered empty -->
    <div v-else-if="filteredGifts.length === 0 && statusFilter" class="empty-state">
      <p>No gifts with status "{{ GIFT_STATUS_LABELS[statusFilter] }}".</p>
      <button class="btn btn-secondary" @click="statusFilter = null">Clear filter</button>
    </div>

    <!-- Gift list -->
    <ul v-else class="gift-list">
      <GiftCard
        v-for="gift in filteredGifts"
        :key="gift.id"
        :gift="gift"
        @delete="onGiftDeleted"
        @status-change="onStatusChange"
      />
    </ul>

    <Paginator :meta="store.paginationMeta" @page-change="handlePageChange" />

    <AddGiftModal v-model:open="isAddModalOpen" @submit="onGiftCreated" />
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from "vue";
import { useGifts } from "@/composables/useGifts";
import { useGiftsStore } from "@/stores/gifts";
import { GIFT_STATUS_LABELS, type GiftCreate, type GiftStatus } from "@/api/gifts";
import type { FetchParams } from "@/api";
import GiftCard from "@/components/GiftCard.vue";
import GiftStatusFilter from "@/components/GiftStatusFilter.vue";
import Paginator from "@/components/Paginator.vue";
import AddGiftModal from "@/components/AddGiftModal.vue";

const { fetchAll, createGift, deleteGift, updateGiftStatus, loading, error } = useGifts();
const store = useGiftsStore();

const currentPage = ref(1);
const limit = ref(10);
const sortOrder = ref<FetchParams["sort"]>("default");
const isAddModalOpen = ref(false);
const statusFilter = ref<GiftStatus | null>(null);

const filteredGifts = computed(() => {
  if (!statusFilter.value) return store.gifts;
  return store.gifts.filter((g) => g.status === statusFilter.value);
});

async function loadGifts() {
  await fetchAll({ limit: limit.value, page: currentPage.value, sort: sortOrder.value });
}

async function onGiftCreated(data: GiftCreate) {
  const success = await createGift(data);
  if (success) {
    isAddModalOpen.value = false;
    await loadGifts();
  }
}

async function onGiftDeleted(id: string) {
  const success = await deleteGift(id);
  if (success) {
    await loadGifts();
  }
}

async function onStatusChange(id: string, status: GiftStatus) {
  await updateGiftStatus(id, status);
}

function handlePageChange(page: number) {
  currentPage.value = page;
  loadGifts();
}

onMounted(() => {
  loadGifts();
});
</script>

<style scoped>
.page-header {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  gap: 1rem;
  margin-bottom: 1.5rem;
}

.page-header h1 {
  margin: 0;
}

.page-header p {
  margin: 0.25rem 0 0;
  color: #6b7280;
}

.toolbar {
  display: flex;
  flex-wrap: wrap;
  align-items: center;
  justify-content: space-between;
  gap: 1rem;
  margin-bottom: 1.25rem;
}

.sort-control {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  font-size: 0.875rem;
}

.sort-control label {
  color: #6b7280;
  white-space: nowrap;
}

.sort-control select {
  padding: 0.35rem 0.6rem;
  border: 1px solid #d1d5db;
  border-radius: 6px;
  font-size: 0.875rem;
  background: #fff;
  cursor: pointer;
}

.sort-control select:focus {
  outline: none;
  border-color: #3b82f6;
}

.error {
  color: #b91c1c;
  padding: 1rem;
  margin: 0 0 1rem;
  background: #fef2f2;
  border-radius: 6px;
}

.loading-state {
  text-align: center;
  padding: 3rem 1rem;
  color: #6b7280;
  font-size: 0.9375rem;
}

.empty-state {
  text-align: center;
  padding: 3rem 1rem;
  color: #6b7280;
}

.empty-icon {
  font-size: 3rem;
  margin-bottom: 0.75rem;
}

.empty-state h2 {
  margin: 0 0 0.5rem;
  color: #374151;
  font-size: 1.25rem;
}

.empty-state p {
  margin: 0 0 1.25rem;
}

.gift-list {
  list-style: none;
  padding: 0;
  margin: 0 0 1rem;
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}

.btn {
  padding: 0.5rem 1rem;
  border: 1px solid transparent;
  border-radius: 6px;
  font-size: 0.875rem;
  font-weight: 500;
  cursor: pointer;
  transition: background-color 0.15s, border-color 0.15s;
}

.btn-primary {
  background: #3b82f6;
  color: #fff;
}

.btn-primary:hover {
  background: #2563eb;
}

.btn-secondary {
  background: #fff;
  color: #374151;
  border-color: #d1d5db;
}

.btn-secondary:hover {
  background: #f9fafb;
}

@media (max-width: 640px) {
  .page-header {
    flex-direction: column;
  }

  .toolbar {
    flex-direction: column;
    align-items: flex-start;
  }
}
</style>
