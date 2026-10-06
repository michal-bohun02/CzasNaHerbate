import React, { useEffect, useRef, useState } from "react";
import styles from "@/components/css/NavBar.module.css";
import logo from "@/assets/icons/logo.svg";
import { NavLink, useNavigate } from "react-router-dom";
import accountIcon from "@/assets/icons/accountIcon.svg";
import cartIcon from "@/assets/icons/cartIcon.svg";
import searchIcon from "@/assets/icons/searchIcon.svg";
import apiClient from "@/api/client";
import { displayName } from "@/components/catalog/ProductTile";
import { categoryPaths } from "@/utils/search";

type SearchHit = {
  id: number;
  name: string;
  slug: string;
  photo_url: string | null;
  category_name: string | null;
  category_slug: string | null;
};

interface Props {}

export const NavBar: React.FC<Props> = ({}: Props) => {
  const navigate = useNavigate();
  const searchRef = useRef<HTMLFormElement>(null);
  const inputRef = useRef<HTMLInputElement>(null);
  const [isSearchOpen, setIsSearchOpen] = useState(false);
  const [query, setQuery] = useState("");
  const [results, setResults] = useState<SearchHit[]>([]);
  const [searchStatus, setSearchStatus] = useState<"idle" | "loading" | "ready" | "error">("idle");

  useEffect(() => {
    if (isSearchOpen) inputRef.current?.focus();
  }, [isSearchOpen]);

  useEffect(() => {
    if (!isSearchOpen) return;
    const trimmed = query.trim();
    if (trimmed.length < 2) {
      setResults([]);
      setSearchStatus("idle");
      return;
    }

    const controller = new AbortController();
    const timer = window.setTimeout(() => {
      setSearchStatus("loading");
      apiClient
        .get<SearchHit[]>("/items/search", { params: { q: trimmed }, signal: controller.signal })
        .then((response) => {
          setResults(response.data);
          setSearchStatus("ready");
        })
        .catch((error: { code?: string }) => {
          if (controller.signal.aborted || error.code === "ERR_CANCELED") return;
          setSearchStatus("error");
        });
    }, 250);

    return () => {
      controller.abort();
      window.clearTimeout(timer);
    };
  }, [isSearchOpen, query]);

  useEffect(() => {
    if (!isSearchOpen) return;
    const onPointerDown = (event: MouseEvent) => {
      if (!searchRef.current?.contains(event.target as Node)) closeSearch();
    };
    const onKeyDown = (event: KeyboardEvent) => {
      if (event.key === "Escape") closeSearch();
    };
    document.addEventListener("mousedown", onPointerDown);
    document.addEventListener("keydown", onKeyDown);
    return () => {
      document.removeEventListener("mousedown", onPointerDown);
      document.removeEventListener("keydown", onKeyDown);
    };
  }, [isSearchOpen]);

  const closeSearch = () => {
    setIsSearchOpen(false);
    setQuery("");
    setResults([]);
    setSearchStatus("idle");
  };

  const openHit = (hit: SearchHit) => {
    const path = categoryPaths[hit.category_slug ?? ""] ?? "/tea";
    navigate(`${path}?q=${encodeURIComponent(query.trim())}`);
    closeSearch();
  };

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
                to="/herbs"
                className={({ isActive }) => (isActive ? styles.active : "")}
              >
                Zioła
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
                to="/additives"
                className={({ isActive }) => (isActive ? styles.active : "")}
              >
                Dodatki
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
          <form
            ref={searchRef}
            className={`${styles.search} ${isSearchOpen ? styles.searchOpen : ""}`}
            onSubmit={(event) => {
              event.preventDefault();
              if (results[0]) openHit(results[0]);
            }}
          >
            <input
              ref={inputRef}
              type="search"
              className={styles.searchInput}
              placeholder="Szukaj..."
              aria-label="Szukaj"
              aria-controls="search-results"
              aria-expanded={isSearchOpen && query.trim().length >= 2}
              tabIndex={isSearchOpen ? 0 : -1}
              value={query}
              onChange={(event) => setQuery(event.target.value)}
            />
            <button
              type="button"
              className={styles.searchToggle}
              onClick={() => {
                if (isSearchOpen) closeSearch();
                else setIsSearchOpen(true);
              }}
              aria-expanded={isSearchOpen}
              aria-label={isSearchOpen ? "Zamknij wyszukiwanie" : "Otwórz wyszukiwanie"}
            >
              <img src={searchIcon} alt="" />
            </button>
            {isSearchOpen && query.trim().length >= 2 && (
              <div id="search-results" className={styles.results} role="listbox">
                {searchStatus === "loading" && <p className={styles.resultStatus}>Szukam…</p>}
                {searchStatus === "error" && (
                  <p className={styles.resultStatus}>Nie udało się wyszukać.</p>
                )}
                {searchStatus === "ready" && results.length === 0 && (
                  <p className={styles.resultStatus}>Brak wyników.</p>
                )}
                {results.map((hit) => (
                  <button
                    key={hit.id}
                    type="button"
                    className={styles.result}
                    role="option"
                    onClick={() => openHit(hit)}
                  >
                    {hit.photo_url ? (
                      <img src={hit.photo_url} alt="" />
                    ) : (
                      <span className={styles.resultPhoto} />
                    )}
                    <span>
                      <span className={styles.resultName}>{displayName(hit.name)}</span>
                      {hit.category_name && (
                        <span className={styles.resultCategory}>{hit.category_name}</span>
                      )}
                    </span>
                  </button>
                ))}
              </div>
            )}
          </form>
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
