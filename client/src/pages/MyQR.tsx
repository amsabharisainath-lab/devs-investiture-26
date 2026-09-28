import { useNavigate } from "react-router-dom";

export default function MyQR() {
  const navigate = useNavigate();

  return (
    <main className="qr-page">
      <section className="qr-container">

        {/* PAGE TITLE */}
        <h1 className="qr-page-title">
          MY QR
        </h1>

        {/* ENTRY QR */}
        <section className="qr-tile">
          <h2>ENTRY QR</h2>

          <div className="qr-display">
            <span>QR CODE</span>
          </div>
        </section>

        {/* EXIT QR */}
        <section className="qr-tile">
          <h2>EXIT QR</h2>

          <div className="qr-display">
            <span>QR CODE</span>
          </div>
        </section>

        {/* BACK */}
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