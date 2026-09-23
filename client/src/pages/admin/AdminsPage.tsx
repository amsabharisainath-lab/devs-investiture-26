import { useState } from "react";
import { useAdminAuth } from "../../features/admin/hooks/useAdminAuth";

export default function AdminsPage() {
  const { role } = useAdminAuth();
  const isSuperAdmin = role === "SUPER_ADMIN";

  const [admins, setAdmins] = useState<string[]>([
    "admin@example.com",
    "operator-one@example.com",
    "operator-two@example.com",
  ]);
  const [emailInput, setEmailInput] = useState("");
  const [formError, setFormError] = useState<string | null>(null);
  const [revokingEmail, setRevokingEmail] = useState<string | null>(null);

  const handleAddAdmin = (e: React.FormEvent) => {
    e.preventDefault();
    const cleanEmail = emailInput.trim().toLowerCase();
    if (!cleanEmail) return;

    if (admins.includes(cleanEmail)) {
      setFormError("EMAIL IS ALREADY AUTHORIZED");
      return;
    }

    setAdmins((prev) => [...prev, cleanEmail]);
    setEmailInput("");
    setFormError(null);
  };

  const handleConfirmRevoke = (email: string) => {
    setAdmins((prev) => prev.filter((a) => a !== email));
    setRevokingEmail(null);
  };

  // 1. Render Unauthorized Error View (ADMIN role attempts to access /admin/admins)
  if (!isSuperAdmin) {
    return (
      <div className="page-container" style={{ textAlign: "center", paddingTop: "48px" }}>
        <span
          className="outcome-badge error-scan"
          style={{ marginBottom: "16px", borderColor: "var(--border-dark)", color: "var(--muted-gray)" }}
        >
          PRIVILEGES REQUIRED
        </span>
        <h3
          style={{
            margin: "12px 0 6px",
            fontSize: "14px",
            fontFamily: "var(--font-mono)",
            letterSpacing: "0.1em",
            textTransform: "uppercase",
            color: "#ffffff",
          }}
        >
          ACCESS RESTRICTED
        </h3>
        <p className="page-description" style={{ margin: "0 auto", maxWidth: "300px" }}>
          Database access is read-only. Managing admin access credentials requires SUPER_ADMIN role authentication.
        </p>
      </div>
    );
  }

  // 2. Render Super Admin UI View (SUPER_ADMIN role accesses /admin/admins)
  return (
    <div className="page-container" style={{ textAlign: "left", alignItems: "stretch" }}>
      {/* Editorial Header */}
      <div style={{ display: "flex", justifyContent: "space-between", alignItems: "flex-end", marginBottom: "24px" }}>
        <div>
          <h1
            style={{
              fontFamily: "var(--font-sans)",
              fontSize: "22px",
              fontWeight: 700,
              color: "#ffffff",
              letterSpacing: "0.08em",
              textTransform: "uppercase",
              margin: "0 0 4px 0",
            }}
          >
            ADMINS
          </h1>
          <div
            style={{
              fontFamily: "var(--font-mono)",
              fontSize: "9px",
              color: "var(--muted-gray)",
              letterSpacing: "0.15em",
              textTransform: "uppercase",
            }}
          >
            AUTHORIZED ADMINISTRATORS
          </div>
        </div>

        <div style={{ textAlign: "right" }}>
          <div
            style={{
              fontFamily: "var(--font-sans)",
              fontSize: "18px",
              fontWeight: 700,
              color: "#ffffff",
              letterSpacing: "0.04em",
              lineHeight: "1",
            }}
          >
            {admins.length.toString().padStart(2, "0")}
          </div>
          <div
            style={{
              fontFamily: "var(--font-mono)",
              fontSize: "8px",
              color: "var(--muted-gray)",
              letterSpacing: "0.15em",
              textTransform: "uppercase",
              marginTop: "2px",
            }}
          >
            AUTHORIZED
          </div>
        </div>
      </div>

      {/* Add Administrator Operation Form */}
      <div style={{ marginBottom: "28px" }}>
        <div
          style={{
            fontFamily: "var(--font-mono)",
            fontSize: "9px",
            color: "var(--muted-gray)",
            letterSpacing: "0.15em",
            textTransform: "uppercase",
            marginBottom: "8px",
          }}
        >
          ADD ADMINISTRATOR
        </div>
        <div style={{ width: "100%", height: "1px", backgroundColor: "var(--border-dark)", marginBottom: "12px" }} />

        <form onSubmit={handleAddAdmin} style={{ display: "flex", flexDirection: "column", gap: "8px", width: "100%", boxSizing: "border-box" }}>
          <div style={{ display: "flex", flexDirection: "column", gap: "4px" }}>
            <label
              htmlFor="admin-email-input"
              style={{
                fontFamily: "var(--font-mono)",
                fontSize: "8px",
                color: "var(--muted-gray)",
                letterSpacing: "0.12em",
                textTransform: "uppercase",
              }}
            >
              EMAIL ADDRESS
            </label>
            <div style={{ display: "flex", gap: "8px" }}>
              <input
                id="admin-email-input"
                type="email"
                placeholder="OPERATOR@EXAMPLE.COM"
                value={emailInput}
                onChange={(e) => {
                  setEmailInput(e.target.value);
                  if (formError) setFormError(null);
                }}
                required
                style={{
                  flexGrow: 1,
                  height: "38px",
                  background: "#09090b",
                  border: formError ? "1px solid #ef4444" : "1px solid var(--border-dark)",
                  color: "var(--fg-white)",
                  padding: "0 12px",
                  fontSize: "11px",
                  fontFamily: "var(--font-mono)",
                  letterSpacing: "0.05em",
                  outline: "none",
                  boxSizing: "border-box",
                }}
              />
              <button
                type="submit"
                style={{
                  height: "38px",
                  padding: "0 16px",
                  backgroundColor: "#fafafa",
                  color: "#000000",
                  border: "none",
                  fontFamily: "var(--font-mono)",
                  fontSize: "9px",
                  fontWeight: 700,
                  letterSpacing: "0.15em",
                  textTransform: "uppercase",
                  cursor: "pointer",
                  whiteSpace: "nowrap",
                }}
              >
                AUTHORIZE ADMIN
              </button>
            </div>
            {formError && (
              <span
                style={{
                  fontFamily: "var(--font-mono)",
                  fontSize: "9px",
                  color: "#ef4444",
                  letterSpacing: "0.05em",
                  marginTop: "4px",
                }}
              >
                {formError}
              </span>
            )}
          </div>
        </form>
      </div>

      {/* Authorized Administrator Registry */}
      <div>
        <div
          style={{
            fontFamily: "var(--font-mono)",
            fontSize: "9px",
            color: "var(--muted-gray)",
            letterSpacing: "0.15em",
            textTransform: "uppercase",
            marginBottom: "8px",
          }}
        >
          REGISTRY
        </div>
        <div style={{ width: "100%", height: "1px", backgroundColor: "var(--border-dark)" }} />

        {admins.map((email) => (
          <div
            key={email}
            style={{
              display: "flex",
              justifyContent: "space-between",
              alignItems: "center",
              padding: "14px 0",
              borderBottom: "1px solid var(--border-dark)",
            }}
          >
            <div style={{ display: "flex", flexDirection: "column", gap: "3px" }}>
              <span
                style={{
                  fontSize: "13px",
                  fontFamily: "var(--font-mono)",
                  color: "#ffffff",
                  letterSpacing: "0.02em",
                }}
              >
                {email}
              </span>
              <div style={{ display: "flex", alignItems: "center", gap: "8px" }}>
                <span
                  style={{
                    fontFamily: "var(--font-mono)",
                    fontSize: "9px",
                    color: "var(--muted-gray)",
                    letterSpacing: "0.1em",
                    textTransform: "uppercase",
                  }}
                >
                  ADMIN
                </span>
                <span style={{ color: "#3f3f46", fontSize: "9px" }}>·</span>
                <span
                  style={{
                    fontFamily: "var(--font-mono)",
                    fontSize: "9px",
                    color: "var(--muted-gray)",
                    letterSpacing: "0.1em",
                    textTransform: "uppercase",
                  }}
                >
                  ACTIVE
                </span>
              </div>
            </div>

            {revokingEmail === email ? (
              <div style={{ display: "flex", gap: "8px", alignItems: "center" }}>
                <button
                  onClick={() => handleConfirmRevoke(email)}
                  style={{
                    background: "none",
                    border: "1px solid #ef4444",
                    color: "#ef4444",
                    cursor: "pointer",
                    fontSize: "9px",
                    fontFamily: "var(--font-mono)",
                    letterSpacing: "0.12em",
                    textTransform: "uppercase",
                    padding: "4px 8px",
                  }}
                >
                  CONFIRM REVOKE
                </button>
                <button
                  onClick={() => setRevokingEmail(null)}
                  style={{
                    background: "none",
                    border: "1px solid var(--border-dark)",
                    color: "var(--muted-gray)",
                    cursor: "pointer",
                    fontSize: "9px",
                    fontFamily: "var(--font-mono)",
                    letterSpacing: "0.12em",
                    textTransform: "uppercase",
                    padding: "4px 8px",
                  }}
                >
                  CANCEL
                </button>
              </div>
            ) : (
              <button
                onClick={() => setRevokingEmail(email)}
                style={{
                  background: "none",
                  border: "none",
                  color: "var(--muted-gray)",
                  cursor: "pointer",
                  fontSize: "9px",
                  fontFamily: "var(--font-mono)",
                  letterSpacing: "0.15em",
                  textTransform: "uppercase",
                  padding: "6px 8px",
                  transition: "color 150ms ease",
                }}
                onMouseEnter={(e) => (e.currentTarget.style.color = "#ef4444")}
                onMouseLeave={(e) => (e.currentTarget.style.color = "var(--muted-gray)")}
              >
                REVOKE
              </button>
            )}
          </div>
        ))}
      </div>
    </div>
  );
}
