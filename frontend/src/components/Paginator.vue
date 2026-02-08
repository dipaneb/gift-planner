<template>
  <nav v-if="meta && meta.totalPages > 1" class="paginator">
    <button
      :disabled="!meta.hasPrev"
      @click="$emit('page-change', meta.page - 1)"
      class="paginator-btn"
    >
      Previous
    </button>

    <div class="paginator-pages">
      <button
        v-for="page in visiblePages"
        :key="page"
        @click="$emit('page-change', page)"
        :class="['paginator-page', { active: page === meta.page }]"
      >
        {{ page }}
      </button>
    </div>

    <button
      :disabled="!meta.hasNext"
      @click="$emit('page-change', meta.page + 1)"
      class="paginator-btn"
    >
      Next
    </button>

    <div class="paginator-info">
      Page {{ meta.page }} of {{ meta.totalPages }} ({{ meta.total }} total)
    </div>
  </nav>
</template>

<script setup lang="ts">
import { computed } from "vue";
import type { PaginationMeta } from "@/api/index";

const props = defineProps<{
  meta: PaginationMeta | null;
}>();

defineEmits<{
  "page-change": [page: number];
}>();

const visiblePages = computed(() => {
  if (!props.meta) return [];

  const current = props.meta.page;
  const total = props.meta.totalPages;
  const delta = 2;

  const range: number[] = [];
  const rangeWithDots: (number | string)[] = [];

  for (
    let i = Math.max(2, current - delta);
    i <= Math.min(total - 1, current + delta);
    i++
  ) {
    range.push(i);
  }

  if (current - delta > 2) {
    rangeWithDots.push(1, "...");
  } else {
    rangeWithDots.push(1);
  }

  rangeWithDots.push(...range);

  if (current + delta < total - 1) {
    rangeWithDots.push("...", total);
  } else if (total > 1) {
    rangeWithDots.push(total);
  }

  return rangeWithDots.filter((v) => typeof v === "number") as number[];
});
</script>

<style scoped>
.paginator {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  margin-top: 1rem;
}

.paginator-btn,
.paginator-page {
  padding: 0.5rem 1rem;
  border: 1px solid #ccc;
  background: white;
  cursor: pointer;
  border-radius: 4px;
}

.paginator-btn:hover:not(:disabled),
.paginator-page:hover {
  background: #f0f0f0;
}

.paginator-btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.paginator-pages {
  display: flex;
  gap: 0.25rem;
}

.paginator-page.active {
  background: #007bff;
  color: white;
  border-color: #007bff;
}

.paginator-info {
  margin-left: auto;
  font-size: 0.875rem;
  color: #666;
}
</style>
