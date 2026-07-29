import React, { FormEvent } from "react";
import styles from "@/components/css/NewsletterSection.module.css";

const LeafIcon = () => (
  <svg
    className={styles.icon}
    viewBox="0 0 24 24"
    fill="none"
    xmlns="http://www.w3.org/2000/svg"
    aria-hidden="true"
  >
    <path
      d="M12 21c-4.5-3.5-8-7.5-8-12a8 8 0 0 1 16 0c0 4.5-3.5 8.5-8 12Z"
      stroke="currentColor"
      strokeWidth="1.2"
      strokeLinejoin="round"
    />
    <path
      d="M12 21V9M12 9C12 9 9 8 7 5"
      stroke="currentColor"
      strokeWidth="1.2"
      strokeLinecap="round"
    />
  </svg>
);

export const NewsletterSection: React.FC = () => {
  const handleSubmit = (event: FormEvent<HTMLFormElement>) => {
    event.preventDefault();
  };

  return (
    <section className={styles.section}>
      <div className={styles.card}>
        <div className={styles.decorLeft} aria-hidden="true" />
        <div className={styles.decorRight} aria-hidden="true" />

        <div className={styles.content}>
          <LeafIcon />
          <h2 className={styles.title}>Sezonowy List</h2>
          <p className={styles.description}>
            Przewodniki parzenia, nowości ze zbiorów, historie o pochodzeniu
            produktów i wcześniejszy dostęp do nowości. Jeden przemyślany e-mail
            miesięcznie.
          </p>

          <form className={styles.form} onSubmit={handleSubmit}>
            <input
              type="email"
              className={styles.input}
              placeholder="Twój adres e-mail"
              aria-label="Adres e-mail"
            />
            <button type="submit" className={styles.button}>
              Zapisz się
            </button>
          </form>
        </div>
      </div>
    </section>
  );
};
