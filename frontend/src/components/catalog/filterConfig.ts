export type FilterOption = {
  id: string;
  name: string;
  slug: string;
  position: number;
  source: "category" | "attribute";
};

export type FilterGroup = {
  id: string;
  name: string;
  slug: string;
  position: number;
  options: FilterOption[];
};

export type CatalogBadge = {
  id: string;
  name: string;
  slug: string;
  position: number;
  source: "category" | "attribute";
};

export type CatalogItem = {
  id: number;
  name: string;
  slug: string;
  description: string | null;
  photo_url: string | null;
  price: string | number | null;
  badges: CatalogBadge[];
};

export type CategoryFiltersResponse = {
  id: number;
  name: string;
  slug: string;
  price_min: string | number | null;
  price_max: string | number | null;
  groups: FilterGroup[];
};
