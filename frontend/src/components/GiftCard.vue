<template>
  <li class="gift-card">
    <div class="card-main">
      <div class="card-header">
        <h3 class="card-name">{{ gift.name }}</h3>
        <GiftStatusBadge :status="gift.status" />
      </div>

      <div class="card-meta">
        <span v-if="gift.price" class="meta-price">{{ formattedPrice }}</span>
        <span v-if="gift.quantity > 1" class="meta-qty">x{{ gift.quantity }}</span>
        <a
          v-if="gift.url"
          :href="gift.url"
          target="_blank"
          rel="noopener noreferrer"
          class="meta-link"
        >
          Link &nearr;
        </a>
      </div>
    </div>

    <div class="card-actions">
      <select
        :value="gift.status"
        class="status-select"
        @change="onStatusChange"
      >
        <option v-for="(label, key) in GIFT_STATUS_LABELS" :key="key" :value="key">
          {{ label }}
        </option>
      </select>

      <RouterLink
        :to="{ name: 'giftDetails', params: { gift_id: gift.id } }"
        class="btn btn-link"
      >
        Details
      </RouterLink>

      <button class="btn btn-danger-outline" @click="onDelete">Delete</button>
    </div>
  </li>
</template>

<script setup lang="ts">
import { computed } from "vue";
import { type Gift, type GiftStatus, GIFT_STATUS_LABELS } from "@/api/gifts";
import GiftStatusBadge from "@/components/GiftStatusBadge.vue";

const props = defineProps<{
  gift: Gift;
}>();

const emit = defineEmits<{
  delete: [id: string];
  "status-change": [id: string, status: GiftStatus];
}>();

const formattedPrice = computed(() => {
  if (!props.gift.price) return null;
  return new Intl.NumberFormat("fr-FR", {
    style: "currency",
    currency: "EUR",
  }).format(Number(props.gift.price));
});

function onStatusChange(event: Event) {
  const target = event.target as HTMLSelectElement;
  emit("status-change", props.gift.id, target.value as GiftStatus);
}

function onDelete() {
  if (!confirm(`Delete "${props.gift.name}"? This cannot be undone.`)) return;
  emit("delete", props.gift.id);
}
</script>

<style scoped>
.gift-card {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 1rem;
  padding: 1rem 1.25rem;
  border: 1px solid #e5e7eb;
  border-radius: 8px;
  background: #fff;
  transition: box-shadow 0.15s;
}

.gift-card:hover {
  box-shadow: 0 1px 4px rgba(0, 0, 0, 0.06);
}

.card-main {
  min-width: 0;
  flex: 1;
}

.card-header {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  flex-wrap: wrap;
}

.card-name {
  margin: 0;
  font-size: 1rem;
  font-weight: 600;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
  max-width: 300px;
}

.card-meta {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  margin-top: 0.35rem;
  font-size: 0.8125rem;
  color: #6b7280;
}

.meta-price {
  font-weight: 600;
  color: #374151;
}

.meta-qty {
  background: #f3f4f6;
  padding: 0.1rem 0.4rem;
  border-radius: 4px;
  font-weight: 500;
}

.meta-link {
  color: #3b82f6;
  text-decoration: none;
}

.meta-link:hover {
  text-decoration: underline;
}

.card-actions {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  flex-shrink: 0;
}

.status-select {
  padding: 0.3rem 0.5rem;
  border: 1px solid #d1d5db;
  border-radius: 6px;
  font-size: 0.8125rem;
  background: #fff;
  cursor: pointer;
  color: #374151;
}

.status-select:focus {
  outline: none;
  border-color: #3b82f6;
  box-shadow: 0 0 0 2px rgba(59, 130, 246, 0.15);
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

@media (max-width: 640px) {
  .gift-card {
    flex-direction: column;
    align-items: flex-start;
  }

  .card-actions {
    width: 100%;
    justify-content: flex-end;
    border-top: 1px solid #f3f4f6;
    padding-top: 0.75rem;
    margin-top: 0.25rem;
  }

  .card-name {
    max-width: 100%;
  }
}
</style>
