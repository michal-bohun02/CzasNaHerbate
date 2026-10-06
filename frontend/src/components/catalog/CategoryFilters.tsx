import React, { useEffect, useRef, useState } from "react";
import styles from "@/components/css/CategoryFilters.module.css";
import type { FilterGroup } from "@/components/catalog/filterConfig";

export type SelectedFilters = Record<string, string[]>;

interface Props {
  groups: FilterGroup[];
  priceMinHint: string | number | null;
  priceMaxHint: string | number | null;
  status: "loading" | "ready" | "error";
  onChange?: (selected: SelectedFilters, priceMin: string, priceMax: string) => void;
}

export const CategoryFilters: React.FC<Props> = ({
  groups,
  priceMinHint,
  priceMaxHint,
  status,
  onChange,
}) => {
  const [openGroups, setOpenGroups] = useState<Record<string, boolean>>({});
  const [selected, setSelected] = useState<Record<string, string[]>>({});
  const [priceMin, setPriceMin] = useState("");
  const [priceMax, setPriceMax] = useState("");
  const filtersRef = useRef<HTMLElement>(null);

  useEffect(() => {
    const el = filtersRef.current;
    if (!el) return;

    const topGap = 24;
    const bottomGap = 24;
    const desktop = window.matchMedia("(min-width: 861px)");
    let lastY = window.scrollY;
    let currentTop = topGap;

    const place = (fromScroll: boolean) => {
      if (!desktop.matches) {
        el.style.top = "";
        lastY = window.scrollY;
        return;
      }
      const height = el.offsetHeight;
      const minTop = window.innerHeight - bottomGap - height;
      if (height <= window.innerHeight - topGap - bottomGap) {
        currentTop = topGap;
      } else if (fromScroll) {
        const delta = window.scrollY - lastY;
        currentTop = Math.min(topGap, Math.max(minTop, currentTop - delta));
      } else {
        currentTop = Math.min(topGap, Math.max(minTop, currentTop));
      }
      lastY = window.scrollY;
      el.style.top = `${currentTop}px`;
    };

    const onScroll = () => place(true);
    const onResize = () => place(false);
    place(false);
    const observer = new ResizeObserver(() => place(false));
    observer.observe(el);
    desktop.addEventListener("change", onResize);
    window.addEventListener("scroll", onScroll, { passive: true });
    window.addEventListener("resize", onResize);
    return () => {
      observer.disconnect();
      desktop.removeEventListener("change", onResize);
      window.removeEventListener("scroll", onScroll);
      window.removeEventListener("resize", onResize);
      el.style.top = "";
    };
  }, []);

  useEffect(() => {
    setOpenGroups(Object.fromEntries(groups.map((group, index) => [group.id, index === 0])));
    setSelected({});
    setPriceMin("");
    setPriceMax("");
  }, [groups]);

  const toggleGroup = (groupId: string) => {
    setOpenGroups((current) => ({ ...current, [groupId]: !current[groupId] }));
  };

  const emit = (nextSelected: SelectedFilters, nextMin: string, nextMax: string) => {
    onChange?.(nextSelected, nextMin, nextMax);
  };

  const toggleOption = (groupId: string, optionId: string) => {
    setSelected((current) => {
      const currentIds = current[groupId] ?? [];
      const nextIds = currentIds.includes(optionId)
        ? currentIds.filter((id) => id !== optionId)
        : [...currentIds, optionId];
      const next = { ...current, [groupId]: nextIds };
      emit(next, priceMin, priceMax);
      return next;
    });
  };

  return (
    <aside ref={filtersRef} className={styles.filters} aria-label="Filtry">
      <div className={styles.header}>
        <FilterIcon />
        <h2 className={styles.title}>Filtry</h2>
      </div>

      {status === "loading" && <p className={styles.status}>Wczytywanie filtrów…</p>}
      {status === "error" && <p className={styles.status}>Nie udało się wczytać filtrów.</p>}

      {status === "ready" && (
        <>
          <div className={styles.price}>
            <span className={styles.sectionLabel}>Przedział cenowy</span>
            <div className={styles.priceRow}>
              <input
                className={styles.priceInput}
                type="number"
                min={0}
                inputMode="numeric"
                placeholder={pricePlaceholder(priceMinHint, "od")}
                aria-label="Cena od"
            value={priceMin}
            onChange={(event) => {
              const next = event.target.value;
              setPriceMin(next);
              emit(selected, next, priceMax);
            }}
              />
              <span className={styles.priceDash} aria-hidden="true">
                –
              </span>
              <input
                className={styles.priceInput}
                type="number"
                min={0}
                inputMode="numeric"
                placeholder={pricePlaceholder(priceMaxHint, "do")}
                aria-label="Cena do"
            value={priceMax}
            onChange={(event) => {
              const next = event.target.value;
              setPriceMax(next);
              emit(selected, priceMin, next);
            }}
              />
            </div>
          </div>

          {groups.map((group) => (
            <FilterSection
              key={group.id}
              group={group}
              open={Boolean(openGroups[group.id])}
              selected={selected[group.id] ?? []}
              onToggleGroup={() => toggleGroup(group.id)}
              onToggleOption={(optionId) => toggleOption(group.id, optionId)}
            />
          ))}
        </>
      )}
    </aside>
  );
};

const FilterSection: React.FC<{
  group: FilterGroup;
  open: boolean;
  selected: string[];
  onToggleGroup: () => void;
  onToggleOption: (optionId: string) => void;
}> = ({ group, open, selected, onToggleGroup, onToggleOption }) => {
  const panelId = `filter-${group.id}`;

  return (
    <section className={styles.group}>
      <button
        type="button"
        className={styles.groupToggle}
        aria-expanded={open}
        aria-controls={panelId}
        onClick={onToggleGroup}
      >
        <span>{group.name}</span>
        <ChevronIcon open={open} />
      </button>
      {open && (
        <ul className={styles.options} id={panelId}>
          {group.options.map((option) => {
            const checked = selected.includes(option.id);
            return (
              <li key={option.id}>
                <label className={styles.option}>
                  <input
                    type="checkbox"
                    checked={checked}
                    onChange={() => onToggleOption(option.id)}
                  />
                  <span className={styles.box} aria-hidden="true" />
                  <span className={styles.optionLabel}>{option.name}</span>
                </label>
              </li>
            );
          })}
        </ul>
      )}
    </section>
  );
};

function pricePlaceholder(value: string | number | null, fallback: string) {
  if (value == null || value === "") return fallback;
  const amount = Number(value);
  if (Number.isNaN(amount)) return fallback;
  const rounded = Number.isInteger(amount) ? String(amount) : amount.toLocaleString("pl-PL");
  return `${rounded} zł`;
}

const FilterIcon: React.FC = () => (
  <svg className={styles.icon} viewBox="0 0 20 20" aria-hidden="true">
    <path
      d="M3 4.5h14M6 10h8M8.5 15.5h3"
      fill="none"
      stroke="currentColor"
      strokeWidth="1.6"
      strokeLinecap="round"
    />
  </svg>
);

const ChevronIcon: React.FC<{ open: boolean }> = ({ open }) => (
  <svg
    className={`${styles.chevron} ${open ? styles.chevronOpen : ""}`}
    viewBox="0 0 16 16"
    aria-hidden="true"
  >
    <path
      d="M4 6.5 8 10.5 12 6.5"
      fill="none"
      stroke="currentColor"
      strokeWidth="1.6"
      strokeLinecap="round"
      strokeLinejoin="round"
    />
  </svg>
);
