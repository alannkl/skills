import { useTranslation } from "react-i18next";

export function Profile({ email }: { email: string }) {
  const { t } = useTranslation("account");
  return (
    <section>
      <h1>{t("profile.title")}</h1>
      <p>
        {t("profile.emailLabel")}: {email}
      </p>
    </section>
  );
}
