<script setup lang="ts">
import { useI18n } from "vue-i18n";
import { legalConfig } from "@/i18n/legal";

const { t } = useI18n();
</script>

<template>
  <h1>{{ t("privacyPolicy.title") }}</h1>

  <section>
    <h2>{{ t("privacyPolicy.introduction.title") }}</h2>
    <p>{{ t("privacyPolicy.introduction.p1") }}</p>
    <p>{{ t("privacyPolicy.introduction.p2") }}</p>
  </section>

  <section>
    <h2>{{ t("privacyPolicy.dataController.title") }}</h2>
    <p>{{ t("privacyPolicy.dataController.p1") }}</p>

    <p>
      {{ legalConfig.editor.name }}
    </p>

    <p>
      <strong>{{ t("privacyPolicy.dataController.email") }} :</strong>
      <a :href="`mailto:${legalConfig.privacy.dataProtectionEmail}`">
        {{ legalConfig.privacy.dataProtectionEmail }}
      </a>
    </p>
  </section>

  <section>
    <h2>{{ t("privacyPolicy.dataCollected.title") }}</h2>

    <p>{{ t("privacyPolicy.dataCollected.p1") }}</p>

    <ul>
      <li>{{ t("privacyPolicy.dataCollected.account") }}</li>
      <li>{{ t("privacyPolicy.dataCollected.giftLists") }}</li>
      <li>{{ t("privacyPolicy.dataCollected.technical") }}</li>
    </ul>
  </section>

  <section>
    <h2>{{ t("privacyPolicy.purposes.title") }}</h2>

    <ul>
      <li>{{ t("privacyPolicy.purposes.accountManagement") }}</li>
      <li>{{ t("privacyPolicy.purposes.serviceProvision") }}</li>
      <li>{{ t("privacyPolicy.purposes.security") }}</li>
      <li>{{ t("privacyPolicy.purposes.improvement") }}</li>
    </ul>
  </section>

  <section>
    <h2>{{ t("privacyPolicy.authentication.title") }}</h2>
    <p>{{ t("privacyPolicy.authentication.p1") }}</p>
    <p>{{ t("privacyPolicy.authentication.p2") }}</p>
  </section>

  <section>
    <h2>{{ t("privacyPolicy.cookies.title") }}</h2>
    <p>{{ t("privacyPolicy.cookies.p1") }}</p>
    <p>{{ t("privacyPolicy.cookies.p2") }}</p>
  </section>

  <section>
    <h2>{{ t("privacyPolicy.storage.title") }}</h2>
    <p>{{ t("privacyPolicy.storage.p1") }}</p>
    <p>{{ t("privacyPolicy.storage.p2") }}</p>
  </section>

  <section>
    <h2>{{ t("privacyPolicy.rights.title") }}</h2>

    <ul>
      <li>{{ t("privacyPolicy.rights.access") }}</li>
      <li>{{ t("privacyPolicy.rights.rectification") }}</li>
      <li>{{ t("privacyPolicy.rights.deletion") }}</li>
      <li>{{ t("privacyPolicy.rights.restriction") }}</li>
      <li>{{ t("privacyPolicy.rights.portability") }}</li>
    </ul>
  </section>

  <section>
    <h2>{{ t("privacyPolicy.contact.title") }}</h2>

    <p>{{ t("privacyPolicy.contact.p1") }}</p>

    <a :href="`mailto:${legalConfig.privacy.dataProtectionEmail}`">
      {{ legalConfig.privacy.dataProtectionEmail }}
    </a>
  </section>

  <p>
    <small>
      {{
        t("privacyPolicy.lastUpdated", {
          date: legalConfig.lastUpdated,
        })
      }}
    </small>
  </p>
</template>
