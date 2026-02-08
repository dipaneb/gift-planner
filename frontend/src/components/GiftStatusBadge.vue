<template>
  <span
    class="status-badge"
    :style="{
      backgroundColor: colors.bg,
      color: colors.text,
      borderColor: colors.border,
    }"
  >
    {{ label }}
  </span>
</template>

<script setup lang="ts">
import { computed } from "vue";
import {
  GIFT_STATUS_LABELS,
  GIFT_STATUS_COLORS,
  type GiftStatus,
} from "@/api/gifts";

const props = defineProps<{
  status: GiftStatus;
}>();

const label = computed(() => GIFT_STATUS_LABELS[props.status]);
const colors = computed(() => GIFT_STATUS_COLORS[props.status]);
</script>

<style scoped>
.status-badge {
  display: inline-flex;
  align-items: center;
  padding: 0.2rem 0.6rem;
  border: 1px solid;
  border-radius: 9999px;
  font-size: 0.75rem;
  font-weight: 600;
  line-height: 1.4;
  white-space: nowrap;
  user-select: none;
}
</style>
