import React, { useState } from "react";
import styles from "@/components/css/ProductTile.module.css";
import type { CatalogItem } from "@/components/catalog/filterConfig";

interface Props {
  item: CatalogItem;
  categoryName: string;
  layout?: "tiles" | "rows";
}

export const ProductTile: React.FC<Props> = ({ item, categoryName, layout = "tiles" }) => {
  const [saved, setSaved] = useState(false);
  const price = formatPrice(item.price);
  const row = layout === "rows";

  return (
    <article className={`${styles.tile} ${row ? styles.row : ""}`}>
      <button
        type="button"
        className={`${styles.heart} ${saved ? styles.heartOn : ""}`}
        aria-pressed={saved}
        aria-label={saved ? "Usuń z zapisanych" : "Zapisz"}
        onClick={() => setSaved((current) => !current)}
      >
        <HeartIcon filled={saved} />
      </button>
      <div className={styles.media}>
        {item.photo_url ? (
          <img src={item.photo_url} alt={displayName(item.name)} />
        ) : (
          <div className={styles.placeholder} />
        )}
      </div>
      <div className={styles.body}>
        <p className={styles.eyebrow}>{categoryName}</p>
        <h3 className={styles.name}>{displayName(item.name)}</h3>
        {row && item.description && <p className={styles.description}>{item.description}</p>}
        <div className={styles.types}>
          {item.badges.some((badge) => badge.source === "category") && (
            <span className={styles.typeLabel}>Typ</span>
          )}
          {item.badges.map((badge) => (
            <span key={badge.id} className={styles.pill}>
              {badge.name}
            </span>
          ))}
        </div>
        {price && <p className={styles.price}>{price}</p>}
      </div>
    </article>
  );
};

export function displayName(name: string) {
  const cleaned = name
    .replace(/\d{3,4}\s*[xX]\s*\d{3,4}/g, " ")
    .replace(/\[[^\]]*\]/g, " ")
    .replace(/\b(xl|ec)\b/gi, " ")
    .replace(/[-_]+/g, " ")
    .replace(/\s+/g, " ")
    .trim();
  if (!cleaned) return cleaned;
  const letters = cleaned.replace(/[^\p{L}]/gu, "");
  const normalized =
    letters && letters === letters.toLocaleUpperCase("pl-PL")
      ? cleaned.toLocaleLowerCase("pl-PL")
      : cleaned;
  return normalized.charAt(0).toLocaleUpperCase("pl-PL") + normalized.slice(1);
}

function formatPrice(value: string | number | null) {
  if (value == null || value === "") return null;
  const amount = Number(value);
  if (Number.isNaN(amount)) return null;
  return `${amount.toLocaleString("pl-PL", {
    minimumFractionDigits: Number.isInteger(amount) ? 0 : 2,
    maximumFractionDigits: 2,
  })} zł`;
}

const HeartIcon: React.FC<{ filled: boolean }> = ({ filled }) => (
  <svg viewBox="0 0 24 24" aria-hidden="true">
    <path
      d="M12 19.4c-.3 0-6.8-4.1-8.2-7.6C2.7 9.4 3.6 6.6 6.2 5.8c1.5-.5 3.1 0 4.1 1.2.4.5 1 .5 1.4 0 1-1.2 2.6-1.7 4.1-1.2 2.6.8 3.5 3.6 2.4 5.9-1.4 3.6-7.9 7.7-8.2 7.7z"
      fill={filled ? "currentColor" : "none"}
      stroke="currentColor"
      strokeWidth="1.6"
      strokeLinejoin="round"
    />
  </svg>
);
