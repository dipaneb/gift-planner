<template>
  <div class="status-filter">
    <button
      :class="['filter-chip', { active: modelValue === null }]"
      @click="$emit('update:modelValue', null)"
    >
      All
    </button>
    <button
      v-for="(label, key) in GIFT_STATUS_LABELS"
      :key="key"
      :class="['filter-chip', { active: modelValue === key }]"
      :style="
        modelValue === key
          ? {
              backgroundColor: GIFT_STATUS_COLORS[key].bg,
              color: GIFT_STATUS_COLORS[key].text,
              borderColor: GIFT_STATUS_COLORS[key].border,
            }
          : {}
      "
      @click="$emit('update:modelValue', key)"
    >
      {{ label }}
    </button>
  </div>
</template>

<script setup lang="ts">
import {
  GIFT_STATUS_LABELS,
  GIFT_STATUS_COLORS,
  type GiftStatus,
} from "@/api/gifts";

defineProps<{
  modelValue: GiftStatus | null;
}>();

defineEmits<{
  "update:modelValue": [value: GiftStatus | null];
}>();
</script>

<style scoped>
.status-filter {
  display: flex;
  flex-wrap: wrap;
  gap: 0.375rem;
}

.filter-chip {
  padding: 0.3rem 0.7rem;
  border: 1px solid #d1d5db;
  border-radius: 9999px;
  background: #fff;
  font-size: 0.8125rem;
  font-weight: 500;
  color: #6b7280;
  cursor: pointer;
  transition: all 0.15s;
  white-space: nowrap;
}

.filter-chip:hover {
  border-color: #9ca3af;
  color: #374151;
}

.filter-chip.active {
  background: #f3f4f6;
  color: #111827;
  border-color: #9ca3af;
  font-weight: 600;
}
</style>
