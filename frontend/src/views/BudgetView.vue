<template>
  <div class="flex flex-col gap-6">
    <h1>{{ t("budget.title") }}</h1>

    <UCard>
      <template #header>
        <h2>{{ t("budget.overview") }}</h2>
      </template>

      <div class="flex flex-col gap-6">
        <div class="grid grid-cols-1 md:grid-cols-3 gap-4">
          <div
            class="bg-linear-to-br from-gray-50 to-gray-100 border border-gray-200 rounded-xl p-6 text-center transition-transform hover:-translate-y-1 hover:shadow-lg"
          >
            <div class="text-xs text-gray-600 uppercase tracking-wide mb-2 font-decorative">
              {{ t("budget.totalBudget") }}
            </div>
            <div
              class="text-3xl font-decorative"
              :class="!authStore.user?.budget ? 'text-gray-400 italic' : 'text-gray-900'"
            >
              {{ authStore.user?.budget ? formatPrice(authStore.user.budget) : t("common.notSet") }}
            </div>
          </div>

          <div
            class="bg-linear-to-br from-orange-50 to-orange-100 border border-orange-200 rounded-xl p-6 text-center transition-transform hover:-translate-y-1 hover:shadow-lg"
          >
            <div class="text-xs text-orange-700 uppercase tracking-wide mb-2 font-decorative">
              {{ t("budget.spent") }}
            </div>
            <div class="text-3xl text-orange-600 font-decorative">
              {{ formatPrice(authStore.user?.spent) }}
            </div>
          </div>

          <div
            class="bg-linear-to-br from-gray-50 to-gray-100 border rounded-xl p-6 text-center transition-transform hover:-translate-y-1 hover:shadow-lg"
            :class="remainingColorClass"
          >
            <div
              class="text-xs uppercase tracking-wide mb-2 font-decorative"
              :class="remainingLabelClass"
            >
              {{ t("budget.remaining") }}
            </div>
            <div class="text-3xl font-decorative" :class="remainingValueClass">
              {{ remainingDisplay }}
            </div>
          </div>
        </div>

        <div v-if="authStore.user?.budget && showChart" class="flex justify-center py-4">
          <BudgetDonut
            :spent="parseFloat(authStore.user.spent || '0')"
            :budget="parseFloat(authStore.user.budget)"
            :spent-label="t('budget.chartSpent')"
            :remaining-label="t('budget.chartRemaining')"
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
            <UButton type="submit" color="primary" :loading="loading">
              {{ t("budget.setBudget") }}
            </UButton>
            <UButton
              type="button"
              color="error"
              variant="outline"
              :disabled="loading || !authStore.user?.budget"
              @click="handleDelete"
            >
              {{ t("budget.removeBudget") }}
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
import BudgetDonut from "@/components/BudgetDonut.vue";
import { useAuthStore } from "@/stores/auth";
import { useBudget } from "@/composables/useBudget";
import { useFormatPrice } from "@/composables/useFormatPrice";

const { t } = useI18n();
const formatPrice = useFormatPrice();
const authStore = useAuthStore();
const { loading, error, updateBudget, deleteBudget } = useBudget();

const budgetSchema = computed(() =>
  z.object({
    budget: z.number().positive(t("validation.budgetPositive")),
  }),
);

type BudgetSchema = z.output<typeof budgetSchema.value>;

const budgetForm = reactive<Partial<BudgetSchema>>({
  budget: authStore.user?.budget ? parseFloat(authStore.user.budget) : undefined,
});

const successMessage = ref<string | null>(null);

const remainingDisplay = computed(() => {
  if (!authStore.user?.budget) return t("common.na");
  if (authStore.user.remaining === null) return t("common.na");
  return formatPrice(authStore.user.remaining);
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

const showChart = computed(() => {
  const budget = parseFloat(authStore.user?.budget || "0");
  return budget > 0;
});

function clearMessages() {
  successMessage.value = null;
  error.value = null;
}

async function handleSubmit(event: FormSubmitEvent<BudgetSchema>) {
  clearMessages();

  const ok = await updateBudget(event.data.budget);
  if (ok) {
    successMessage.value = t("budget.budgetUpdated");
  }
}

async function handleDelete() {
  clearMessages();

  const ok = await deleteBudget();
  if (ok) {
    budgetForm.budget = undefined;
    successMessage.value = t("budget.budgetRemoved");
  }
}
</script>
