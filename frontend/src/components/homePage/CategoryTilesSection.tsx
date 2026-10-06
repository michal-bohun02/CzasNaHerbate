import React from "react";
import styles from "@/components/css/CategoryTilesSection.module.css";
import {
  CategoryTile,
  type CategoryVariant,
} from "@/components/homePage/CategoryTile";
import teaImage from "@/assets/pics/teaBG.jpg";
import herbsImage from "@/assets/pics/herbsBG.jpg";
import additivesImage from "@/assets/pics/additivesBG.jpg";
import coffeeImage from "@/assets/pics/coffeeBG.jpg";
import porcelainImage from "@/assets/pics/porcelainBG.jpg";
import accessoriesImage from "@/assets/pics/accessoriesBG.jpg";
import giftSetsImage from "@/assets/pics/setsBG.jpg";

const categories: {
  title: string;
  subtitle: string;
  to: string;
  variant: CategoryVariant;
  image?: string;
}[] = [
  {
    title: "Herbata",
    subtitle: "Liście z jednego źródła",
    to: "/tea",
    variant: "tea",
    image: teaImage,
  },
  {
    title: "Zioła",
    subtitle: "Zioła, zioła korzenne i yerba",
    to: "/herbs",
    variant: "herbs",
    image: herbsImage,
  },
  {
    title: "Kawa",
    subtitle: "Kawa speciality z jednego źródła",
    to: "/coffee",
    variant: "coffee",
    image: coffeeImage,
  },
  {
    title: "Dodatki",
    subtitle: "Syropy, miody, czekolady i słodycze",
    to: "/additives",
    variant: "extras",
    image: additivesImage,
  },
  {
    title: "Porcelana",
    subtitle: "Ręcznie wytwarzana ceramika",
    to: "/porcelain",
    variant: "porcelain",
    image: porcelainImage,
  },
  {
    title: "Akcesoria",
    subtitle: "Narzędzia i akcesoria do parzenia",
    to: "/accessories",
    variant: "accessories",
    image: accessoriesImage,
  },
  {
    title: "Zestawy Prezentowe",
    subtitle: "Starannie dobrane kolekcje",
    to: "/gift-sets",
    variant: "giftSets",
    image: giftSetsImage,
  },
];

export const CategoryTilesSection: React.FC = () => {
  return (
    <section id="shop" className={styles.section}>
      <div className={styles.header}>
        <span className={styles.eyebrow}>Przeglądaj według kolekcji</span>
        <h2 className={styles.heading}>Nasz Świat</h2>
      </div>
      <div className={styles.grid}>
        {categories.map((category) => (
          <CategoryTile key={category.to} {...category} />
        ))}
      </div>
    </section>
  );
};
