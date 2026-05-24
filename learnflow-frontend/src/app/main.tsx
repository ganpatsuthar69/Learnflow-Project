import React from "react";
import { createRoot } from "react-dom/client";
import "../styles/index.css";
import App from "./App";

import { ThemeProvider } from "../components/ThemeProvider";

createRoot(document.getElementById("root")!).render(
  <React.StrictMode>
    <ThemeProvider defaultTheme="dark" storageKey="learnflow-theme">
      <App />
    </ThemeProvider>
  </React.StrictMode>
);
