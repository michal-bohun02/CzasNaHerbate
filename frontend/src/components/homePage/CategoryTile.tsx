import React from "react";
import { NavLink } from "react-router-dom";
import styles from "@/components/css/CategoryTile.module.css";

export type CategoryVariant =
  | "tea"
  | "coffee"
  | "porcelain"
  | "accessories"
  | "giftSets";

export interface CategoryTileProps {
  title: string;
  subtitle: string;
  to: string;
  variant: CategoryVariant;
  image?: string;
}

export const CategoryTile: React.FC<CategoryTileProps> = ({
  title,
  subtitle,
  to,
  variant,
  image,
}) => {
  return (
    <NavLink
      to={to}
      className={`${styles.tile} ${styles[variant]}`}
    >
      {image && <img src={image} alt="" className={styles.image} />}
      <div className={styles.overlay} />
      <div className={styles.content}>
        <h3 className={styles.title}>{title}</h3>
        <p className={styles.subtitle}>{subtitle}</p>
      </div>
    </NavLink>
  );
};
