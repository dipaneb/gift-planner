<template>
  <BaseModal v-model:open="openModel" title="Add recipient">
    <form id="add-recipient-form" novalidate @submit.prevent="onSubmit">
      <div class="form-group">
        <label for="recipient-name">Name</label>
        <input
          id="recipient-name"
          v-model="name"
          type="text"
          required
          autocomplete="off"
          placeholder="e.g. Mom"
        />
      </div>

      <div class="form-group">
        <label for="recipient-notes">Notes</label>
        <textarea
          id="recipient-notes"
          v-model="notes"
          rows="3"
          placeholder="Likes, dislikes, ideas..."
        />
      </div>

      <div class="form-group">
        <label>Gifts</label>
        <div class="checkbox-list">
          <p v-if="giftsStore.allGifts.length === 0" class="checkbox-empty">
            No gifts yet.
          </p>
          <label
            v-for="gift in giftsStore.allGifts"
            :key="gift.id"
            class="checkbox-item"
          >
            <input
              type="checkbox"
              :value="gift.id"
              v-model="giftIds"
            />
            {{ gift.name }}
          </label>
        </div>
      </div>
    </form>

    <template #footer>
      <button type="button" class="btn btn-secondary" @click="openModel = false">
        Cancel
      </button>
      <button type="submit" form="add-recipient-form" class="btn btn-primary">
        Add recipient
      </button>
    </template>
  </BaseModal>
</template>

<script setup lang="ts">
import { onMounted, ref, watch } from "vue";
import BaseModal from "@/components/BaseModal.vue";
import type { RecipientCreate } from "@/api/recipients";
import { useGifts } from "@/composables/useGifts";
import { useGiftsStore } from "@/stores/gifts";

const openModel = defineModel<boolean>("open", { required: true });

const emit = defineEmits<{
  submit: [data: RecipientCreate];
}>();

const giftsStore = useGiftsStore();
const { fetchAll } = useGifts();
onMounted(() => {
  fetchAll();
});

const name = ref("");
const notes = ref("");
const giftIds = ref<string[]>([]);

watch(openModel, (isOpen) => {
  if (isOpen) {
    name.value = "";
    notes.value = "";
    giftIds.value = [];
  }
});

function onSubmit(): void {
  if (!name.value.trim()) return;

  const data: RecipientCreate = {
    name: name.value.trim(),
    notes: notes.value.trim() || null,
  };

  if (giftIds.value.length > 0) {
    data.gift_ids = giftIds.value;
  }

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

.checkbox-list {
  max-height: 160px;
  overflow-y: auto;
  border: 1px solid #d1d5db;
  border-radius: 6px;
  padding: 0.5rem;
  display: flex;
  flex-direction: column;
  gap: 0.25rem;
}

.checkbox-item {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.3rem 0.5rem;
  border-radius: 4px;
  font-size: 0.875rem;
  cursor: pointer;
  transition: background-color 0.1s;
}

.checkbox-item:hover {
  background: #f3f4f6;
}

.checkbox-item input[type="checkbox"] {
  accent-color: #3b82f6;
}

.checkbox-empty {
  margin: 0;
  padding: 0.5rem;
  color: #9ca3af;
  font-size: 0.8125rem;
  font-style: italic;
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
