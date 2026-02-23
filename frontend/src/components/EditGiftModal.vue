<template>
  <UModal
    v-model:open="openModel"
    title="Edit gift"
    description="Update gift information."
    :ui="{ footer: 'justify-end' }"
  >
    <UButton icon="i-lucide-pencil">Edit gift</UButton>

    <template #body>
      <UForm
        :schema="schema"
        :state="formState"
        id="edit-gift-form"
        class="flex flex-col gap-4"
        @submit="onSubmit"
      >
        <UFormField label="Name" name="name" required>
          <UInput
            v-model="formState.name"
            placeholder="e.g. Book"
            autocomplete="off"
            class="w-full"
          />
        </UFormField>

        <UFormField label="URL" name="url">
          <UInput v-model="formState.url" type="url" placeholder="https://..." class="w-full" />
        </UFormField>

        <div class="grid grid-cols-2 gap-4">
          <UFormField label="Price" name="price">
            <UInputNumber
              v-model="formState.price"
              :step="0.01"
              :min="0"
              placeholder="0.00"
              :format-options="{
                style: 'currency',
                currency: 'EUR',
                currencyDisplay: 'symbol',
              }"
              class="w-full"
            />
          </UFormField>

          <UFormField label="Quantity" name="quantity" required>
            <UInputNumber v-model="formState.quantity" :min="1" class="w-full" />
          </UFormField>
        </div>

        <UFormField label="Status" name="status" required>
          <USelect v-model="formState.status" :items="statusOptions" class="w-full" />
        </UFormField>

        <UFormField label="Recipients" name="recipient_ids">
          <USelectMenu
            v-model="formState.recipient_ids"
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
      <UButton color="primary" type="submit" form="edit-gift-form"> Save changes </UButton>
    </template>
  </UModal>
</template>

<script setup lang="ts">
import { computed, onMounted, reactive, watch } from "vue";
import { z } from "zod";
import type { FormSubmitEvent } from "@nuxt/ui";
import { GIFT_STATUS_LABELS, type Gift, type GiftUpdate, type GiftStatus } from "@/api/gifts";
import { useRecipients } from "@/composables/useRecipients";
import { useRecipientsStore } from "@/stores/recipients";

const props = defineProps<{
  gift: Gift | null;
}>();

const openModel = defineModel<boolean>("open", { required: true });

const emit = defineEmits<{
  submit: [id: string, data: GiftUpdate];
}>();

const schema = z.object({
  name: z.string().trim().min(1, "Name is required").max(255, "Name is too long (max 255)"),
  url: z.url("Please enter a valid URL").trim().optional().or(z.literal("")),
  price: z
    .union([z.number(), z.coerce.number().positive("Price must be greater than 0")])
    .optional(),
  quantity: z.coerce.number().int().min(1, "Quantity must be at least 1"),
  status: z.string() as z.ZodType<GiftStatus>,
  recipient_ids: z.array(z.string()).optional(),
});

type Schema = z.output<typeof schema>;

const recipientsStore = useRecipientsStore();
const { fetchAll } = useRecipients();
onMounted(() => {
  fetchAll();
});

const formState = reactive<Partial<Schema>>({
  name: "",
  url: "",
  price: undefined,
  quantity: 1,
  status: "idee" as GiftStatus,
  recipient_ids: [] as string[],
});

const statusOptions = computed(() => {
  return Object.entries(GIFT_STATUS_LABELS).map(([value, label]) => ({
    label,
    value,
  }));
});

const recipientOptions = computed(() => {
  return recipientsStore.allRecipients.map((recipient) => ({
    label: recipient.name,
    value: recipient.id,
  }));
});

watch(
  () => [openModel.value, props.gift] as const,
  ([isOpen, gift]) => {
    if (isOpen && gift) {
      formState.name = gift.name;
      formState.url = gift.url ?? "";
      formState.price = gift.price ? Number(gift.price) : undefined;
      formState.quantity = gift.quantity;
      formState.status = gift.status;
      formState.recipient_ids = [...gift.recipient_ids];
    }
  },
);

function onSubmit(event: FormSubmitEvent<Schema>): void {
  if (!props.gift) return;

  const data: GiftUpdate = {
    name: event.data.name,
    url: event.data.url && event.data.url !== "" ? event.data.url : null,
    price: event.data.price
      ? typeof event.data.price === "string"
        ? parseFloat(event.data.price)
        : event.data.price
      : null,
    status: event.data.status,
    quantity: event.data.quantity,
    recipient_ids: event.data.recipient_ids || [],
  };

  emit("submit", props.gift.id, data);
  openModel.value = false;
}
</script>
