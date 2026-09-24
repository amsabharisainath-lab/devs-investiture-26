import { useState } from "react";
import { BrowserRouter, Routes, Route } from "react-router-dom";

import LoadingState from "./components/shared/LoadingState";
import Home from "./pages/Home";
import Register from "./pages/Register";
import Event from "./pages/Event";
import Profile from "./pages/Profile";
import MyQR from "./pages/MyQR";
import "./App.css";

// Admin / Operator interface routes
import AdminLayout from "./features/admin/components/AdminLayout";
import ScannerPage from "./pages/admin/ScannerPage";
import DatabasePage from "./pages/admin/DatabasePage";
import AdminsPage from "./pages/admin/AdminsPage";
import AdminProfilePage from "./pages/admin/AdminProfilePage";

export default function App() {
  const [isLoading, setIsLoading] = useState(true);

  return (
    <BrowserRouter>
      {isLoading && <LoadingState onComplete={() => setIsLoading(false)} />}

      <Routes>
        {/* Student Attendee Flow */}
        <Route path="/" element={<Home />} />
        <Route path="/register" element={<Register />} />
        <Route path="/event" element={<Event />} />
        <Route path="/profile" element={<Profile />} />
        <Route path="/my-qr" element={<MyQR />} />

        {/* Admin Operator Flow */}
        <Route path="/admin" element={<AdminLayout />}>
          <Route index element={<ScannerPage />} />
          <Route path="database" element={<DatabasePage />} />
          <Route path="admins" element={<AdminsPage />} />
          <Route path="profile" element={<AdminProfilePage />} />
        </Route>
      </Routes>
    </BrowserRouter>
  );
}
