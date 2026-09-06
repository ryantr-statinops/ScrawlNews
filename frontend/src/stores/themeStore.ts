import { create } from "zustand";
import { persist } from "zustand/middleware";

type ColorScheme = "light" | "dark";

interface ThemeState {
  colorScheme: ColorScheme;
  toggle: () => void;
  set: (scheme: ColorScheme) => void;
}

export const useThemeStore = create<ThemeState>()(
  persist(
    (set) => ({
      colorScheme: "dark",
      toggle: () =>
        set((s) => ({
          colorScheme: s.colorScheme === "dark" ? "light" : "dark",
        })),
      set: (colorScheme) => set({ colorScheme }),
    }),
    { name: "scrawlnews-theme" },
  ),
);
