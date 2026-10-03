import { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import { getMe } from "../api/api";

export default function OAuthCallback() {
  const navigate = useNavigate();

  const [error, setError] = useState("");

  useEffect(() => {
    let cancelled = false;

    async function finishLogin() {
      try {
        const response = await getMe();

        if (cancelled) return;

        if (!response.authenticated || !response.user) {
          setError("Authentication failed. Please try again.");
          return;
        }

        const user = response.user;

        const profileComplete =
          Boolean(user.name) &&
          Boolean(user.roll_no) &&
          Boolean(user.department) &&
          user.year !== null;

        /*
         * Remember where the user originally wanted to go.
         */
        const redirectTo =
          sessionStorage.getItem("devs_oauth_redirect") ||
          "/event";

        sessionStorage.removeItem("devs_oauth_redirect");

        /*
         * If profile is incomplete, user must complete
         * registration/profile information first.
         */
        if (!profileComplete) {
          navigate("/register", {
            replace: true,
            state: {
              redirectTo,
            },
          });

          return;
        }

        /*
         * Profile is complete → send them to
         * the page they originally requested.
         */
        navigate(redirectTo, {
          replace: true,
        });
      } catch (err) {
        if (!cancelled) {
          setError(
            err instanceof Error
              ? err.message
              : "Unable to complete login.",
          );
        }
      }
    }

    finishLogin();

    return () => {
      cancelled = true;
    };
  }, [navigate]);

  if (error) {
    return (
      <main className="oauth-page">
        <section className="oauth-container">
          <h1>LOGIN FAILED</h1>

          <p>{error}</p>

          <button
            type="button"
            onClick={() => navigate("/oauth")}
          >
            TRY AGAIN
          </button>
        </section>
      </main>
    );
  }

  return (
    <main className="oauth-page">
      <section className="oauth-container">
        <h1>AUTHENTICATING...</h1>

        <p>Please wait.</p>
      </section>
    </main>
  );
}