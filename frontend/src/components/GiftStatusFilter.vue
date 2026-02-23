<template>
  <ul class="flex flex-wrap gap-0.5">
    <UBadge
      :color="modelValue===null ? 'primary' : 'neutral'"
      :variant="modelValue===null ? 'subtle' : 'soft'"
      size="lg"
      class="rounded-full cursor-pointer"
      @click="$emit('update:modelValue', null)"
    >
      All
    </UBadge>
    <UBadge
      v-for="(label, key) in GIFT_STATUS_LABELS"
      :key="key"
      :color="modelValue===key ? 'primary' : 'neutral'"
      :variant="modelValue===key ? 'subtle' : 'soft'"
      size="lg"
      class="rounded-full cursor-pointer"
      @click="$emit('update:modelValue', key)"
    >
      {{ label }}
    </UBadge>
  </ul>
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
