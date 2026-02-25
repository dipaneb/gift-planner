<template>
  <UModal
    v-model:open="openModel"
    :title="t('recipients.editRecipient')"
    :description="t('recipients.editRecipientDescription')"
    :ui="{ footer: 'justify-end' }"
  >
    <UButton icon="i-lucide-pencil">{{ t('recipients.editRecipient') }}</UButton>

    <template #body>
      <UForm :schema="schema" :state="formState" id="edit-recipient-form" class="flex flex-col gap-4" @submit="onSubmit">
        <UFormField :label="t('auth.name')" name="name" required>
          <UInput v-model="formState.name" :placeholder="t('recipients.namePlaceholder')" autocomplete="off" class="w-full"/>
        </UFormField>

        <UFormField :label="t('recipients.notes')" name="notes">
          <UTextarea
            v-model="formState.notes"
            :placeholder="t('recipients.notesPlaceholder')"
            class="w-full"
          />
        </UFormField>

        <UFormField :label="t('recipients.giftsField')" name="gift_ids">
          <USelectMenu
            v-model="formState.gift_ids"
            :items="giftOptions"
            value-key="value"
            multiple
            :placeholder="t('recipients.selectGifts')"
            class="w-full"
          />
        </UFormField>
      </UForm>
    </template>

    <template #footer="{ close }">
      <UButton color="neutral" variant="outline" @click="close">
        {{ t('common.cancel') }}
      </UButton>
      <UButton color="primary" type="submit" form="edit-recipient-form">
        {{ t('common.save') }}
      </UButton>
    </template>
  </UModal>
</template>

<script setup lang="ts">
import { computed, onMounted, reactive, watch } from "vue";
import { useI18n } from "vue-i18n";
import { z } from "zod";
import type { FormSubmitEvent } from "@nuxt/ui";
import type { Recipient, RecipientUpdate } from "@/api/recipients";
import { useGifts } from "@/composables/useGifts";
import { useGiftsStore } from "@/stores/gifts";

interface Props {
  recipient: Recipient;
}

const props = defineProps<Props>();

const { t } = useI18n();
const openModel = defineModel<boolean>("open", { required: true });

const emit = defineEmits<{
  submit: [data: RecipientUpdate];
}>();

const schema = computed(() => z.object({
  name: z.string().min(1, t('validation.nameRequired')).trim(),
  notes: z.string().trim().optional(),
  gift_ids: z.array(z.string()).optional(),
}));

type Schema = z.output<typeof schema.value>;

const giftsStore = useGiftsStore();
const { fetchAll } = useGifts();
onMounted(() => {
  fetchAll();
});

const formState = reactive<Partial<Schema>>({
  name: "",
  notes: "",
  gift_ids: [] as string[],
});

const giftOptions = computed(() => {
  return giftsStore.allGifts.map((gift) => ({
    label: gift.name,
    value: gift.id,
  }));
});

watch(openModel, (isOpen) => {
  if (isOpen) {
    formState.name = props.recipient.name;
    formState.notes = props.recipient.notes ?? "";
    formState.gift_ids = [...props.recipient.gift_ids];
  }
});

function onSubmit(event: FormSubmitEvent<Schema>): void {
  const update: RecipientUpdate = {};

  const trimmedName = event.data.name;
  const trimmedNotes = event.data.notes || null;

  if (trimmedName !== props.recipient.name) {
    update.name = trimmedName;
  }
  if (trimmedNotes !== props.recipient.notes) {
    update.notes = trimmedNotes;
  }

  // Always send gift_ids so the user can add/remove/clear
  const currentIds = [...(event.data.gift_ids || [])].sort();
  const originalIds = [...props.recipient.gift_ids].sort();
  if (JSON.stringify(currentIds) !== JSON.stringify(originalIds)) {
    update.gift_ids = event.data.gift_ids || [];
  }

  if (Object.keys(update).length === 0) {
    openModel.value = false;
    return;
  }

  emit("submit", update);
  openModel.value = false;
}
</script>
