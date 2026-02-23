<template>
  <div class="flex flex-col gap-6 max-w-3xl">
    <UButton
      :to="{ name: 'recipients' }"
      icon="i-lucide-arrow-left"
      color="neutral"
      variant="ghost"
    >
      Back to recipients
    </UButton>

    <div v-if="loading" class="text-center py-12">
      <UIcon name="i-lucide-loader-2" class="w-8 h-8 animate-spin text-primary" />
    </div>

    <UAlert v-else-if="error" :title="error" variant="subtle" color="error" />

    <template v-if="recipient">
      <div class="flex items-start justify-between gap-4">
        <div class="flex-1">
          <h1 class="text-3xl font-bold mb-2">{{ recipient.name }}</h1>
          <p v-if="recipient.notes" class="text-gray-600 whitespace-pre-wrap">
            {{ recipient.notes }}
          </p>
          <p v-else class="text-gray-400 italic">No notes yet.</p>
        </div>

        <div class="flex gap-2 shrink-0">
          <EditRecipientModal
            v-model:open="isEditModalOpen"
            :recipient="recipient"
            @submit="onUpdate"
          />
          <UButton icon="i-lucide-trash" color="error" @click="onDelete"> Delete </UButton>
        </div>
      </div>

      <div class="pt-6 border-t border-gray-200">
        <h2 class="text-xl font-semibold mb-3">Gift ideas</h2>
        <p v-if="recipient.gift_ids.length === 0" class="text-gray-400 italic">
          No gifts assigned to this recipient.
        </p>
        <div v-else class="flex flex-wrap gap-2">
          <RouterLink
            v-for="g in resolvedGifts"
            :key="g.id"
            :to="{ name: 'giftDetails', params: { gift_id: g.id } }"
          >
            <UBadge color="info" variant="soft" size="lg" class="rounded-full">
              {{ g.name }}
            </UBadge>
          </RouterLink>
        </div>
      </div>

      <div class="pt-6 border-t border-gray-200">
        <h2 class="text-xl font-semibold mb-3">Groups</h2>
        <p class="text-gray-400 italic">Group management is not available yet. Coming soon.</p>
      </div>
    </template>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from "vue";
import { useRoute, useRouter } from "vue-router";
import { useRecipients } from "@/composables/useRecipients";
import { useRecipientsStore } from "@/stores/recipients";
import { useGifts } from "@/composables/useGifts";
import { useGiftsStore } from "@/stores/gifts";
import { useConfirmDialog } from "@/composables/useConfirmDialog";
import type { RecipientUpdate } from "@/api/recipients";
import EditRecipientModal from "@/components/EditRecipientModal.vue";

const route = useRoute();
const router = useRouter();
const store = useRecipientsStore();
const { fetchById, updateRecipient, deleteRecipient, loading, error } = useRecipients();
const giftsStore = useGiftsStore();
const { fetchAll: fetchAllGifts } = useGifts();
const confirm = useConfirmDialog();

const recipientId = computed(() => route.params.recipient_id as string);
const recipient = computed(
  () => store.paginatedRecipients.find((r) => r.id === recipientId.value) ?? null,
);

const isEditModalOpen = ref(false);

const resolvedGifts = computed(() => {
  if (!recipient.value) return [];
  return recipient.value.gift_ids
    .map((id) => giftsStore.allGifts.find((g) => g.id === id))
    .filter((g): g is NonNullable<typeof g> => g != null);
});

onMounted(async () => {
  await fetchById(recipientId.value);
  fetchAllGifts();
});

async function onUpdate(data: RecipientUpdate) {
  const success = await updateRecipient(recipientId.value, data);
  if (success) {
    isEditModalOpen.value = false;
    await fetchById(recipientId.value);
  }
}

async function onDelete() {
  const confirmed = await confirm({
    title: `Delete "${recipient.value?.name}"?`,
    description: "This action cannot be undone.",
  });

  if (!confirmed) return;

  const success = await deleteRecipient(recipientId.value);
  if (success) {
    router.push({ name: "recipients" });
  }
}
</script>
