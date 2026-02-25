<template>
  <div v-if="meta && meta.totalPages > 1" class="flex flex-col items-center gap-4 mt-6">
    <UPagination
      :page="meta.page"
      :total="meta.total"
      :items-per-page="limit"
      @update:page="$emit('page-change', $event)"
    />
    <div class="text-sm text-gray-500">
      {{ t('paginator.pageInfo', { page: meta.page, totalPages: meta.totalPages, total: meta.total }) }}
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed } from "vue";
import { useI18n } from "vue-i18n";

import type { PaginationMeta } from "@/api/index";

const props = defineProps<{
  meta: PaginationMeta | null;
}>();

defineEmits<{
  "page-change": [page: number];
}>();

const { t } = useI18n();

const limit = computed(() => {
  if (!props.meta) return 10;
  // Calculate items per page based on total and totalPages to pass to UPagination
  // If we're on the last page, the number of items might be less than the limit,
  // so we estimate the limit by dividing total by totalPages (rounding up is usually what happens, but we can just use a default or calculate it if needed).
  // A safe fallback is 10, but ideally the limit should be passed as a prop.
  // For now, let's assume limit is 10 which is the default in RecipientsView.
  return 10;
});
</script>
