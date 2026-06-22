<template>
  <div v-if="password" :style="{ '--pw-color': passwordColorValue }">
    <UProgress
      :model-value="passwordScore"
      :max="5"
      :indicator="passwordText"
      size="sm"
      :ui="{ indicator: 'bg-[var(--pw-color)] transition-[background-color] duration-300' }"
    />
    <p class="text-xs pb-0.5 pt-2">
      {{ passwordText }}. {{ t("auth.passwordStrength.mustContain") }}
    </p>
    <ul class="space-y-1">
      <li
        v-for="(req, index) in passwordRequirements"
        :key="index"
        class="flex items-center gap-0.5"
        :class="req.met ? 'text-success' : 'text-muted'"
      >
        <UIcon
          :name="req.met ? 'i-lucide-circle-check' : 'i-lucide-circle-x'"
          class="size-4 shrink-0"
        />
        <span class="text-xs">&nbsp;{{ req.text }}</span>
      </li>
    </ul>
  </div>
</template>

<script setup lang="ts">
import { computed } from "vue";
import { useI18n } from "vue-i18n";

interface Props {
  password: string | undefined;
}

const props = defineProps<Props>();
const { t } = useI18n();

const passwordRequirements = computed(() => {
  const password = props.password || "";
  return [
    {
      regex: /.{8,}/,
      text: t("auth.passwordStrength.requirement8Chars"),
      met: /.{8,}/.test(password),
    },
    { regex: /\d/, text: t("auth.passwordStrength.requirement1Number"), met: /\d/.test(password) },
    {
      regex: /[a-z]/,
      text: t("auth.passwordStrength.requirement1Lowercase"),
      met: /[a-z]/.test(password),
    },
    {
      regex: /[A-Z]/,
      text: t("auth.passwordStrength.requirement1Uppercase"),
      met: /[A-Z]/.test(password),
    },
    {
      regex: /[^A-Za-z0-9\s]/,
      text: t("auth.passwordStrength.requirement1Special"),
      met: /[^A-Za-z0-9\s]/.test(password),
    },
  ];
});

const passwordScore = computed(() => {
  return passwordRequirements.value.filter((req) => req.met).length;
});

const passwordColorValue = computed(() => {
  const score = passwordScore.value;
  if (score === 0) return "oklch(55% 0 0)";
  if (score === 1) return "oklch(55% 0.2 25)";
  if (score === 2) return "oklch(65% 0.18 50)";
  if (score === 3) return "oklch(75% 0.15 85)";
  if (score === 4) return "oklch(75% 0.16 110)";
  return "oklch(75% 0.19 145)";
});

const passwordText = computed(() => {
  const score = passwordScore.value;
  if (score === 0) return t("auth.passwordStrength.enterPassword");
  if (score <= 2) return t("auth.passwordStrength.weakPassword");
  if (score <= 3) return t("auth.passwordStrength.mediumPassword");
  return t("auth.passwordStrength.strongPassword");
});
</script>
