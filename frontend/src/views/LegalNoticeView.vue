<script setup lang="ts">
import { useI18n } from "vue-i18n";
import { legalConfig } from "@/config/legal";

const { t } = useI18n();
</script>

<template>
  <h1>{{ t("legalNotice.title") }}</h1>

  <section>
    <h2>{{ t("legalNotice.editor.title") }}</h2>

    <p>{{ t("legalNotice.editor.intro") }}</p>

    <p>
      <strong>{{ t("legalNotice.editor.name") }} :</strong>
      {{ legalConfig.editor.name }}
    </p>

    <p v-if="legalConfig.editor.legalForm">
      <strong>{{ t("legalNotice.editor.legalForm") }} :</strong>
      {{ legalConfig.editor.legalForm }}
    </p>

    <p>
      <strong>{{ t("legalNotice.editor.address") }} :</strong>
      {{ legalConfig.editor.address }}
    </p>

    <p v-if="legalConfig.editor.siret">
      <strong>{{ t("legalNotice.editor.siret") }} :</strong>
      {{ legalConfig.editor.siret }}
    </p>

    <p>
      <strong>{{ t("legalNotice.editor.email") }} :</strong>

      <a :href="`mailto:${legalConfig.editor.email}`">
        {{ legalConfig.editor.email }}
      </a>
    </p>
  </section>

  <section>
    <h2>{{ t("legalNotice.publicationDirector.title") }}</h2>

    <p>{{ legalConfig.publicationDirector }}</p>
  </section>

  <section>
    <h2>{{ t("legalNotice.hosting.title") }}</h2>

    <p>
      <strong>{{ t("legalNotice.hosting.name") }} :</strong>
      {{ legalConfig.hosting.name }}
    </p>

    <p>
      <strong>{{ t("legalNotice.hosting.address") }} :</strong>
      {{ legalConfig.hosting.address }}
    </p>

    <p>
      <strong>{{ t("legalNotice.hosting.phone") }} :</strong>
      {{ legalConfig.hosting.phone }}
    </p>
  </section>

  <section>
    <h2>{{ t("legalNotice.intellectualProperty.title") }}</h2>

    <p>{{ t("legalNotice.intellectualProperty.p1") }}</p>
    <p>{{ t("legalNotice.intellectualProperty.p2") }}</p>
    <p>{{ t("legalNotice.intellectualProperty.p3") }}</p>
  </section>

  <section>
    <h2>{{ t("legalNotice.liability.title") }}</h2>

    <p>{{ t("legalNotice.liability.p1") }}</p>
    <p>{{ t("legalNotice.liability.p2") }}</p>
    <p>{{ t("legalNotice.liability.p3") }}</p>
  </section>

  <section>
    <h2>{{ t("legalNotice.externalLinks.title") }}</h2>

    <p>{{ t("legalNotice.externalLinks.p1") }}</p>
  </section>

  <section>
    <h2>{{ t("legalNotice.applicableLaw.title") }}</h2>

    <p>{{ t("legalNotice.applicableLaw.p1") }}</p>
  </section>

  <p>
    <small>
      {{
        t("legalNotice.lastUpdated", {
          date: legalConfig.lastUpdated,
        })
      }}
    </small>
  </p>
</template>