import { useNavigate } from "react-router-dom";

export default function MyQR() {
  const navigate = useNavigate();

  return (
    <main className="qr-page">

      <section className="qr-card">

        <h1>
          MY QR
        </h1>

        <div className="qr-placeholder">
          QR CODE
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