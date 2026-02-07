<template>
  <div class="recipient-details">
    <RouterLink :to="{ name: 'recipients' }" class="back-link">&larr; Back to recipients</RouterLink>

    <div v-if="loading" class="status-message">Loading...</div>
    <div v-else-if="error" class="status-message error">{{ error }}</div>

    <template v-if="recipient">
      <header class="details-header">
        <div>
          <h1>{{ recipient.name }}</h1>
          <p v-if="recipient.notes" class="notes">{{ recipient.notes }}</p>
          <p v-else class="notes notes--empty">No notes yet.</p>
        </div>

        <div class="header-actions">
          <button class="btn btn-primary" @click="isEditModalOpen = true">Edit</button>
          <button class="btn btn-danger" @click="onDelete">Delete</button>
        </div>
      </header>

      <EditRecipientModal
        v-model:open="isEditModalOpen"
        :recipient="recipient"
        @submit="onUpdate"
      />

      <section class="detail-section">
        <h2>Gift ideas</h2>
        <p class="placeholder">Gift tracking is not available yet. Coming soon.</p>
      </section>

      <section class="detail-section">
        <h2>Groups</h2>
        <p class="placeholder">Group management is not available yet. Coming soon.</p>
      </section>
    </template>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from "vue";
import { useRoute, useRouter } from "vue-router";
import { useRecipients } from "@/composables/useRecipients";
import { useRecipientsStore } from "@/stores/recipients";
import type { RecipientUpdate } from "@/api/recipients";
import EditRecipientModal from "@/components/EditRecipientModal.vue";

const route = useRoute();
const router = useRouter();
const store = useRecipientsStore();
const { fetchById, updateRecipient, deleteRecipient, loading, error } = useRecipients();

const recipientId = computed(() => route.params.recipient_id as string);
const recipient = computed(() =>
  store.recipients.find((r) => r.id === recipientId.value) ?? null,
);

const isEditModalOpen = ref(false);

onMounted(async () => {
  await fetchById(recipientId.value);
});

async function onUpdate(data: RecipientUpdate) {
  const success = await updateRecipient(recipientId.value, data);
  if (success) {
    isEditModalOpen.value = false;
    await fetchById(recipientId.value);
  }
}

async function onDelete() {
  if (!confirm(`Delete "${recipient.value?.name}"? This cannot be undone.`)) return;

  const success = await deleteRecipient(recipientId.value);
  if (success) {
    router.push({ name: "recipients" });
  }
}
</script>

<style scoped>
.recipient-details {
  max-width: 720px;
}

.back-link {
  display: inline-block;
  margin-bottom: 1.5rem;
  color: #3b82f6;
  text-decoration: none;
  font-size: 0.875rem;
}

.back-link:hover {
  text-decoration: underline;
}

.status-message {
  padding: 1rem;
  border-radius: 6px;
  margin-bottom: 1rem;
}

.error {
  color: #b91c1c;
  background: #fef2f2;
}

.details-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  gap: 1rem;
  margin-bottom: 2rem;
}

.details-header h1 {
  margin: 0 0 0.25rem;
  font-size: 1.5rem;
  font-weight: 700;
}

.notes {
  color: #4b5563;
  margin: 0;
  line-height: 1.6;
  white-space: pre-wrap;
}

.notes--empty {
  font-style: italic;
  color: #9ca3af;
}

.header-actions {
  display: flex;
  gap: 0.5rem;
  flex-shrink: 0;
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

.btn-danger {
  background: #ef4444;
  color: #fff;
}

.btn-danger:hover {
  background: #dc2626;
}

.detail-section {
  margin-top: 2rem;
  padding-top: 1.5rem;
  border-top: 1px solid #e5e7eb;
}

.detail-section h2 {
  margin: 0 0 0.75rem;
  font-size: 1.125rem;
  font-weight: 600;
}

.placeholder {
  color: #9ca3af;
  font-style: italic;
}
</style>