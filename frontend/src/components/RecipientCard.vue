<template>
  <li class="recipient-card">
    <div class="card-body">
      <h2 class="card-name">{{ props.name }}</h2>
      <p v-if="props.notes" class="card-notes">{{ props.notes }}</p>
      <div v-if="giftNames.length > 0" class="card-gifts">
        <span
          v-for="name in giftNames"
          :key="name"
          class="gift-tag"
        >{{ name }}</span>
      </div>
    </div>

    <div class="card-actions">
      <RouterLink
        :to="{ name: 'recipientDetails', params: { recipient_id: props.id } }"
        class="btn btn-link"
      >
        See more
      </RouterLink>
      <button class="btn btn-danger-outline" @click="onDelete">Delete</button>
    </div>
  </li>
</template>

<script setup lang="ts">
import { computed } from "vue";
import type { Recipient } from "@/api/recipients";
import { useGiftsStore } from "@/stores/gifts";

const props = defineProps<Recipient>();
const giftsStore = useGiftsStore();

const giftNames = computed(() => {
  return props.gift_ids
    .map((id) => giftsStore.allGifts.find((g) => g.id === id))
    .filter((g): g is NonNullable<typeof g> => g != null)
    .map((g) => g.name);
});

const emit = defineEmits<{
  delete: [id: string];
}>();

function onDelete() {
  if (!confirm(`Delete "${props.name}"? This cannot be undone.`)) return;
  emit("delete", props.id);
}
</script>

<style scoped>
.recipient-card {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 1rem;
  padding: 1rem 1.25rem;
  border: 1px solid #e5e7eb;
  border-radius: 8px;
  background: #fff;
}

.card-body {
  min-width: 0;
}

.card-name {
  margin: 0;
  font-size: 1rem;
  font-weight: 600;
}

.card-gifts {
  display: flex;
  flex-wrap: wrap;
  gap: 0.35rem;
  margin-top: 0.35rem;
}

.gift-tag {
  display: inline-block;
  padding: 0.1rem 0.5rem;
  background: #dbeafe;
  color: #1d4ed8;
  border-radius: 9999px;
  font-size: 0.75rem;
  font-weight: 500;
}

.card-notes {
  margin: 0.25rem 0 0;
  font-size: 0.875rem;
  color: #6b7280;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
  max-width: 400px;
}

.card-actions {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  flex-shrink: 0;
}

.btn {
  padding: 0.375rem 0.75rem;
  border: 1px solid transparent;
  border-radius: 6px;
  font-size: 0.8125rem;
  font-weight: 500;
  cursor: pointer;
  text-decoration: none;
  transition: background-color 0.15s, border-color 0.15s, color 0.15s;
}

.btn-link {
  color: #3b82f6;
  background: transparent;
}

.btn-link:hover {
  background: #eff6ff;
}

.btn-danger-outline {
  color: #ef4444;
  border-color: #fecaca;
  background: transparent;
}

.btn-danger-outline:hover {
  background: #fef2f2;
  border-color: #ef4444;
}
</style>
