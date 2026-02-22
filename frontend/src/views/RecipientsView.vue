<template>
  <div class="flex flex-col gap-6">
    <div class="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
      <div>
        <h1 class="text-2xl font-bold tracking-tight">Recipients</h1>
        <p class="text-sm text-gray-500 mt-1">People you love and want to surprise.</p>
      </div>
      <UButton icon="i-lucide-plus" @click="isModalOpen = true">
        Add new recipient
      </UButton>
    </div>

    <UAlert
      v-if="error"
      color="error"
      variant="subtle"
      icon="i-lucide-circle-alert"
      :description="error"
    />

    <div v-if="loading" class="flex justify-center py-12">
      <UIcon name="i-lucide-loader-2" class="w-8 h-8 animate-spin text-primary" />
    </div>

    <template v-else>
      <ul v-if="store.paginatedRecipients.length > 0" class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
        <RecipientCard
          v-for="recipient in store.paginatedRecipients"
          :key="recipient.id"
          v-bind="recipient"
          @delete="onRecipientDeleted"
        />
      </ul>
      <div v-else class="text-center py-12 text-gray-500 bg-gray-50 rounded-lg border border-dashed border-gray-200">
        No recipients found. Add one to get started!
      </div>

      <Paginator :meta="store.paginationMeta" @page-change="handlePageChange" />
    </template>

    <AddRecipientModal v-model:open="isModalOpen" @submit="onRecipientCreated" />
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from "vue";
import { useRecipients } from "@/composables/useRecipients";
import { useRecipientsStore } from "@/stores/recipients";
import { useGifts } from "@/composables/useGifts";
import type { RecipientCreate } from "@/api/recipients";
import RecipientCard from "@/components/RecipientCard.vue";
import Paginator from "@/components/Paginator.vue";
import AddRecipientModal from "@/components/AddRecipientModal.vue";

const { fetchPaginated, createRecipient, deleteRecipient, loading, error } = useRecipients();
const { fetchAll: fetchAllGifts } = useGifts();
const store = useRecipientsStore();

const currentPage = ref(1);
const limit = ref(10);
const isModalOpen = ref(false);

async function loadRecipients() {
  await fetchPaginated({ limit: limit.value, page: currentPage.value });
}

async function onRecipientCreated(data: RecipientCreate) {
  const success = await createRecipient(data);
  if (success) {
    isModalOpen.value = false;
    await loadRecipients();
  }
}

async function onRecipientDeleted(id: string) {
  const success = await deleteRecipient(id);
  if (success) {
    // Optional: if last item on page is deleted, handle pagination logic if necessary
    await loadRecipients();
  }
}

function handlePageChange(page: number) {
  currentPage.value = page;
  loadRecipients();
}

onMounted(() => {
  loadRecipients();
  fetchAllGifts();
});
</script>
