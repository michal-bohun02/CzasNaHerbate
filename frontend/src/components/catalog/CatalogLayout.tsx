import React, { useEffect, useState } from "react";
import { Link, useSearchParams } from "react-router-dom";
import styles from "@/components/css/CatalogLayout.module.css";
import apiClient from "@/api/client";
import { CategoryFilters, type SelectedFilters } from "@/components/catalog/CategoryFilters";
import { displayName, ProductTile } from "@/components/catalog/ProductTile";
import type { CatalogItem, CategoryFiltersResponse } from "@/components/catalog/filterConfig";
import { textMatchesQuery } from "@/utils/search";

type SortKey = "default" | "name-asc" | "name-desc" | "price-asc" | "price-desc";
type ViewMode = "tiles" | "rows";

const EMPTY_GROUPS: CategoryFiltersResponse["groups"] = [];

interface Props {
  slug: string;
}

export const CatalogLayout: React.FC<Props> = ({ slug }) => {
  const [category, setCategory] = useState<CategoryFiltersResponse | null>(null);
  const [items, setItems] = useState<CatalogItem[]>([]);
  const [status, setStatus] = useState<"loading" | "ready" | "error">("loading");
  const [itemsStatus, setItemsStatus] = useState<"loading" | "ready" | "error">("loading");
  const [selected, setSelected] = useState<SelectedFilters>({});
  const [priceMin, setPriceMin] = useState("");
  const [priceMax, setPriceMax] = useState("");
  const [sort, setSort] = useState<SortKey>("default");
  const [view, setView] = useState<ViewMode>("tiles");
  const [searchParams, setSearchParams] = useSearchParams();
  const query = searchParams.get("q")?.trim() ?? "";

  useEffect(() => {
    let cancelled = false;
    setStatus("loading");
    setItemsStatus("loading");
    setCategory(null);
    setItems([]);
    setSelected({});
    setPriceMin("");
    setPriceMax("");

    Promise.allSettled([
      apiClient.get<CategoryFiltersResponse>(`/categories/${slug}/filters`),
      apiClient.get<CatalogItem[]>(`/categories/${slug}/items`),
    ]).then(([filtersResult, itemsResult]) => {
      if (cancelled) return;
      if (filtersResult.status === "fulfilled") {
        setCategory(filtersResult.value.data);
        setStatus("ready");
      } else {
        setStatus("error");
      }
      if (itemsResult.status === "fulfilled") {
        setItems(itemsResult.value.data);
        setItemsStatus("ready");
      } else {
        setItemsStatus("error");
      }
    });

    return () => {
      cancelled = true;
    };
  }, [slug]);

  const visible = sortItems(
    items.filter(
      (item) =>
        matches(item, selected, priceMin, priceMax) &&
        (textMatchesQuery(item.name, query) || textMatchesQuery(item.description, query)),
    ),
    sort,
  );

  return (
    <div className={styles.page}>
      <nav className={styles.breadcrumb} aria-label="Ścieżka">
        <Link to="/">Strona główna</Link>
        <span aria-hidden="true">/</span>
        <span>{category?.name ?? "…"}</span>
      </nav>
      <h1 className={styles.heading}>{category?.name ?? ""}</h1>
      <div className={styles.layout}>
        <CategoryFilters
          key={slug}
          groups={category?.groups ?? EMPTY_GROUPS}
          priceMinHint={category?.price_min ?? null}
          priceMaxHint={category?.price_max ?? null}
          status={status}
          onChange={(nextSelected, nextMin, nextMax) => {
            setSelected(nextSelected);
            setPriceMin(nextMin);
            setPriceMax(nextMax);
          }}
        />
        <div className={styles.products}>
          {itemsStatus === "ready" && query && (
            <p className={styles.searchNote}>
              Wyniki dla „{query}”
              <button
                type="button"
                onClick={() => {
                  const next = new URLSearchParams(searchParams);
                  next.delete("q");
                  setSearchParams(next, { replace: true });
                }}
              >
                Wyczyść
              </button>
            </p>
          )}
          {itemsStatus === "ready" && (
            <div className={styles.toolbar}>
              <label className={styles.sortLabel} htmlFor="catalog-sort">
                Sortuj:
              </label>
              <select
                id="catalog-sort"
                className={styles.sort}
                value={sort}
                onChange={(event) => setSort(event.target.value as SortKey)}
              >
                <option value="default">Domyślnie</option>
                <option value="name-asc">Nazwa: A–Z</option>
                <option value="name-desc">Nazwa: Z–A</option>
                <option value="price-asc">Cena: rosnąco</option>
                <option value="price-desc">Cena: malejąco</option>
              </select>
              <div className={styles.views}>
                <button
                  type="button"
                  className={`${styles.viewButton} ${view === "tiles" ? styles.viewButtonActive : ""}`}
                  aria-pressed={view === "tiles"}
                  aria-label="Kafelki"
                  onClick={() => setView("tiles")}
                >
                  <GridIcon />
                </button>
                <button
                  type="button"
                  className={`${styles.viewButton} ${view === "rows" ? styles.viewButtonActive : ""}`}
                  aria-pressed={view === "rows"}
                  aria-label="Rzędy"
                  onClick={() => setView("rows")}
                >
                  <RowsIcon />
                </button>
              </div>
            </div>
          )}
          {itemsStatus === "loading" && <p className={styles.status}>Wczytywanie produktów…</p>}
          {itemsStatus === "error" && <p className={styles.status}>Nie udało się wczytać produktów.</p>}
          {itemsStatus === "ready" && visible.length === 0 && (
            <p className={styles.status}>
              {query ? `Brak produktów dla „${query}”.` : "Brak produktów dla wybranych filtrów."}
            </p>
          )}
          {itemsStatus === "ready" && visible.length > 0 && (
            <div className={view === "rows" ? styles.rows : styles.grid}>
              {visible.map((item) => (
                <ProductTile
                  key={item.id}
                  item={item}
                  categoryName={category?.name ?? ""}
                  layout={view}
                />
              ))}
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

function sortItems(items: CatalogItem[], sort: SortKey) {
  if (sort === "default") return items;
  return [...items].sort((a, b) => {
    if (sort === "name-asc" || sort === "name-desc") {
      const result = displayName(a.name).localeCompare(displayName(b.name), "pl");
      return sort === "name-asc" ? result : -result;
    }
    const priceA = priceValue(a.price);
    const priceB = priceValue(b.price);
    if (priceA == null && priceB == null) return 0;
    if (priceA == null) return 1;
    if (priceB == null) return -1;
    return sort === "price-asc" ? priceA - priceB : priceB - priceA;
  });
}

function priceValue(value: string | number | null) {
  if (value == null || value === "") return null;
  const amount = Number(value);
  return Number.isNaN(amount) ? null : amount;
}

function matches(item: CatalogItem, selected: SelectedFilters, priceMin: string, priceMax: string) {
  const groups = Object.values(selected).filter((ids) => ids.length > 0);
  const badgeIds = new Set(item.badges.map((badge) => badge.id));
  if (!groups.every((ids) => ids.some((id) => badgeIds.has(id)))) return false;

  const min = priceMin === "" ? null : Number(priceMin);
  const max = priceMax === "" ? null : Number(priceMax);
  if (min == null && max == null) return true;

  const price = item.price == null || item.price === "" ? null : Number(item.price);
  if (price == null || Number.isNaN(price)) return false;
  if (min != null && !Number.isNaN(min) && price < min) return false;
  if (max != null && !Number.isNaN(max) && price > max) return false;
  return true;
}

const GridIcon: React.FC = () => (
  <svg viewBox="0 0 18 18" aria-hidden="true">
    <rect x="1.5" y="1.5" width="6" height="6" rx="1.2" fill="currentColor" />
    <rect x="10.5" y="1.5" width="6" height="6" rx="1.2" fill="currentColor" />
    <rect x="1.5" y="10.5" width="6" height="6" rx="1.2" fill="currentColor" />
    <rect x="10.5" y="10.5" width="6" height="6" rx="1.2" fill="currentColor" />
  </svg>
);

const RowsIcon: React.FC = () => (
  <svg viewBox="0 0 18 18" aria-hidden="true">
    <rect x="1.5" y="2.2" width="15" height="2.6" rx="1" fill="currentColor" />
    <rect x="1.5" y="7.7" width="15" height="2.6" rx="1" fill="currentColor" />
    <rect x="1.5" y="13.2" width="15" height="2.6" rx="1" fill="currentColor" />
  </svg>
);
