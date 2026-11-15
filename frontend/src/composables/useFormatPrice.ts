import { useI18n } from "vue-i18n";

/**
 * Format an amount in euros for the current language: "49,90 €" in French, "€49.90" in English.
 * Amounts come from the API as decimal strings ("49.90"), to avoid float rounding on the server.
 */
export function useFormatPrice() {
  const { locale } = useI18n();

  return (amount: string | number | null | undefined): string => {
    const value = Number(amount ?? 0);
    return new Intl.NumberFormat(locale.value, { style: "currency", currency: "EUR" }).format(
      Number.isFinite(value) ? value : 0,
    );
  };
}
