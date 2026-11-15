<template>
  <figure class="flex flex-col items-center gap-4">
    <svg :width="size" :height="size" :viewBox="`0 0 ${size} ${size}`" role="img" :aria-label="ariaLabel">
      <!-- Remaining: full ring underneath -->
      <circle
        :cx="center"
        :cy="center"
        :r="radius"
        fill="none"
        :stroke="REMAINING_COLOR"
        :stroke-width="strokeWidth"
      />
      <!-- Spent: arc drawn on top, starting at 12 o'clock -->
      <circle
        v-if="spentRatio > 0"
        :cx="center"
        :cy="center"
        :r="radius"
        fill="none"
        :stroke="SPENT_COLOR"
        :stroke-width="strokeWidth"
        :stroke-dasharray="`${spentRatio * circumference} ${circumference}`"
        :transform="`rotate(-90 ${center} ${center})`"
      />
      <text
        :x="center"
        :y="center"
        text-anchor="middle"
        dominant-baseline="central"
        class="fill-current font-decorative text-2xl"
      >
        {{ Math.round(spentRatio * 100) }}&nbsp;%
      </text>
    </svg>

    <figcaption class="flex flex-wrap justify-center gap-x-6 gap-y-2 text-sm">
      <span class="flex items-center gap-2">
        <span class="size-3 rounded-full" :style="{ backgroundColor: SPENT_COLOR }" aria-hidden="true" />
        {{ spentLabel }}
      </span>
      <span class="flex items-center gap-2">
        <span class="size-3 rounded-full" :style="{ backgroundColor: REMAINING_COLOR }" aria-hidden="true" />
        {{ remainingLabel }}
      </span>
    </figcaption>
  </figure>
</template>

<script setup lang="ts">
import { computed } from "vue";

/**
 * Spent vs remaining budget, as a two-slice donut.
 * Plain SVG on purpose: a chart library weighed ~600 kB for these two arcs.
 */
const props = withDefaults(
  defineProps<{
    spent: number;
    budget: number;
    spentLabel: string;
    remainingLabel: string;
    size?: number;
    strokeWidth?: number;
  }>(),
  { size: 200, strokeWidth: 25 },
);

const SPENT_COLOR = "#f97316";
const REMAINING_COLOR = "#22c55e";

const center = computed(() => props.size / 2);
const radius = computed(() => (props.size - props.strokeWidth) / 2);
const circumference = computed(() => 2 * Math.PI * radius.value);

// Clamped to [0, 1]: an overspent budget shows a full "spent" ring.
const spentRatio = computed(() => {
  if (props.budget <= 0) return 0;
  return Math.min(Math.max(props.spent / props.budget, 0), 1);
});

const ariaLabel = computed(
  () => `${props.spentLabel}: ${Math.round(spentRatio.value * 100)} %, ${props.remainingLabel}: ${100 - Math.round(spentRatio.value * 100)} %`,
);
</script>
