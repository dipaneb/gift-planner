<template>
  <ul class="flex flex-wrap gap-0.5">
    <UBadge
      :color="modelValue===null ? 'primary' : 'neutral'"
      :variant="modelValue===null ? 'subtle' : 'soft'"
      size="lg"
      class="rounded-full cursor-pointer"
      @click="$emit('update:modelValue', null)"
    >
      {{ t('common.all') }}
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
      {{ t(`gifts.status_labels.${key}`) }}
    </UBadge>
  </ul>
</template>

<script setup lang="ts">
import {
  GIFT_STATUS_LABELS,
  type GiftStatus,
} from "@/api/gifts";
import { useI18n } from "vue-i18n";

defineProps<{
  modelValue: GiftStatus | null;
}>();

defineEmits<{
  "update:modelValue": [value: GiftStatus | null];
}>();

const { t } = useI18n();
</script>
