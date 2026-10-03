import { useNavigate } from "react-router-dom";

interface SidebarProps {
  canAccessUserPages: boolean;
  onClose: () => void;
}

export default function Sidebar({
  canAccessUserPages,
  onClose,
}: SidebarProps) {
  const navigate = useNavigate();

  const handleProfile = () => {
    onClose();

    if (canAccessUserPages) {
      navigate("/profile");
    } else {
      navigate("/oauth", {
        state: {
          redirectTo: "/profile",
        },
      });
    }
  };

  const handleQR = () => {
    onClose();

    if (canAccessUserPages) {
      navigate("/my-qr");
    } else {
      navigate("/oauth", {
        state: {
          redirectTo: "/my-qr",
        },
      });
    }
  };

  const handleLogout = () => {
    onClose();

    localStorage.removeItem("isLoggedIn");
    localStorage.removeItem("devs_access_token");

    navigate("/");
  };

  return (
    <>
      {/* Dark overlay */}
      <div
        className="sidebar-overlay"
        onClick={onClose}
      />

      {/* Sidebar */}
      <aside className="sidebar">

        {/* Profile */}
        <button
          type="button"
          className="sidebar-button"
          onClick={handleProfile}
        >
          My Profile
        </button>

        {/* QR */}
        <button
          type="button"
          className="sidebar-button"
          onClick={handleQR}
        >
          My QR
        </button>

        {/* Logout */}
        <button
          type="button"
          className="sidebar-button sidebar-logout"
          onClick={handleLogout}
        >
          Log Out
        </button>

      </aside>
    </>
  );
}