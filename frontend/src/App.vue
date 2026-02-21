<template>
  <UApp :toaster="toaster">
    <RouterView />
  </UApp>
</template>

<script setup lang="ts">
import { RouterView } from "vue-router";

const toaster = { position: "top-center" as const };
</script>
