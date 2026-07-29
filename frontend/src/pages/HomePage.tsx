import React from "react";
import styles from "./css/HomePage.module.css";
import { CategoryTilesSection } from "@/components/homePage/CategoryTilesSection";
import { NewsletterSection } from "@/components/homePage/NewsletterSection";
import { smoothScrollToElement } from "@/utils/smoothScroll";

interface Props {}

export const HomePage: React.FC<Props> = ({}: Props) => {
  const scrollToShop = () => {
    const shopSection = document.getElementById("shop");
    if (shopSection) {
      smoothScrollToElement(shopSection);
    }
  };

  return (
    <div className={styles.mainContainer}>
      <div className={styles.picBG}>
        <div className={styles.mainTitleContainer}>
          <div className={styles.mainTitle}>
            <span className={styles.titleLine1}>Sztuka</span>
            <br />
            <span className={styles.titleLine2}>idealnej filiżanki</span>
          </div>
          <div className={styles.underTitle}>
            <span>
              Rzadkie herbaty, kawy segmentu specialty i ręcznie wytwarzana
              porcelana – sprowadzane bezpośrednio od najlepszych światowych
              producentów.
            </span>
          </div>
          <div className={styles.buttons}>
            <button type="button" className={styles.btnShop} onClick={scrollToShop}>
              Do Sklepu
            </button>
            <button className={styles.btnSets}>Zobacz Zestawy</button>
          </div>
        </div>
      </div>
      <CategoryTilesSection />
      <NewsletterSection />
    </div>
  );
};
