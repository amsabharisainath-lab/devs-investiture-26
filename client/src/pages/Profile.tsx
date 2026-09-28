import { useNavigate } from "react-router-dom";

export default function Profile() {
  const navigate = useNavigate();

  return (
    <main className="profile-page">
      <section className="profile-container">

        {/* PAGE TITLE */}
        <h1 className="profile-page-title">
          MY PROFILE
        </h1>

        {/* NAME */}
        <section className="profile-tile">
          <h2>NAME</h2>

          <div className="profile-value">
            {/* Student name will appear here */}
          </div>
        </section>

        {/* DEPARTMENT */}
        <section className="profile-tile">
          <h2>DEPARTMENT</h2>

          <div className="profile-value">
            {/* Department will appear here */}
          </div>
        </section>

        {/* YEAR */}
        <section className="profile-tile">
          <h2>YEAR</h2>

          <div className="profile-value">
            {/* Year will appear here */}
          </div>
        </section>

        {/* REGISTER NUMBER */}
        <section className="profile-tile">
          <h2>REGISTER NUMBER</h2>

          <div className="profile-value">
            {/* Register number will appear here */}
          </div>
        </section>

        {/* GO BACK */}
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