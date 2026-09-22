import { useState } from "react";
import { useAdminAuth } from "../../features/admin/hooks/useAdminAuth";

export default function AdminProfilePage() {
  const { user } = useAdminAuth();
  const [isSignedOut, setIsSignedOut] = useState(false);
  const [isConfirmingSignOut, setIsConfirmingSignOut] = useState(false);

  if (isSignedOut) {
    return (
      <div className="page-container" style={{ textAlign: "center", paddingTop: "56px" }}>
        <h2
          style={{
            fontSize: "18px",
            fontFamily: "var(--font-sans)",
            fontWeight: 700,
            letterSpacing: "0.04em",
            textTransform: "uppercase",
            color: "#ffffff",
            marginBottom: "8px",
          }}
        >
          Signed Out
        </h2>
        <p className="page-description" style={{ margin: "0 auto 24px", maxWidth: "300px", fontSize: "12px" }}>
          You have successfully disconnected from the operator session.
        </p>
        <button
          onClick={() => setIsSignedOut(false)}
          style={{
            background: "#ffffff",
            border: "none",
            color: "#000000",
            fontFamily: "var(--font-mono)",
            fontSize: "10px",
            fontWeight: 700,
            letterSpacing: "0.1em",
            padding: "10px 20px",
            cursor: "pointer",
            textTransform: "uppercase",
          }}
        >
          Sign Back In
        </button>
      </div>
    );
  }

  if (!user) {
    return (
      <div className="page-container" style={{ textAlign: "center", paddingTop: "56px" }}>
        <p className="page-description">No active session found.</p>
      </div>
    );
  }

  const roleDisplay = user.role === "SUPER_ADMIN" ? "SUPER ADMIN" : "ADMIN";
  const statusDisplay = user.is_active ? "ACTIVE" : "INACTIVE";

  return (
    <div className="page-container" style={{ textAlign: "left", alignItems: "stretch", paddingBottom: "48px" }}>
      {/* 1. Typographic Identity Hero */}
      <div
        style={{
          display: "flex",
          flexDirection: "column",
          gap: "8px",
          marginBottom: "32px",
          paddingBottom: "24px",
          borderBottom: "1px solid var(--border-dark)",
        }}
      >
        <div
          style={{
            fontFamily: "var(--font-mono)",
            fontSize: "9px",
            color: "var(--muted-gray)",
            letterSpacing: "0.15em",
            textTransform: "uppercase",
          }}
        >
          OPERATOR PROFILE
        </div>

        <h1
          style={{
            fontFamily: "var(--font-sans)",
            fontSize: "26px",
            fontWeight: 700,
            color: "#ffffff",
            letterSpacing: "0.02em",
            margin: 0,
            lineHeight: "1.15",
          }}
        >
          {user.name}
        </h1>

        <div
          style={{
            fontFamily: "var(--font-mono)",
            fontSize: "12px",
            color: "var(--muted-gray)",
            letterSpacing: "0.02em",
          }}
        >
          {user.email}
        </div>

        {/* Role and Status Badges */}
        <div style={{ display: "flex", alignItems: "center", gap: "8px", marginTop: "6px" }}>
          <span
            style={{
              fontFamily: "var(--font-mono)",
              fontSize: "9px",
              fontWeight: 600,
              color: "#ffffff",
              background: "#18181b",
              border: "1px solid #3f3f46",
              padding: "3px 8px",
              letterSpacing: "0.08em",
            }}
          >
            {roleDisplay}
          </span>

          <span
            style={{
              fontFamily: "var(--font-mono)",
              fontSize: "9px",
              fontWeight: 600,
              color: user.is_active ? "#e4e4e7" : "var(--muted-gray)",
              border: "1px solid var(--border-dark)",
              padding: "3px 8px",
              letterSpacing: "0.08em",
            }}
          >
            {statusDisplay}
          </span>
        </div>
      </div>

      {/* 2. ACCOUNT SPECIFICATIONS */}
      <div style={{ marginBottom: "32px" }}>
        <div
          style={{
            fontFamily: "var(--font-mono)",
            fontSize: "9px",
            color: "var(--muted-gray)",
            letterSpacing: "0.15em",
            textTransform: "uppercase",
            marginBottom: "10px",
          }}
        >
          ACCOUNT DETAILS
        </div>
        <div style={{ width: "100%", height: "1px", backgroundColor: "var(--border-dark)" }} />

        {/* Row: Name */}
        <div
          style={{
            display: "flex",
            justifyContent: "space-between",
            alignItems: "center",
            padding: "14px 0",
            borderBottom: "1px solid var(--border-dark)",
          }}
        >
          <span
            style={{
              fontFamily: "var(--font-mono)",
              fontSize: "10px",
              color: "var(--muted-gray)",
              letterSpacing: "0.06em",
            }}
          >
            Full Name
          </span>
          <span
            style={{
              fontFamily: "var(--font-sans)",
              fontSize: "13px",
              fontWeight: 600,
              color: "#ffffff",
            }}
          >
            {user.name}
          </span>
        </div>

        {/* Row: Email */}
        <div
          style={{
            display: "flex",
            justifyContent: "space-between",
            alignItems: "center",
            padding: "14px 0",
            borderBottom: "1px solid var(--border-dark)",
          }}
        >
          <span
            style={{
              fontFamily: "var(--font-mono)",
              fontSize: "10px",
              color: "var(--muted-gray)",
              letterSpacing: "0.06em",
            }}
          >
            Email Address
          </span>
          <span
            style={{
              fontFamily: "var(--font-mono)",
              fontSize: "12px",
              color: "#ffffff",
            }}
          >
            {user.email}
          </span>
        </div>
      </div>

      {/* 3. ACCESS & AUTHORIZATION */}
      <div style={{ marginBottom: "32px" }}>
        <div
          style={{
            fontFamily: "var(--font-mono)",
            fontSize: "9px",
            color: "var(--muted-gray)",
            letterSpacing: "0.15em",
            textTransform: "uppercase",
            marginBottom: "10px",
          }}
        >
          ACCESS & PERMISSIONS
        </div>
        <div style={{ width: "100%", height: "1px", backgroundColor: "var(--border-dark)" }} />

        {/* Row: Role */}
        <div
          style={{
            display: "flex",
            justifyContent: "space-between",
            alignItems: "center",
            padding: "14px 0",
            borderBottom: "1px solid var(--border-dark)",
          }}
        >
          <span
            style={{
              fontFamily: "var(--font-mono)",
              fontSize: "10px",
              color: "var(--muted-gray)",
              letterSpacing: "0.06em",
            }}
          >
            Role
          </span>
          <span
            style={{
              fontFamily: "var(--font-mono)",
              fontSize: "11px",
              fontWeight: 600,
              color: "#ffffff",
            }}
          >
            {roleDisplay}
          </span>
        </div>

        {/* Row: Scope */}
        <div
          style={{
            display: "flex",
            justifyContent: "space-between",
            alignItems: "center",
            padding: "14px 0",
            borderBottom: "1px solid var(--border-dark)",
          }}
        >
          <span
            style={{
              fontFamily: "var(--font-mono)",
              fontSize: "10px",
              color: "var(--muted-gray)",
              letterSpacing: "0.06em",
            }}
          >
            Access Scope
          </span>
          <span
            style={{
              fontFamily: "var(--font-mono)",
              fontSize: "11px",
              color: "#a1a1aa",
              textAlign: "right",
            }}
          >
            {user.role === "SUPER_ADMIN" ? "Full Database & Scanner" : "Attendance Scanner Only"}
          </span>
        </div>

        {/* Row: Status */}
        <div
          style={{
            display: "flex",
            justifyContent: "space-between",
            alignItems: "center",
            padding: "14px 0",
            borderBottom: "1px solid var(--border-dark)",
          }}
        >
          <span
            style={{
              fontFamily: "var(--font-mono)",
              fontSize: "10px",
              color: "var(--muted-gray)",
              letterSpacing: "0.06em",
            }}
          >
            Status
          </span>
          <span
            style={{
              fontFamily: "var(--font-mono)",
              fontSize: "11px",
              color: "#ffffff",
            }}
          >
            Active
          </span>
        </div>
      </div>

      {/* 4. SESSION & ACTIONS */}
      <div>
        <div
          style={{
            fontFamily: "var(--font-mono)",
            fontSize: "9px",
            color: "var(--muted-gray)",
            letterSpacing: "0.15em",
            textTransform: "uppercase",
            marginBottom: "10px",
          }}
        >
          SESSION
        </div>
        <div style={{ width: "100%", height: "1px", backgroundColor: "var(--border-dark)", marginBottom: "16px" }} />

        {isConfirmingSignOut ? (
          <div style={{ display: "flex", gap: "8px" }}>
            <button
              onClick={() => {
                setIsSignedOut(true);
                setIsConfirmingSignOut(false);
              }}
              style={{
                flex: 1,
                height: "40px",
                background: "none",
                border: "1px solid #ef4444",
                color: "#ef4444",
                fontFamily: "var(--font-mono)",
                fontSize: "10px",
                fontWeight: 600,
                letterSpacing: "0.1em",
                textTransform: "uppercase",
                cursor: "pointer",
              }}
            >
              Confirm Sign Out
            </button>
            <button
              onClick={() => setIsConfirmingSignOut(false)}
              style={{
                height: "40px",
                padding: "0 18px",
                background: "none",
                border: "1px solid var(--border-dark)",
                color: "var(--muted-gray)",
                fontFamily: "var(--font-mono)",
                fontSize: "10px",
                letterSpacing: "0.08em",
                cursor: "pointer",
              }}
            >
              Cancel
            </button>
          </div>
        ) : (
          <button
            onClick={() => setIsConfirmingSignOut(true)}
            style={{
              width: "100%",
              height: "40px",
              background: "transparent",
              border: "1px solid var(--border-dark)",
              color: "var(--muted-gray)",
              fontFamily: "var(--font-mono)",
              fontSize: "10px",
              letterSpacing: "0.08em",
              cursor: "pointer",
              transition: "color 150ms ease, border-color 150ms ease",
            }}
            onMouseEnter={(e) => {
              e.currentTarget.style.borderColor = "#3f3f46";
              e.currentTarget.style.color = "#ffffff";
            }}
            onMouseLeave={(e) => {
              e.currentTarget.style.borderColor = "var(--border-dark)";
              e.currentTarget.style.color = "var(--muted-gray)";
            }}
          >
            Sign Out
          </button>
        )}
      </div>
    </div>
  );
}

