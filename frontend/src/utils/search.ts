const FOLDED = "acelnoszz";
const ACCENTED = "ąćęłńóśźż";

export function foldSearch(value: string) {
  return value
    .toLocaleLowerCase("pl-PL")
    .replace(/[ąćęłńóśźż]/g, (letter) => FOLDED[ACCENTED.indexOf(letter)] ?? letter);
}

export function textMatchesQuery(value: string | null | undefined, query: string) {
  const needle = foldSearch(query.trim());
  if (!needle) return true;
  return foldSearch(value ?? "").includes(needle);
}

export const categoryPaths: Record<string, string> = {
  herbata: "/tea",
  ziola: "/herbs",
  kawa: "/coffee",
  dodatki: "/additives",
  porcelana: "/porcelain",
  akcesoria: "/accessories",
  "zestawy-prezentowe": "/gift-sets",
};
