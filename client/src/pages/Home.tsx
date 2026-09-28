import { useState } from "react";
import { useNavigate } from "react-router-dom";
import Sidebar from "../components/Sidebar";
import PacmanTile from "../components/PacmanTile";

import devsLogo from "../assets/devs-header.jpeg";
import chiefGuestPhoto from "../assets/chief-guest.jpg";
import specialGuestPhoto from "../assets/special-guest.jpg";

export default function Home() {

  const [sidebarOpen, setSidebarOpen] = useState(false);
  const navigate = useNavigate();

  return (
    <main className="home-page">

      {/* =================================================
          SIDEBAR
         ================================================= */}

      {sidebarOpen && (
        <Sidebar
          canAccessUserPages={false}
          onClose={() => setSidebarOpen(false)}
        />
      )}


      {/* =================================================
          HEADER
         ================================================= */}

      <PacmanTile>


        <section className="home-header">

        {/* Hamburger / Sidebar Button */}
        <button
          className="menu-button"
          type="button"
          aria-label="Open menu"
          onClick={() => setSidebarOpen(true)}
        >
          <span />
          <span />
          <span />
        </button>


        {/* DEVS LOGO */}
        <div className="home-brand">
          <img
            src={devsLogo}
            alt="DEVS"
          />
        </div>


        {/* EVENT TITLE */}
        <h1 className="event-title hollow title">
          INVESTITURE-26
        </h1>

      </section>


      </PacmanTile>


      {/* =================================================
          SIGN IN
         ================================================= */}

      <section className="signin-section">


        <PacmanTile className="pacman-signin pacman-fast">


          <button
          className="signin-button"
          type="button"
          onClick={() => navigate("/register")}
        >
          SIGN IN
        </button>


        </PacmanTile>


      </section>


      {/* =================================================
          GUEST INFORMATION
         ================================================= */}

      <PacmanTile>


        <section className="event-card">

        {/* =================================================
            CHIEF GUEST
           ================================================= */}

        <div className="guest-info-card">

          {/* Chief Guest Photo — LEFT */}
          <img
            className="guest-photo"
            src={chiefGuestPhoto}
            alt="Chief Guest"
          />


          {/* Chief Guest Information — RIGHT */}
          <div className="guest-content">

            <h2>
              ABOUT CHIEF GUEST
            </h2>

            <p className="guest-description">
              Our chief guest for INVESTITURE-26 is an
              accomplished personality who has made
              significant contributions in their field.
              More information about the chief guest,
              achievements, designation and professional
              journey will be added here.
            </p>

          </div>

        </div>


        {/* =================================================
            SPECIAL GUEST
           ================================================= */}

        <div className="guest-info-card">

          {/* Guest Photo — LEFT */}
          <img
            className="guest-photo"
            src={specialGuestPhoto}
            alt="Guest"
          />


          {/* Guest Information — RIGHT */}
          <div className="guest-content">

            <h2>
              ABOUT CHIEF GUEST
            </h2>

            <p className="guest-description">
              Our guest for INVESTITURE-26 brings
              valuable experience and insights to the
              event. Details about the guest, their
              designation, achievements and background
              will be added here later.
            </p>

          </div>

        </div>

      </section>


      </PacmanTile>


      {/* =================================================
          VENUE + TIMINGS
         ================================================= */}

      <PacmanTile>


        <section className="venue-timing-card">

        {/* VENUE */}
        <div className="venue-timing-item">

          <h2>
            VENUE
          </h2>

          <p>
            Rajalakshmi Engineering College
          </p>

        </div>


        {/* TIMINGS */}
        <div className="venue-timing-item">

          <h2>
            TIMING
          </h2>

          <p>
            Date and timing will be updated here.
          </p>

        </div>

      </section>


      </PacmanTile>


      {/* =================================================
          SOCIAL LINKS
         ================================================= */}

      <PacmanTile className="pacman-slow">


        <footer className="social-card">

        {/* LinkedIn */}
        <a
          href="https://www.linkedin.com/in/devsrec/"
          target="_blank"
          rel="noopener noreferrer"
          aria-label="LinkedIn"
          className="social-icon"
        >

          <svg
            viewBox="0 0 24 24"
            aria-hidden="true"
          >
            <path
              fill="currentColor"
              d="M6.5 8.5A1.5 1.5 0 1 0 6.5 5a1.5 1.5 0 0 0 0 3.5ZM5 9.5h3v9H5v-9Zm5 0h2.9v1.23h.04c.4-.76 1.39-1.56 2.86-1.56 3.06 0 3.63 2.02 3.63 4.65v4.68h-3v-4.15c0-.99-.02-2.26-1.38-2.26-1.39 0-1.6 1.08-1.6 2.19v4.22h-3v-9Z"
            />
          </svg>

        </a>


        {/* Instagram */}
        <a
          href="https://www.instagram.com/devsrec/?hl=en"
          target="_blank"
          rel="noopener noreferrer"
          aria-label="Instagram"
          className="social-icon"
        >

          <svg
            viewBox="0 0 24 24"
            aria-hidden="true"
          >

            <rect
              x="4"
              y="4"
              width="16"
              height="16"
              rx="4"
              fill="none"
              stroke="currentColor"
              strokeWidth="2"
            />

            <circle
              cx="12"
              cy="12"
              r="3.5"
              fill="none"
              stroke="currentColor"
              strokeWidth="2"
            />

            <circle
              cx="17.2"
              cy="6.8"
              r="1"
              fill="currentColor"
            />

          </svg>

        </a>

      </footer>


      </PacmanTile>

    </main>
  );
}