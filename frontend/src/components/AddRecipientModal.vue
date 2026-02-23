<template>
  <UModal
    v-model:open="openModel"
    title="Add recipient"
    description="Add a new person to your gift list."
    :ui="{ footer: 'justify-end' }"
  >
    <UButton icon="i-lucide-plus">Add recipient</UButton>

    <template #body>
      <UForm :schema="schema" :state="formState" id="recipient-form" class="flex flex-col gap-4" @submit="onSubmit">
        <UFormField label="Name" name="name" required>
          <UInput v-model="formState.name" placeholder="e.g. Mom" autocomplete="off" class="w-full"/>
        </UFormField>

        <UFormField label="Notes" name="notes">
          <UTextarea
            v-model="formState.notes"
            placeholder="Likes, dislikes, ideas..."
            class="w-full"
          />
        </UFormField>

        <UFormField label="Gifts" name="gift_ids">
          <USelectMenu
            v-model="formState.gift_ids"
            :items="giftOptions"
            value-key="value"
            multiple
            placeholder="Select gifts..."
            :ui="{ content: 'min-w-fit' }"
            class="w-full"
          />
        </UFormField>
      </UForm>
    </template>

    <template #footer="{ close }">
      <UButton color="neutral" variant="outline" @click="close">
        Cancel
      </UButton>
      <UButton color="primary" type="submit" form="recipient-form">
        Add recipient
      </UButton>
    </template>
  </UModal>
</template>

<script setup lang="ts">
import { computed, onMounted, reactive, watch } from "vue";
import { z } from "zod";
import type { FormSubmitEvent } from "@nuxt/ui";
import type { RecipientCreate } from "@/api/recipients";
import { useGifts } from "@/composables/useGifts";
import { useGiftsStore } from "@/stores/gifts";

const openModel = defineModel<boolean>("open", { required: true });

const emit = defineEmits<{
  submit: [data: RecipientCreate];
}>();

const schema = z.object({
  name: z.string().min(1, "Name is required").trim(),
  notes: z.string().trim().optional(),
  gift_ids: z.array(z.string()).optional(),
});

type Schema = z.output<typeof schema>;

const giftsStore = useGiftsStore();
const { fetchAll } = useGifts();
onMounted(() => {
  fetchAll();
});

const formState = reactive({
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
    formState.name = "";
    formState.notes = "";
    formState.gift_ids = [];
  }
});

function onSubmit(event: FormSubmitEvent<Schema>): void {
  const data: RecipientCreate = {
    name: event.data.name,
    notes: event.data.notes || null,
  };

  if (event.data.gift_ids && event.data.gift_ids.length > 0) {
    data.gift_ids = event.data.gift_ids;
  }

  emit("submit", data);
  openModel.value = false;
}
</script>
