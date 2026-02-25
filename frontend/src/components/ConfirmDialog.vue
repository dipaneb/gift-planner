<template>
  <UModal
    :title="title"
    :description="description"
    :dismissible="false"
    :ui="{ footer: 'justify-end' }"
  >
    <template #footer>
      <UButton
        :label="t('common.cancel')"
        color="neutral"
        variant="outline"
        @click="emits('close', false)"
        class="cursor-pointer"
      />
      <UButton
        :label="t('common.confirm')"
        color="error"
        @click="emits('close', true)"
        class="cursor-pointer"
      />
    </template>
  </UModal>
</template>

<script setup lang="ts">
import { useI18n } from 'vue-i18n';

interface ConfirmDialogProps {
  title?: string;
  description?: string;
}

defineProps<ConfirmDialogProps>();

const emits = defineEmits<{
  close: [value: boolean];
}>();

const { t } = useI18n();
</script>
