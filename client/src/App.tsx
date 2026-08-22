import { BrowserRouter, Routes, Route } from "react-router-dom";

import Preloader from "./components/Preloader";
import Home from "./pages/Home";
import Register from "./pages/Register";
import Event from "./pages/Event";
import Profile from "./pages/profile";
import MyQR from "./pages/MyQR";

import "./App.css";

export default function App() {
  return (
    <BrowserRouter>
      <Preloader />

      <Routes>
        <Route path="/" element={<Home />} />
        <Route path="/register" element={<Register />} />
        <Route path="/event" element={<Event />} />
        <Route path="/profile" element={<Profile />} />
        <Route path="/my-qr" element={<MyQR />} />
      </Routes>
    </BrowserRouter>
  );
}