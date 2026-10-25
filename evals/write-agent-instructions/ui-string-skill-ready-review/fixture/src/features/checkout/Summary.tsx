import { useTranslation } from "react-i18next";

export function Summary({ total, count }: { total: string; count: number }) {
  const { t } = useTranslation("checkout");
  return (
    <div>
      <p>{t("summary.itemCount", { count })}</p>
      <p>
        {t("summary.totalLabel")}: {total}
      </p>
      <button>{t("payNow")}</button>
    </div>
  );
}
