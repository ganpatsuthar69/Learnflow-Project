import React, { createContext, useContext, useEffect, useState } from "react";

type Theme = "light";

interface ThemeProviderProps {
    children: React.ReactNode;
    defaultTheme?: Theme;
    storageKey?: string;
}

interface ThemeProviderState {
    theme: Theme;
    setTheme: (theme: Theme) => void;
}

const initialState: ThemeProviderState = {
    theme: "light",
    setTheme: () => null,
};

const ThemeProviderContext = createContext<ThemeProviderState>(initialState);

export function ThemeProvider({
    children,
}: ThemeProviderProps) {
    // Always force light theme, ignore storage and props
    const [theme] = useState<Theme>("light");

    useEffect(() => {
        const root = window.document.documentElement;
        root.classList.remove("dark");
        root.classList.add("light");
    }, []);

    const value = {
        theme,
        setTheme: () => null, // Disable changing theme
    };

    return (
        <ThemeProviderContext.Provider value={value}>
            {children}
        </ThemeProviderContext.Provider>
    );
}

// eslint-disable-next-line react-refresh/only-export-components
export const useTheme = () => {
    const context = useContext(ThemeProviderContext);

    if (context === undefined)
        throw new Error("useTheme must be used within a ThemeProvider");

    return context;
};
