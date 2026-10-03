import { useState } from "react";
import { useLocation } from "react-router-dom";
import { getGoogleOAuthURL } from "../api/api";

interface OAuthLocationState {
  redirectTo?: string;
}

export default function OAuth() {
  const [loading, setLoading] = useState(false);
  const location = useLocation();

  const handleGoogleLogin = () => {
    setLoading(true);

    const state = location.state as OAuthLocationState | null;

    const redirectTo = state?.redirectTo || "/event";

    sessionStorage.setItem(
      "devs_oauth_redirect",
      redirectTo,
    );

    window.location.href = getGoogleOAuthURL();
  };

  return (
    <main className="oauth-page">

      {/* Decorative grid */}
      <div className="oauth-grid" />

      {/* Main authentication card */}
      <section className="oauth-card">

        {/* Top label */}
        <div className="oauth-card-top">
          <span>DEVS // AUTHENTICATION</span>
          <span>26</span>
        </div>

        {/* Header */}
        <div className="oauth-header">

          <div className="oauth-brand">
            DEVS
          </div>

          <div className="oauth-line" />

          <h1>
            INVESTITURE<span>-26</span>
          </h1>

          <p className="oauth-subtitle">
            STUDENT AUTHENTICATION PORTAL
          </p>

        </div>

        {/* Login section */}
        <div className="oauth-login-box">

          <div className="oauth-status">
            <span className="status-dot" />
            AUTHENTICATION REQUIRED
          </div>

          <p className="oauth-description">
            Sign in using your Rajalakshmi Engineering College
            Google account to continue.
          </p>

          <button
            type="button"
            className="oauth-google-button"
            onClick={handleGoogleLogin}
            disabled={loading}
          >
            <span className="google-icon">
              G
            </span>

            <span>
              {loading
                ? "REDIRECTING..."
                : "CONTINUE WITH GOOGLE"}
            </span>

            <span className="oauth-arrow">
              →
            </span>
          </button>

        </div>

        {/* Bottom information */}
        <div className="oauth-footer">

          <span>
            SECURE ACCESS
          </span>

          <span className="footer-divider">
            //
          </span>

          <span>
            REC STUDENTS ONLY
          </span>

        </div>

        {/* Corner decorations */}
        <span className="corner corner-tl" />
        <span className="corner corner-tr" />
        <span className="corner corner-bl" />
        <span className="corner corner-br" />

      </section>

      {/* Bottom page label */}
      <div className="oauth-page-label">
        <span>INVESTITURE-26</span>
        <span>DEVS REC</span>
      </div>

    </main>
  );
}