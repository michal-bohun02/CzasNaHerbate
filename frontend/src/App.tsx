// App.tsx
import { BrowserRouter, Routes, Route } from "react-router-dom";
import { HomePage } from "./pages/HomePage";
import { ItemsPage } from "./pages/ItemsPage";
import { TeaPage } from "./pages/TeaPage";
import { CoffeePage } from "./pages/CoffeePage";
import { PorcelainPage } from "./pages/PorcelainPage";
import { AccessoriesPage } from "./pages/AccessoriesPage";
import { GiftSetsPage } from "./pages/GiftSetsPage";
import { NavBar } from "@/components/homePage/NavBar.tsx";
import { Footer } from "@/components/homePage/Footer";
import styles from "./App.module.css";

function App() {
  return (
    <BrowserRouter>
      <div className={styles.app}>
        <NavBar />
        <main className={styles.main}>
          <Routes>
            <Route path="/" element={<HomePage />} />
            <Route path="/items" element={<ItemsPage />} />
            <Route path="/tea" element={<TeaPage />} />
            <Route path="/coffee" element={<CoffeePage />} />
            <Route path="/porcelain" element={<PorcelainPage />} />
            <Route path="/accessories" element={<AccessoriesPage />} />
            <Route path="/gift-sets" element={<GiftSetsPage />} />
          </Routes>
        </main>
        <Footer />
      </div>
    </BrowserRouter>
  );
}

export default App;
