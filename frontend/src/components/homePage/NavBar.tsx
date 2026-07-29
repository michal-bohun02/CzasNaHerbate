import React, { useState } from "react";
import styles from "@/components/css/NavBar.module.css";
import logo from "@/assets/icons/logo.svg";
import { NavLink } from "react-router-dom";
import accountIcon from "@/assets/icons/accountIcon.svg";
import cartIcon from "@/assets/icons/cartIcon.svg";
import searchIcon from "@/assets/icons/searchIcon.svg";

interface Props {}

export const NavBar: React.FC<Props> = ({}: Props) => {
  const [isSearchOpen, setIsSearchOpen] = useState(false);

  return (
    <div className={styles.navBar}>
      <div className={styles.container}>
        <div className={styles.logo}>
          <NavLink to="/">
            <img src={logo} alt="logo" />
          </NavLink>
        </div>
        <div className={styles.sites}>
          <ul className={styles.navLinks}>
            <li>
              <NavLink
                to="/tea"
                className={({ isActive }) => (isActive ? styles.active : "")}
              >
                Herbata
              </NavLink>
            </li>
            <li>
              <NavLink
                to="/coffee"
                className={({ isActive }) => (isActive ? styles.active : "")}
              >
                Kawa
              </NavLink>
            </li>
            <li>
              <NavLink
                to="/porcelain"
                className={({ isActive }) => (isActive ? styles.active : "")}
              >
                Porcelana
              </NavLink>
            </li>
            <li>
              <NavLink
                to="/accessories"
                className={({ isActive }) => (isActive ? styles.active : "")}
              >
                Akcesoria
              </NavLink>
            </li>
            <li>
              <NavLink
                to="/gift-sets"
                className={({ isActive }) => (isActive ? styles.active : "")}
              >
                Zestawy Prezentowe
              </NavLink>
            </li>
          </ul>
        </div>
        <div className={styles.icons}>
          <div
            className={`${styles.search} ${isSearchOpen ? styles.searchOpen : ""}`}
          >
            <input
              type="text"
              className={styles.searchInput}
              placeholder="Szukaj..."
              aria-label="Szukaj"
              tabIndex={isSearchOpen ? 0 : -1}
              readOnly
            />
            <button
              type="button"
              className={styles.searchToggle}
              onClick={() => setIsSearchOpen((open) => !open)}
              aria-expanded={isSearchOpen}
              aria-label={isSearchOpen ? "Zamknij wyszukiwanie" : "Otwórz wyszukiwanie"}
            >
              <img src={searchIcon} alt="" />
            </button>
          </div>
          <NavLink
            to="/account"
            className={({ isActive }) => (isActive ? styles.active : "")}
          >
            <img src={accountIcon} alt="account" />
          </NavLink>
          <NavLink
            to="/cart"
            className={({ isActive }) => (isActive ? styles.active : "")}
          >
            <img src={cartIcon} alt="cart" />
          </NavLink>
        </div>
      </div>
    </div>
  );
};
