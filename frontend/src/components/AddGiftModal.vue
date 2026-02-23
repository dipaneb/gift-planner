<template>
  <UModal
    v-model:open="openModel"
    title="Add gift"
    description="Add a new gift idea to track."
    :ui="{ footer: 'justify-end' }"
  >
    <UButton icon="i-lucide-plus">Add gift</UButton>

    <template #body>
      <UForm
        :schema="giftSchema"
        :state="form"
        id="add-gift-form"
        class="flex flex-col gap-4"
        @submit="onSubmit"
      >
        <UFormField label="Name" name="name" required>
          <UInput
            v-model="form.name"
            placeholder="e.g. Canon EOS R50"
            autocomplete="off"
            class="w-full"
          />
        </UFormField>

        <UFormField label="URL" name="url">
          <UInput
            v-model="form.url"
            type="url"
            placeholder="https://..."
            autocomplete="off"
            class="w-full"
          />
        </UFormField>

        <div class="grid grid-cols-2 gap-4">
          <UFormField label="Price (€)" name="price">
            <UInputNumber
              :v-model="form.price"
              :step="0.01"
              :min="0"
              placeholder="0.00"
              :format-options="{
                style: 'currency',
                currency: 'EUR',
                currencyDisplay: 'symbol'
              }"
              class="w-full"
            />
          </UFormField>

          <UFormField label="Quantity" name="quantity">
            <UInputNumber v-model="form.quantity" :min="1" class="w-full" />
          </UFormField>
        </div>

        <UFormField label="Status" name="status">
          <USelect v-model="form.status" :items="statusOptions" class="w-full" />
        </UFormField>

        <UFormField label="Recipients" name="recipient_ids">
          <USelectMenu
            v-model="form.recipient_ids"
            :items="recipientOptions"
            value-key="value"
            multiple
            placeholder="Select recipients..."
            class="w-full"
          />
        </UFormField>
      </UForm>
    </template>

    <template #footer="{ close }">
      <UButton color="neutral" variant="outline" @click="close"> Cancel </UButton>
      <UButton color="primary" type="submit" form="add-gift-form"> Add gift </UButton>
    </template>
  </UModal>
</template>

<script setup lang="ts">
import { computed, onMounted, reactive, watch } from "vue";
import { z } from "zod";
import type { FormSubmitEvent } from "@nuxt/ui";
import { GIFT_STATUS_LABELS, type GiftCreate, type GiftStatus } from "@/api/gifts";
import { useRecipients } from "@/composables/useRecipients";
import { useRecipientsStore } from "@/stores/recipients";

const openModel = defineModel<boolean>("open", { required: true });

const emit = defineEmits<{
  submit: [data: GiftCreate];
}>();

const giftSchema = z.object({
  name: z.string().trim().min(1, "Name is required").max(255, "Name is too long (max 255)"),
  url: z.url("Please enter a valid URL").trim().optional().or(z.literal("")),
  price: z
    .union([z.literal(""), z.coerce.number().positive("Price must be greater than 0")])
    .optional(),
  quantity: z.coerce.number().int().min(1, "Quantity must be at least 1"),
  status: z.string() as z.ZodType<GiftStatus>,
  recipient_ids: z.array(z.string()).optional(),
});

type Schema = z.output<typeof giftSchema>;

const recipientsStore = useRecipientsStore();
const { fetchAll } = useRecipients();
onMounted(() => {
  fetchAll();
});

const form = reactive<Partial<Schema>>({
  name: "",
  url: "",
  price: undefined,
  quantity: 1,
  status: "idee" as GiftStatus,
  recipient_ids: [] as string[],
});

const statusOptions = computed(() => {
  return Object.entries(GIFT_STATUS_LABELS).map(([key, label]) => ({
    label,
    value: key,
  }));
});

const recipientOptions = computed(() => {
  return recipientsStore.allRecipients.map((recipient) => ({
    label: recipient.name,
    value: recipient.id,
  }));
});

watch(openModel, (isOpen) => {
  if (isOpen) {
    form.name = "";
    form.url = "";
    form.price = "";
    form.quantity = 1;
    form.status = "idee";
    form.recipient_ids = [];
  }
});

function onSubmit(event: FormSubmitEvent<Schema>): void {
  const data: GiftCreate = {
    name: event.data.name,
    status: event.data.status,
    quantity: event.data.quantity,
  };

  if (event.data.url && event.data.url !== "") {
    data.url = event.data.url;
  }

  if (event.data.price) {
    data.price = event.data.price;
  }

  if (event.data.recipient_ids && event.data.recipient_ids.length > 0) {
    data.recipient_ids = event.data.recipient_ids;
  }

  emit("submit", data);
  openModel.value = false;
}
</script>
