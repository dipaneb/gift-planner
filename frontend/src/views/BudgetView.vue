<template>
  <div class="flex flex-col gap-6">
    <h1>{{ t('budget.title') }}</h1>

    <UCard>
      <template #header>
        <h2>{{ t('budget.overview') }}</h2>
      </template>

      <div class="flex flex-col gap-6">
        <div class="grid grid-cols-1 md:grid-cols-3 gap-4">
          <div
            class="bg-linear-to-br from-gray-50 to-gray-100 border border-gray-200 rounded-xl p-6 text-center transition-transform hover:-translate-y-1 hover:shadow-lg"
          >
            <div class="text-xs font-semibold text-gray-600 uppercase tracking-wide mb-2">
              {{ t('budget.totalBudget') }}
            </div>
            <div
              class="text-3xl font-bold"
              :class="!authStore.user?.budget ? 'text-gray-400 italic' : 'text-gray-900'"
            >
              {{ authStore.user?.budget ? `${authStore.user.budget} €` : t('common.notSet') }}
            </div>
          </div>

          <div
            class="bg-linear-to-br from-orange-50 to-orange-100 border border-orange-200 rounded-xl p-6 text-center transition-transform hover:-translate-y-1 hover:shadow-lg"
          >
            <div class="text-xs font-semibold text-orange-700 uppercase tracking-wide mb-2">
              {{ t('budget.spent') }}
            </div>
            <div class="text-3xl font-bold text-orange-600">
              {{ authStore.user?.spent || "0.00" }} €
            </div>
          </div>

          <div
            class="bg-linear-to-br from-gray-50 to-gray-100 border rounded-xl p-6 text-center transition-transform hover:-translate-y-1 hover:shadow-lg"
            :class="remainingColorClass"
          >
            <div
              class="text-xs font-semibold uppercase tracking-wide mb-2"
              :class="remainingLabelClass"
            >
              {{ t('budget.remaining') }}
            </div>
            <div class="text-3xl font-bold" :class="remainingValueClass">
              {{ remainingDisplay }}
            </div>
          </div>
        </div>

        <div v-if="authStore.user?.budget && showChart" class="flex justify-center py-4">
          <DonutChart
            :data="chartData"
            :height="250"
            :categories="categories"
            :radius="10"
            :arc-width="25"
            :pad-angle="0.05"
            :legend-position="LegendPosition.BottomCenter"
          />
        </div>

        <USeparator />

        <UForm
          :schema="budgetSchema"
          :state="budgetForm"
          @submit="handleSubmit"
          class="flex flex-col gap-4"
        >
          <UAlert v-if="error" :title="error" color="error" variant="subtle" />
          <UAlert v-if="successMessage" :title="successMessage" color="success" variant="subtle" />

          <UFormField :label="t('budget.budgetField')" name="budget" required>
            <UInputNumber
              v-model="budgetForm.budget"
              :min="0"
              placeholder="e.g. 500.00"
              :format-options="{
                style: 'currency',
                currency: 'EUR',
                currencyDisplay: 'symbol',
              }"
              class="w-full max-w-sm"
            />
          </UFormField>

          <div class="flex gap-2">
            <UButton type="submit" color="primary" :loading="loading"> {{ t('budget.setBudget') }} </UButton>
            <UButton
              type="button"
              color="error"
              variant="outline"
              :disabled="loading || !authStore.user?.budget"
              @click="handleDelete"
            >
              {{ t('budget.removeBudget') }}
            </UButton>
          </div>
        </UForm>
      </div>
    </UCard>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, reactive } from "vue";
import { useI18n } from "vue-i18n";
import { z } from "zod";
import type { FormSubmitEvent } from "@nuxt/ui";
import { DonutChart, type BulletLegendItemInterface, LegendPosition } from "vue-chrts";
import { useAuthStore } from "@/stores/auth";
import { useBudget } from "@/composables/useBudget";

const { t } = useI18n();
const authStore = useAuthStore();
const { loading, error, updateBudget, deleteBudget } = useBudget();

const budgetSchema = computed(() => z.object({
  budget: z.number().positive(t('validation.budgetPositive')),
}));

type BudgetSchema = z.output<typeof budgetSchema.value>;

const budgetForm = reactive<Partial<BudgetSchema>>({
  budget: authStore.user?.budget ? parseFloat(authStore.user.budget) : undefined,
});

const successMessage = ref<string | null>(null);

const remainingDisplay = computed(() => {
  if (!authStore.user?.budget) return t('common.na');
  if (authStore.user.remaining === null) return t('common.na');
  return `${authStore.user.remaining} €`;
});

const remainingColorClass = computed(() => {
  if (!authStore.user?.budget || authStore.user.remaining === null) {
    return "border-gray-200";
  }
  const remaining = parseFloat(authStore.user.remaining);
  if (remaining < 0) return "border-red-200";
  if (remaining === 0) return "border-gray-300";
  return "border-green-200";
});

const remainingLabelClass = computed(() => {
  if (!authStore.user?.budget || authStore.user.remaining === null) {
    return "text-gray-600";
  }
  const remaining = parseFloat(authStore.user.remaining);
  if (remaining < 0) return "text-red-700";
  if (remaining === 0) return "text-gray-600";
  return "text-green-700";
});

const remainingValueClass = computed(() => {
  if (!authStore.user?.budget || authStore.user.remaining === null) {
    return "text-gray-400 italic";
  }
  const remaining = parseFloat(authStore.user.remaining);
  if (remaining < 0) return "text-red-600";
  if (remaining === 0) return "text-gray-500";
  return "text-green-600";
});

// Chart data with edge case handling
const chartData = computed(() => {
  const spent = parseFloat(authStore.user?.spent || "0");
  const budget = parseFloat(authStore.user?.budget || "0");

  // If no budget set, return empty data
  if (budget <= 0) return [0, 100];

  // If spent exceeds budget, show 100% spent
  if (spent >= budget) return [budget, 0];

  // Normal case: show spent and remaining
  const remaining = budget - spent;
  return [spent, remaining > 0 ? remaining : 0];
});

const showChart = computed(() => {
  const budget = parseFloat(authStore.user?.budget || "0");
  return budget > 0;
});

type DonutCategories = Record<string, BulletLegendItemInterface>;

const labels = computed(() => [
  { name: t('budget.chartSpent'), color: "#f97316" },
  { name: t('budget.chartRemaining'), color: "#22c55e" },
]);

const categories = computed<DonutCategories>(() => Object.fromEntries(
  labels.value.map((i) => [i.name, { name: i.name, color: i.color }]),
));

function clearMessages() {
  successMessage.value = null;
  error.value = null;
}

async function handleSubmit(event: FormSubmitEvent<BudgetSchema>) {
  clearMessages();

  const ok = await updateBudget(event.data.budget);
  if (ok) {
    successMessage.value = t('budget.budgetUpdated');
  }
}

async function handleDelete() {
  clearMessages();

  const ok = await deleteBudget();
  if (ok) {
    budgetForm.budget = undefined;
    successMessage.value = t('budget.budgetRemoved');
  }
}
</script>
