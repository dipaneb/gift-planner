<template>
  <UModal
    v-model:open="openModel"
    :title="t('gifts.addGift')"
    :description="t('gifts.addGiftDescription')"
    :ui="{ footer: 'justify-end' }"
  >
    <UButton icon="i-lucide-plus">{{ t('gifts.addGift') }}</UButton>

    <template #body>
      <UForm
        :schema="giftSchema"
        :state="form"
        id="add-gift-form"
        class="flex flex-col gap-4"
        @submit="onSubmit"
      >
        <UFormField :label="t('auth.name')" name="name" required>
          <UInput
            v-model="form.name"
            :placeholder="t('gifts.namePlaceholder')"
            autocomplete="off"
            class="w-full"
          />
        </UFormField>

        <UFormField :label="t('gifts.url')" name="url">
          <UInput
            v-model="form.url"
            type="url"
            placeholder="https://..."
            autocomplete="off"
            class="w-full"
          />
        </UFormField>

        <div class="grid grid-cols-2 gap-4">
          <UFormField :label="t('gifts.priceWithCurrency')" name="price">
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

          <UFormField :label="t('gifts.quantity')" name="quantity">
            <UInputNumber v-model="form.quantity" :min="1" class="w-full" />
          </UFormField>
        </div>

        <UFormField :label="t('gifts.status')" name="status">
          <USelect v-model="form.status" :items="statusOptions" class="w-full" />
        </UFormField>

        <UFormField :label="t('gifts.recipientsField')" name="recipient_ids">
          <USelectMenu
            v-model="form.recipient_ids"
            :items="recipientOptions"
            value-key="value"
            multiple
            :placeholder="t('gifts.selectRecipients')"
            class="w-full"
          />
        </UFormField>
      </UForm>
    </template>

    <template #footer="{ close }">
      <UButton color="neutral" variant="outline" @click="close"> {{ t('common.cancel') }} </UButton>
      <UButton color="primary" type="submit" form="add-gift-form"> {{ t('gifts.addGift') }} </UButton>
    </template>
  </UModal>
</template>

<script setup lang="ts">
import { computed, onMounted, reactive, watch } from "vue";
import { useI18n } from "vue-i18n";
import { z } from "zod";
import type { FormSubmitEvent } from "@nuxt/ui";
import { type GiftCreate, type GiftStatus, GIFT_STATUS_LABELS } from "@/api/gifts";
import { useRecipients } from "@/composables/useRecipients";
import { useRecipientsStore } from "@/stores/recipients";

const { t } = useI18n();
const openModel = defineModel<boolean>("open", { required: true });

const emit = defineEmits<{
  submit: [data: GiftCreate];
}>();

const giftSchema = computed(() => z.object({
  name: z.string().trim().min(1, t('validation.nameRequired')).max(255, t('validation.nameTooLong')),
  url: z.url(t('validation.invalidUrl')).trim().optional().or(z.literal("")),
  price: z
    .union([z.literal(""), z.coerce.number().positive(t('validation.pricePositive'))])
    .optional(),
  quantity: z.coerce.number().int().min(1, t('validation.quantityMin')),
  status: z.string() as z.ZodType<GiftStatus>,
  recipient_ids: z.array(z.string()).optional(),
}));

type Schema = z.output<typeof giftSchema.value>;

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
  return Object.keys(GIFT_STATUS_LABELS).map((key) => ({
    label: t(`gifts.status_labels.${key}`),
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
