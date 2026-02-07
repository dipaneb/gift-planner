<template>
  <Teleport to="body">
    <Transition name="modal">
      <div
        v-if="open"
        class="modal-backdrop"
        @mousedown.self="$emit('update:open', false)"
      >
        <div
          ref="dialogRef"
          role="dialog"
          aria-modal="true"
          :aria-labelledby="titleId"
          tabindex="-1"
          class="modal-dialog"
          @keydown.escape="$emit('update:open', false)"
        >
          <header class="modal-header">
            <h2 :id="titleId" class="modal-title">{{ title }}</h2>
            <button
              type="button"
              class="modal-close"
              aria-label="Close"
              @click="$emit('update:open', false)"
            >
              &times;
            </button>
          </header>

          <div class="modal-body">
            <slot />
          </div>

          <footer v-if="$slots.footer" class="modal-footer">
            <slot name="footer" />
          </footer>
        </div>
      </div>
    </Transition>
  </Teleport>
</template>

<script setup lang="ts">
import { ref, watch, nextTick, useId } from "vue";

interface Props {
  open: boolean;
  title: string;
}

const props = defineProps<Props>();

defineEmits<{
  "update:open": [value: boolean];
}>();

const titleId = useId();
const dialogRef = ref<HTMLElement | null>(null);

watch(
  () => props.open,
  async (isOpen) => {
    if (isOpen) {
      await nextTick();
      dialogRef.value?.focus();
      document.body.style.overflow = "hidden";
    } else {
      document.body.style.overflow = "";
    }
  },
);
</script>

<style scoped>
.modal-backdrop {
  position: fixed;
  inset: 0;
  display: flex;
  align-items: center;
  justify-content: center;
  background: rgba(0, 0, 0, 0.5);
  z-index: 1000;
}

.modal-dialog {
  background: #fff;
  border-radius: 8px;
  box-shadow: 0 8px 30px rgba(0, 0, 0, 0.2);
  width: 90%;
  max-width: 480px;
  max-height: 85vh;
  display: flex;
  flex-direction: column;
  outline: none;
}

.modal-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 1rem 1.25rem;
  border-bottom: 1px solid #e5e7eb;
}

.modal-title {
  margin: 0;
  font-size: 1.125rem;
  font-weight: 600;
  line-height: 1.4;
}

.modal-close {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 2rem;
  height: 2rem;
  border: none;
  background: transparent;
  font-size: 1.5rem;
  line-height: 1;
  color: #6b7280;
  cursor: pointer;
  border-radius: 4px;
  transition: background-color 0.15s, color 0.15s;
}

.modal-close:hover {
  background: #f3f4f6;
  color: #111827;
}

.modal-body {
  padding: 1.25rem;
  overflow-y: auto;
}

.modal-footer {
  display: flex;
  justify-content: flex-end;
  gap: 0.5rem;
  padding: 1rem 1.25rem;
  border-top: 1px solid #e5e7eb;
}

/* Transition */
.modal-enter-active,
.modal-leave-active {
  transition: opacity 0.2s ease;
}

.modal-enter-from,
.modal-leave-to {
  opacity: 0;
}

.modal-enter-active .modal-dialog,
.modal-leave-active .modal-dialog {
  transition: transform 0.2s ease;
}

.modal-enter-from .modal-dialog,
.modal-leave-to .modal-dialog {
  transform: scale(0.95) translateY(-10px);
}
</style>
