<template>
  <UCard as="li" class="hover:ring-1 hover:ring-primary-500 transition-all">
    <template #header>
      <div class="flex items-center justify-between gap-2">
        <h3 v-if="gift.url && gift.url.length>0" class="m-0 text-base font-semibold truncate">
          <a :href="gift.url" class="hover:underline" target="_blank">{{ gift.name }}</a>
        </h3>
        <h3 v-else class="m-0 text-base font-semibold truncate">{{ gift.name }}</h3>
        
        <UButton
          icon="i-lucide-trash"
          size="sm"
          variant="soft"
          color="error"
          @click="onDelete"
          class="cursor-pointer"
        />
      </div>
    </template>

    <div class="flex flex-col gap-4">
      <div v-if="recipientNames.length > 0" class="flex flex-wrap gap-1.5">
        <UBadge
          v-for="name in recipientNames"
          :key="name"
          color="neutral"
          variant="soft"
        >
          {{ name }}
        </UBadge>
      </div>

      <div class="flex items-center gap-2 flex-wrap">
        <USelect
          :model-value="gift.status"
          :items="statusOptions"
          :ui="{ content: 'min-w-fit' }"
          @update:model-value="(value) => onStatusChange(value as GiftStatus)"
        />

        <UButton
          :to="{ name: 'giftDetails', params: { gift_id: gift.id } }"
          color="primary"
          variant="ghost"
        >
          Details
        </UButton>
      </div>
    </div>
  </UCard>
</template>

<script setup lang="ts">
import { computed } from "vue";

import { type Gift, type GiftStatus, GIFT_STATUS_LABELS } from "@/api/gifts";
import { useRecipientsStore } from "@/stores/recipients";
import { useConfirmDialog } from "@/composables/useConfirmDialog";

const props = defineProps<{
  gift: Gift;
}>();

const emit = defineEmits<{
  delete: [id: string];
  "status-change": [id: string, status: GiftStatus];
}>();

const recipientsStore = useRecipientsStore();
const confirm = useConfirmDialog();

const formattedPrice = computed(() => {
  if (!props.gift.price) return null;
  return new Intl.NumberFormat("fr-FR", {
    style: "currency",
    currency: "EUR",
  }).format(Number(props.gift.price));
});

const recipientNames = computed(() => {
  return props.gift.recipient_ids
    .map((id) => {
      const r = recipientsStore.allRecipients.find((r) => r.id === id);
      return r?.name ?? null;
    })
    .filter((n): n is string => n !== null);
});

const statusOptions = computed(() => {
  return Object.entries(GIFT_STATUS_LABELS).map(([value, label]) => ({
    label,
    value,
  }));
});

function onStatusChange(status: GiftStatus) {
  if (!status) return;
  emit("status-change", props.gift.id, status);
}

async function onDelete() {
  const confirmed = await confirm({
    title: `Delete "${props.gift.name}"?`,
    description: "This action cannot be undone.",
  });
  
  if (!confirmed) return;
  emit("delete", props.gift.id);
}
</script>
