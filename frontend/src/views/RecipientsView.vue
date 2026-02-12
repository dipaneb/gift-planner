<template>
  <div>
    <h1>Recipients</h1>
    <p>People you love and want to surprise.</p>

    <div v-if="loading">Loading...</div>
    <div v-if="error" class="error">{{ error }}</div>

    <button @click="isModalOpen = true">Add new recipient</button>

    <AddRecipientModal v-model:open="isModalOpen" @submit="onRecipientCreated" />

    
    <ul v-if="!loading" class="recipient-list">
      <RecipientCard
        v-for="recipient in store.paginatedRecipients"
        :key="recipient.id"
        v-bind="recipient"
        @delete="onRecipientDeleted"
      />
    </ul>

    <Paginator :meta="store.paginationMeta" @page-change="handlePageChange" />
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

<style scoped>
.error {
  color: #b91c1c;
  padding: 1rem;
  margin: 1rem 0;
  background: #fef2f2;
  border-radius: 6px;
}

.recipient-list {
  list-style: none;
  padding: 0;
  margin: 1.5rem 0;
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}
</style>
