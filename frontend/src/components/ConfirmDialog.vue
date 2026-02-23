<template>
  <UModal
    :title="title"
    :description="description"
    :dismissible="false"
    :ui="{ footer: 'justify-end' }"
  >
    <template #footer>
      <UButton
        label="Cancel"
        color="neutral"
        variant="outline"
        @click="emits('close', false)"
        class="cursor-pointer"
      />
      <UButton
        label="Confirm"
        color="error"
        @click="emits('close', true)"
        class="cursor-pointer"
      />
    </template>
  </UModal>
</template>

<script setup lang="ts">
interface ConfirmDialogProps {
  title?: string;
  description?: string;
}

defineProps<ConfirmDialogProps>();

const emits = defineEmits<{
  close: [value: boolean];
}>();
</script>
