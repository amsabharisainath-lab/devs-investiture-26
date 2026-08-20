import { useNavigate } from "react-router-dom";

export default function Profile() {
  const navigate = useNavigate();

  return (
    <main className="profile-page">

      <section className="profile-card">

        <h1>
          MY PROFILE
        </h1>

        <div className="profile-details">

          <p>
            NAME
          </p>

          <p>
            DEPARTMENT
          </p>

          <p>
            YEAR
          </p>

          <p>
            REGISTER NUMBER
          </p>

        </div>

        <button
          className="go-back-button"
          type="button"
          onClick={() => navigate("/event")}
        >
          GO BACK
        </button>

      </section>

    </main>
  );
}