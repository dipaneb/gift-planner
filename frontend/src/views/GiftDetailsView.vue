<template>
  <div class="gift-details">
    <RouterLink :to="{ name: 'gifts' }" class="back-link">&larr; Back to gifts</RouterLink>

    <div v-if="loading" class="status-message">Loading...</div>
    <div v-else-if="error" class="status-message error">{{ error }}</div>

    <template v-if="gift">
      <header class="details-header">
        <div class="header-info">
          <div class="title-row">
            <h1>{{ gift.name }}</h1>
            <GiftStatusBadge :status="gift.status" />
          </div>

          <div class="meta-row">
            <span v-if="gift.price" class="meta-price">{{ formattedPrice }}</span>
            <span v-if="gift.quantity > 1" class="meta-qty">Quantity: {{ gift.quantity }}</span>
            <a
              v-if="gift.url"
              :href="gift.url"
              target="_blank"
              rel="noopener noreferrer"
              class="meta-link"
            >
              Visit link &nearr;
            </a>
          </div>
        </div>

        <div class="header-actions">
          <button class="btn btn-primary" @click="isEditModalOpen = true">Edit</button>
          <button class="btn btn-danger" @click="onDelete">Delete</button>
        </div>
      </header>

      <!-- Quick status update -->
      <section class="detail-section">
        <h2>Update status</h2>
        <div class="status-grid">
          <button
            v-for="(label, key) in GIFT_STATUS_LABELS"
            :key="key"
            :class="['status-btn', { active: gift.status === key }]"
            :style="
              gift.status === key
                ? {
                    backgroundColor: GIFT_STATUS_COLORS[key].bg,
                    color: GIFT_STATUS_COLORS[key].text,
                    borderColor: GIFT_STATUS_COLORS[key].border,
                  }
                : {}
            "
            @click="onQuickStatusUpdate(key as GiftStatus)"
          >
            {{ label }}
          </button>
        </div>
      </section>

      <!-- Recipients section (placeholder for now) -->
      <section class="detail-section">
        <h2>Recipients</h2>
        <p v-if="gift.recipient_ids.length === 0" class="placeholder">
          No recipients assigned to this gift.
        </p>
        <p v-else class="placeholder">
          {{ gift.recipient_ids.length }} recipient(s) assigned.
        </p>
      </section>

      <EditGiftModal
        v-model:open="isEditModalOpen"
        :gift="gift"
        @submit="onUpdate"
      />
    </template>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from "vue";
import { useRoute, useRouter } from "vue-router";
import { useGifts } from "@/composables/useGifts";
import { useGiftsStore } from "@/stores/gifts";
import {
  GIFT_STATUS_LABELS,
  GIFT_STATUS_COLORS,
  type GiftStatus,
  type GiftUpdate,
} from "@/api/gifts";
import GiftStatusBadge from "@/components/GiftStatusBadge.vue";
import EditGiftModal from "@/components/EditGiftModal.vue";

const route = useRoute();
const router = useRouter();
const store = useGiftsStore();
const { fetchById, updateGift, updateGiftStatus, deleteGift, loading, error } = useGifts();

const giftId = computed(() => route.params.gift_id as string);
const gift = computed(() => store.gifts.find((g) => g.id === giftId.value) ?? null);

const isEditModalOpen = ref(false);

const formattedPrice = computed(() => {
  if (!gift.value?.price) return null;
  return new Intl.NumberFormat("fr-FR", {
    style: "currency",
    currency: "EUR",
  }).format(Number(gift.value.price));
});

onMounted(async () => {
  await fetchById(giftId.value);
});

async function onUpdate(id: string, data: GiftUpdate) {
  const success = await updateGift(id, data);
  if (success) {
    isEditModalOpen.value = false;
    await fetchById(giftId.value);
  }
}

async function onQuickStatusUpdate(status: GiftStatus) {
  if (gift.value?.status === status) return;
  await updateGiftStatus(giftId.value, status);
}

async function onDelete() {
  if (!confirm(`Delete "${gift.value?.name}"? This cannot be undone.`)) return;

  const success = await deleteGift(giftId.value);
  if (success) {
    router.push({ name: "gifts" });
  }
}
</script>

<style scoped>
.gift-details {
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

.header-info {
  min-width: 0;
}

.title-row {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  flex-wrap: wrap;
}

.title-row h1 {
  margin: 0;
  font-size: 1.5rem;
  font-weight: 700;
}

.meta-row {
  display: flex;
  align-items: center;
  gap: 1rem;
  margin-top: 0.5rem;
  font-size: 0.875rem;
  color: #6b7280;
}

.meta-price {
  font-weight: 600;
  color: #374151;
  font-size: 1rem;
}

.meta-qty {
  background: #f3f4f6;
  padding: 0.15rem 0.5rem;
  border-radius: 4px;
}

.meta-link {
  color: #3b82f6;
  text-decoration: none;
}

.meta-link:hover {
  text-decoration: underline;
}

.header-actions {
  display: flex;
  gap: 0.5rem;
  flex-shrink: 0;
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

.status-grid {
  display: flex;
  flex-wrap: wrap;
  gap: 0.5rem;
}

.status-btn {
  padding: 0.4rem 0.85rem;
  border: 1px solid #d1d5db;
  border-radius: 9999px;
  background: #fff;
  font-size: 0.8125rem;
  font-weight: 500;
  color: #6b7280;
  cursor: pointer;
  transition: all 0.15s;
}

.status-btn:hover {
  border-color: #9ca3af;
  color: #374151;
}

.status-btn.active {
  font-weight: 600;
  cursor: default;
}

.placeholder {
  color: #9ca3af;
  font-style: italic;
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

@media (max-width: 640px) {
  .details-header {
    flex-direction: column;
  }

  .header-actions {
    width: 100%;
  }

  .header-actions .btn {
    flex: 1;
    text-align: center;
  }
}
</style>
