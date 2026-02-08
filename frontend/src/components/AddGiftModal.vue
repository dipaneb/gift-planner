<template>
  <BaseModal v-model:open="openModel" title="Add gift">
    <form id="add-gift-form" novalidate @submit.prevent="onSubmit">
      <div class="form-group">
        <label for="gift-name">Name <span class="required">*</span></label>
        <input
          id="gift-name"
          v-model="form.name"
          type="text"
          required
          autocomplete="off"
          placeholder="e.g. Canon EOS R50"
        />
        <p v-if="errors.name" class="field-error">{{ errors.name }}</p>
      </div>

      <div class="form-group">
        <label for="gift-url">URL</label>
        <input
          id="gift-url"
          v-model="form.url"
          type="url"
          autocomplete="off"
          placeholder="https://..."
        />
        <p v-if="errors.url" class="field-error">{{ errors.url }}</p>
      </div>

      <div class="form-row">
        <div class="form-group">
          <label for="gift-price">Price (€)</label>
          <input
            id="gift-price"
            v-model="form.price"
            type="number"
            step="0.01"
            min="0.01"
            placeholder="0.00"
          />
          <p v-if="errors.price" class="field-error">{{ errors.price }}</p>
        </div>

        <div class="form-group">
          <label for="gift-quantity">Quantity</label>
          <input
            id="gift-quantity"
            v-model="form.quantity"
            type="number"
            min="1"
            step="1"
          />
          <p v-if="errors.quantity" class="field-error">{{ errors.quantity }}</p>
        </div>
      </div>

      <div class="form-group">
        <label for="gift-status">Status</label>
        <select id="gift-status" v-model="form.status">
          <option v-for="(label, key) in GIFT_STATUS_LABELS" :key="key" :value="key">
            {{ label }}
          </option>
        </select>
      </div>
    </form>

    <template #footer>
      <button type="button" class="btn btn-secondary" @click="openModel = false">
        Cancel
      </button>
      <button type="submit" form="add-gift-form" class="btn btn-primary">
        Add gift
      </button>
    </template>
  </BaseModal>
</template>

<script setup lang="ts">
import { reactive, watch } from "vue";
import { z } from "zod/v4";
import BaseModal from "@/components/BaseModal.vue";
import { GIFT_STATUS_LABELS, type GiftCreate, type GiftStatus } from "@/api/gifts";

const openModel = defineModel<boolean>("open", { required: true });

const emit = defineEmits<{
  submit: [data: GiftCreate];
}>();

const giftSchema = z.object({
  name: z.string().trim().min(1, "Name is required").max(255, "Name is too long (max 255)"),
  url: z
    .union([z.literal(""), z.url("Please enter a valid URL")])
    .transform((v) => (v === "" ? null : v))
    .nullable(),
  price: z
    .union([z.literal(""), z.coerce.number().positive("Price must be greater than 0")])
    .transform((v) => (v === "" ? null : v))
    .nullable(),
  quantity: z.coerce.number().int().min(1, "Quantity must be at least 1"),
  status: z.string() as z.ZodType<GiftStatus>,
});

const defaultForm = () => ({
  name: "",
  url: "",
  price: "" as string | number,
  quantity: 1,
  status: "idee" as GiftStatus,
});

const form = reactive(defaultForm());

const errors = reactive<Record<string, string>>({
  name: "",
  url: "",
  price: "",
  quantity: "",
});

watch(openModel, (isOpen) => {
  if (isOpen) {
    Object.assign(form, defaultForm());
    clearErrors();
  }
});

function clearErrors() {
  errors.name = "";
  errors.url = "";
  errors.price = "";
  errors.quantity = "";
}

function onSubmit(): void {
  clearErrors();

  const result = giftSchema.safeParse(form);

  if (!result.success) {
    for (const issue of result.error.issues) {
      const field = issue.path[0] as string;
      if (field in errors && !errors[field]) {
        errors[field] = issue.message;
      }
    }
    return;
  }

  const data: GiftCreate = {
    name: result.data.name,
    status: result.data.status,
    quantity: result.data.quantity,
  };

  if (result.data.url) data.url = result.data.url;
  if (result.data.price) data.price = result.data.price;

  emit("submit", data);
}
</script>

<style scoped>
.form-group {
  display: flex;
  flex-direction: column;
  gap: 0.25rem;
}

.form-group + .form-group {
  margin-top: 1rem;
}

.form-row {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 1rem;
  margin-top: 1rem;
}

.form-row .form-group + .form-group {
  margin-top: 0;
}

.form-group label {
  font-size: 0.875rem;
  font-weight: 500;
  color: #374151;
}

.required {
  color: #ef4444;
}

.form-group input,
.form-group select {
  padding: 0.5rem 0.75rem;
  border: 1px solid #d1d5db;
  border-radius: 6px;
  font-size: 0.875rem;
  line-height: 1.5;
  transition: border-color 0.15s;
  background: #fff;
}

.form-group input:focus,
.form-group select:focus {
  outline: none;
  border-color: #3b82f6;
  box-shadow: 0 0 0 3px rgba(59, 130, 246, 0.15);
}

.field-error {
  margin: 0.125rem 0 0;
  font-size: 0.8125rem;
  color: #dc2626;
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

.btn-secondary {
  background: #fff;
  color: #374151;
  border-color: #d1d5db;
}

.btn-secondary:hover {
  background: #f9fafb;
}
</style>
