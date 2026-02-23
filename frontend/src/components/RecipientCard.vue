<template>
  <UCard 
    as="li" 
    class="flex flex-col h-full cursor-pointer hover:ring-1 hover:ring-primary-500 transition-all"
    @click="goToDetails"
  >
    <template #header>
      <div class="flex items-center justify-between ">
        <h2 class="text-base font-semibold m-0">{{ props.name }}</h2>
        <UButton
          icon="i-lucide-trash"
          size="sm"
          variant="soft"
          color="error"
          @click.stop="onDelete"
        />
      </div>
    </template>
    <div class="flex flex-col gap-4">
      <div>
        <p v-if="props.notes" class="text-sm text-gray-500 truncate max-w-[400px]">
          {{ props.notes }}
        </p>
        <div v-if="giftNames.length > 0" class="flex flex-wrap gap-1.5 mt-2">
          <UBadge
            v-for="name in giftNames"
            :key="name"
            color="secondary"
            class="rounded-full"
            variant="soft"
          >
            {{ name }}
          </UBadge>
        </div>
      </div>
    </div>
  </UCard>
</template>

<script setup lang="ts">
import { computed } from "vue";
import { useRouter } from "vue-router";

import type { Recipient } from "@/api/recipients";
import { useGiftsStore } from "@/stores/gifts";
import { useConfirmDialog } from "@/composables/useConfirmDialog";

const props = defineProps<Recipient>();
const giftsStore = useGiftsStore();
const router = useRouter();
const confirm = useConfirmDialog();

const giftNames = computed(() => {
  return props.gift_ids
    .map((id) => giftsStore.allGifts.find((g) => g.id === id))
    .filter((g): g is NonNullable<typeof g> => g != null)
    .map((g) => g.name);
});

const emit = defineEmits<{
  delete: [id: string];
}>();

async function onDelete() {
  const confirmed = await confirm({
    title: `Delete "${props.name}"?`,
    description: "This action cannot be undone.",
  });
  
  if (!confirmed) return;
  emit("delete", props.id);
}

function goToDetails() {
  router.push({ name: 'recipientDetails', params: { recipient_id: props.id } });
}
</script>
