<template>
  <BaseModal v-model:open="openModel" title="Edit recipient">
    <form id="edit-recipient-form" novalidate @submit.prevent="onSubmit">
      <div class="form-group">
        <label for="edit-recipient-name">Name</label>
        <input
          id="edit-recipient-name"
          v-model="name"
          type="text"
          required
          autocomplete="off"
        />
      </div>

      <div class="form-group">
        <label for="edit-recipient-notes">Notes</label>
        <textarea
          id="edit-recipient-notes"
          v-model="notes"
          rows="3"
          placeholder="Likes, dislikes, ideas..."
        />
      </div>
    </form>

    <template #footer>
      <button type="button" class="btn btn-secondary" @click="openModel = false">
        Cancel
      </button>
      <button type="submit" form="edit-recipient-form" class="btn btn-primary">
        Save changes
      </button>
    </template>
  </BaseModal>
</template>

<script setup lang="ts">
import { ref, watch } from "vue";
import BaseModal from "@/components/BaseModal.vue";
import type { Recipient, RecipientUpdate } from "@/api/recipients";

interface Props {
  recipient: Recipient;
}

const props = defineProps<Props>();

const openModel = defineModel<boolean>("open", { required: true });

const emit = defineEmits<{
  submit: [data: RecipientUpdate];
}>();

const name = ref("");
const notes = ref("");

watch(openModel, (isOpen) => {
  if (isOpen) {
    name.value = props.recipient.name;
    notes.value = props.recipient.notes ?? "";
  }
});

function onSubmit(): void {
  if (!name.value.trim()) return;

  const update: RecipientUpdate = {};

  const trimmedName = name.value.trim();
  const trimmedNotes = notes.value.trim() || null;

  if (trimmedName !== props.recipient.name) {
    update.name = trimmedName;
  }
  if (trimmedNotes !== props.recipient.notes) {
    update.notes = trimmedNotes;
  }

  if (Object.keys(update).length === 0) {
    openModel.value = false;
    return;
  }

  emit("submit", update);
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

.form-group label {
  font-size: 0.875rem;
  font-weight: 500;
  color: #374151;
}

.form-group input,
.form-group textarea {
  padding: 0.5rem 0.75rem;
  border: 1px solid #d1d5db;
  border-radius: 6px;
  font-size: 0.875rem;
  line-height: 1.5;
  transition: border-color 0.15s;
}

.form-group input:focus,
.form-group textarea:focus {
  outline: none;
  border-color: #3b82f6;
  box-shadow: 0 0 0 3px rgba(59, 130, 246, 0.15);
}

.form-group textarea {
  resize: vertical;
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
