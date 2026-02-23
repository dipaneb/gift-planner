<template>
<div class="flex flex-col gap-6">
    <UButton
      :to="{ name: 'gifts' }"
      icon="i-lucide-arrow-left"
      color="neutral"
      variant="ghost"
    >
      Back to gifts
    </UButton>

    <div v-if="loading" class="text-center py-12">
      <UIcon name="i-lucide-loader-2" class="w-8 h-8 animate-spin text-primary" />
    </div>

    <UAlert v-else-if="error" :title="error" variant="subtle" color="error" />

    <template v-if="gift">
      <div class="flex items-start justify-between gap-4">
        <div class="flex-1 min-w-0">
          <div class="flex items-center gap-3 flex-wrap mb-2">
            <h1>{{ gift.name }}</h1>
          </div>

          <div class="flex items-center gap-4 mt-2">
            <span v-if="gift.price">
              {{ formattedPrice }}
            </span>
            <UBadge v-if="gift.quantity > 1" color="neutral" variant="soft">
              Quantity: {{ gift.quantity }}
            </UBadge>
            <UButton
              v-if="gift.url"
              :to="gift.url"
              external
              target="_blank"
              icon="i-lucide-external-link"
              color="primary"
              variant="link"
            >
              Visit link
            </UButton>
          </div>
        </div>

        <div class="flex gap-2 shrink-0">
          <EditGiftModal
            v-model:open="isEditModalOpen"
            :gift="gift"
            @submit="onUpdate"
          />
          <UButton icon="i-lucide-trash" color="error" @click="onDelete">
            Delete
          </UButton>
        </div>
      </div>

      <div class="pt-6 border-t">
        <h2>Update status</h2>
        <div class="flex flex-wrap gap-1 pt-4">
          <UButton
            v-for="(label, key) in GIFT_STATUS_LABELS"
            :key="key"
            :variant="gift.status === key ? 'solid' : 'outline'"
            :color="gift.status === key ? getStatusColor(key as GiftStatus) : 'neutral'"
            size="sm"
            @click="onQuickStatusUpdate(key as GiftStatus)"
            class="rounded-full"
          >
            {{ label }}
          </UButton>
        </div>
      </div>

      <div class="pt-6 border-t">
        <h2>Recipients</h2>
        <p v-if="gift.recipient_ids.length === 0" class="text-gray-400 italic">
          No recipients assigned to this gift.
        </p>
        <div v-else class="flex flex-wrap gap-2">
          <RouterLink
            v-for="r in resolvedRecipients"
            :key="r.id"
            :to="{ name: 'recipientDetails', params: { recipient_id: r.id } }"
          >
            <UBadge color="primary" variant="soft" size="lg" class="rounded-full">
              {{ r.name }}
            </UBadge>
          </RouterLink>
        </div>
      </div>
    </template>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from "vue";
import { useRoute, useRouter } from "vue-router";
import { useGifts } from "@/composables/useGifts";
import { useGiftsStore } from "@/stores/gifts";
import { useRecipients } from "@/composables/useRecipients";
import { useRecipientsStore } from "@/stores/recipients";
import { useConfirmDialog } from "@/composables/useConfirmDialog";
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
const recipientsStore = useRecipientsStore();
const { fetchAll: fetchAllRecipients } = useRecipients();
const confirm = useConfirmDialog();

const giftId = computed(() => route.params.gift_id as string);
const gift = computed(() => store.paginatedGifts.find((g) => g.id === giftId.value) ?? null);

const isEditModalOpen = ref(false);

const formattedPrice = computed(() => {
  if (!gift.value?.price) return null;
  return new Intl.NumberFormat("fr-FR", {
    style: "currency",
    currency: "EUR",
  }).format(Number(gift.value.price));
});

const resolvedRecipients = computed(() => {
  if (!gift.value) return [];
  return gift.value.recipient_ids
    .map((id) => recipientsStore.allRecipients.find((r) => r.id === id))
    .filter((r): r is NonNullable<typeof r> => r != null);
});

function getStatusColor(status: GiftStatus) {
  const colorMap: Record<GiftStatus, "neutral" | "primary" | "success" | "warning" | "info"> = {
    idee: "neutral",
    achete: "warning",
    commande: "warning",
    en_cours_livraison: "info",
    livre: "info",
    recupere: "primary",
    emballe: "primary",
    offert: "success",
  };
  return colorMap[status] || "neutral";
}

onMounted(async () => {
  await fetchById(giftId.value);
  fetchAllRecipients();
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
  const confirmed = await confirm({
    title: `Delete "${gift.value?.name}"?`,
    description: "This action cannot be undone.",
  });

  if (!confirmed) return;

  const success = await deleteGift(giftId.value);
  if (success) {
    router.push({ name: "gifts" });
  }
}
</script>
