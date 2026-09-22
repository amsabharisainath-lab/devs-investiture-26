import { Link, Outlet, useLocation } from "react-router-dom";
import BrandLogo from "../../../components/shared/BrandLogo";
import { useAdminAuth } from "../hooks/useAdminAuth";

export default function AdminLayout() {
  const location = useLocation();
  const { role } = useAdminAuth();

  const isSuperAdmin = role === "SUPER_ADMIN";

  // Base navigation links accessible by all admin operators
  const navItems = [
    {
      label: "SCANNER",
      path: "/admin",
      icon: (
        <svg
          viewBox="0 0 24 24"
          width="18"
          height="18"
          fill="none"
          stroke="currentColor"
          strokeWidth="1.5"
          strokeLinecap="round"
          strokeLinejoin="round"
        >
          <path d="M4 8V4h4M16 4h4v4M4 16v4h4M16 20h4v-4M8 12h8M12 8v8" />
        </svg>
      ),
    },
    {
      label: "DATABASE",
      path: "/admin/database",
      icon: (
        <svg
          viewBox="0 0 24 24"
          width="18"
          height="18"
          fill="none"
          stroke="currentColor"
          strokeWidth="1.5"
          strokeLinecap="round"
          strokeLinejoin="round"
        >
          <ellipse cx="12" cy="5" rx="9" ry="3" />
          <path d="M3 5v14c0 1.66 4 3 9 3s9-1.34 9-3V5" />
          <path d="M3 12c0 1.66 4 3 9 3s9-1.34 9-3" />
        </svg>
      ),
    },
  ];

  // Dynamically append the Admin Access Management tab only for Super Admins
  if (isSuperAdmin) {
    navItems.push({
      label: "ADMINS",
      path: "/admin/admins",
      icon: (
        <svg
          viewBox="0 0 24 24"
          width="18"
          height="18"
          fill="none"
          stroke="currentColor"
          strokeWidth="1.5"
          strokeLinecap="round"
          strokeLinejoin="round"
        >
          <path d="M16 21v-2a4 4 0 0 0-4-4H6a4 4 0 0 0-4 4v2" />
          <circle cx="9" cy="7" r="4" />
          <path d="M22 21v-2a4 4 0 0 0-3-3.87" />
          <path d="M16 3.13a4 4 0 0 1 0 7.75" />
        </svg>
      ),
    });
  }

  // Profile is always the rightmost navigation tab
  navItems.push({
    label: "PROFILE",
    path: "/admin/profile",
    icon: (
      <svg
        viewBox="0 0 24 24"
        width="18"
        height="18"
        fill="none"
        stroke="currentColor"
        strokeWidth="1.5"
        strokeLinecap="round"
        strokeLinejoin="round"
      >
        <path d="M19 21v-2a4 4 0 0 0-4-4H9a4 4 0 0 0-4 4v2" />
        <circle cx="12" cy="7" r="4" />
      </svg>
    ),
  });

  return (
    <div className="app-shell">
      {/* Asymmetric Header: Brand Logo on Left, System Role Metadata on Right */}
      <header className="page-header">
        <BrandLogo size="sm" />
        <div className="header-subtext">
          {role === "SUPER_ADMIN" ? "SUPER ADMIN" : "ADMIN"}
        </div>
      </header>

      {/* Child Route Content View */}
      <main className="main-content">
        <Outlet />
      </main>

      {/* Dynamic columns grid based on tab count */}
      <nav className="bottom-nav" style={{ gridTemplateColumns: `repeat(${navItems.length}, 1fr)` }}>
        {navItems.map((item) => {
          const active = location.pathname === item.path;
          return (
            <Link
              key={item.path}
              to={item.path}
              className={`nav-item ${active ? "active" : ""}`}
            >
              {active && <span className="active-indicator" />}
              <span className="nav-icon">{item.icon}</span>
              <span className="nav-label">{item.label}</span>
            </Link>
          );
        })}
      </nav>
    </div>
  );
}
