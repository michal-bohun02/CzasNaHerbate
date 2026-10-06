import React from "react";
import { NavLink } from "react-router-dom";
import styles from "@/components/css/Footer.module.css";
import logo from "@/assets/icons/logo.svg";

const shopLinks = [
  { label: "Herbata", to: "/tea" },
  { label: "Zioła", to: "/herbs" },
  { label: "Kawa", to: "/coffee" },
  { label: "Dodatki", to: "/additives" },
  { label: "Porcelana", to: "/porcelain" },
  { label: "Akcesoria", to: "/accessories" },
  { label: "Zestawy Prezentowe", to: "/gift-sets" },
];

const helpLinks = [
  { label: "Kontakt", to: "/contact" },
  { label: "Zwroty", to: "/returns" },
  { label: "Przewodniki parzenia", to: "/brewing-guides" },
];

export const Footer: React.FC = () => {
  return (
    <footer className={styles.footer}>
      <div className={styles.container}>
        <div className={styles.columns}>
          <div className={styles.brand}>
            <NavLink to="/" className={styles.logoLink}>
              <img src={logo} alt="Czas na Herbatę" className={styles.logo} />
            </NavLink>
            <p className={styles.tagline}>
              Rzadkie herbaty, kawy specialty i ręcznie wytwarzana porcelana —
              prosto od najlepszych producentów.
            </p>
          </div>

          <div className={styles.column}>
            <h3 className={styles.columnTitle}>Sklep</h3>
            <ul className={styles.links}>
              {shopLinks.map((link) => (
                <li key={link.to}>
                  <NavLink to={link.to}>{link.label}</NavLink>
                </li>
              ))}
            </ul>
          </div>

          <div className={styles.column}>
            <h3 className={styles.columnTitle}>Pomoc</h3>
            <ul className={styles.links}>
              {helpLinks.map((link) => (
                <li key={link.to}>
                  <NavLink to={link.to}>{link.label}</NavLink>
                </li>
              ))}
            </ul>
          </div>
        </div>

        <div className={styles.bottom}>
          <span className={styles.copyright}>
            © {new Date().getFullYear()} Czas na Herbatę. Wszelkie prawa
            zastrzeżone.
          </span>
        </div>
      </div>
    </footer>
  );
};
