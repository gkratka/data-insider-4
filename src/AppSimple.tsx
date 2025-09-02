import React from "react";
import { BrowserRouter, Routes, Route } from "react-router-dom";
import IndexFixed from "./pages/IndexFixed";

const App = () => (
  <BrowserRouter>
    <Routes>
      <Route path="/" element={<IndexFixed />} />
      <Route path="*" element={<div className="p-8 text-center">404 - Page not found</div>} />
    </Routes>
  </BrowserRouter>
);

export default App;