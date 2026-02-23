<template>
  <div class="flex flex-col gap-6">
    <div class="flex flex-col sm:flex-row items-start justify-between gap-4 mb-6">
      <div>
        <h1 class="m-0">Gifts</h1>
        <p class="mt-1 mb-0 text-gray-500">Track your gift ideas through their lifecycle.</p>
      </div>
      <UButton @click="isAddModalOpen = true">Add gift</UButton>
    </div>

    <UAlert v-if="error" :title="error" variant="subtle" color="warning" />

    <!-- Toolbar: filters + sort -->
    <div class="flex flex-col sm:flex-row flex-wrap items-start sm:items-center justify-between gap-4 mb-5">
      <GiftStatusFilter v-model="statusFilter" />

      <USelect
        v-model="sortOrder"
        :items="sortItems"
        arrow
        color="info"
        @change="loadGifts"
        :ui="{
          trailingIcon: 'group-data-[state=open]:rotate-180 transition-transform duration-200',
          content: 'min-w-fit',
        }"
      />
    </div>

    <!-- Loading -->
    <div v-if="loading" class="text-center py-12 px-4 text-gray-500 text-sm">
      <UIcon name="i-lucide-loader-2" class="w-8 h-8 animate-spin text-primary" />
    </div>

    <!-- Empty state -->
    <div v-else-if="store.paginatedGifts.length === 0 && !statusFilter" class="text-center py-12 px-4 text-gray-500">
      <div class="text-5xl mb-3">🎁</div>
      <h2 class="m-0 mb-2 text-gray-700 text-xl">No gifts yet</h2>
      <p class="m-0 mb-5">Start tracking your gift ideas by adding your first one.</p>
      <UButton @click="isAddModalOpen = true">Add your first gift</UButton>
    </div>

    <!-- Filtered empty -->
    <div v-else-if="filteredGifts.length === 0 && statusFilter" class="text-center py-12 px-4 text-gray-500">
      <p class="m-0 mb-5">No gifts with status "{{ GIFT_STATUS_LABELS[statusFilter] }}".</p>
      <UButton @click="statusFilter = null">Clear filter</UButton>
    </div>

    <!-- Gift list -->
    <ul v-else class="list-none p-0 m-0 mb-4 grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
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
import { useRecipients } from "@/composables/useRecipients";
import { GIFT_STATUS_LABELS, type GiftCreate, type GiftStatus } from "@/api/gifts";
import type { FetchParams } from "@/api";
import GiftCard from "@/components/GiftCard.vue";
import GiftStatusFilter from "@/components/GiftStatusFilter.vue";
import Paginator from "@/components/Paginator.vue";
import AddGiftModal from "@/components/AddGiftModal.vue";

const { fetchPaginated, createGift, deleteGift, updateGiftStatus, loading, error } = useGifts();
const { fetchAll: fetchAllRecipients } = useRecipients();
const store = useGiftsStore();

const currentPage = ref(1);
const limit = ref(10);
const sortOrder = ref<FetchParams["sort"]>("default");
const isAddModalOpen = ref(false);
const statusFilter = ref<GiftStatus | null>(null);
const sortItems = [
  { label: "Default", value: "default" },
  { label: "Name A→Z", value: "asc" },
  { label: "Name Z→A", value: "desc" },
];

const filteredGifts = computed(() => {
  if (!statusFilter.value) return store.paginatedGifts;
  return store.paginatedGifts.filter((g) => g.status === statusFilter.value);
});

async function loadGifts() {
  await fetchPaginated({ limit: limit.value, page: currentPage.value, sort: sortOrder.value });
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
  fetchAllRecipients();
});
</script>
