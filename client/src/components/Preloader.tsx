import { useEffect, useState } from "react";
import "./Preloader.css";
import MatrixRain from "./MatrixRain";

interface PreloaderProps {
  onComplete?: () => void;
}

export default function Preloader({
  onComplete,
}: PreloaderProps) {
  const [progress, setProgress] = useState(0);
  const [isExiting, setIsExiting] = useState(false);

  useEffect(() => {
    const duration = 3500;
    const startTime = performance.now();

    let animationFrame = 0;
    let exitTimer: ReturnType<typeof setTimeout>;
    let completeTimer: ReturnType<typeof setTimeout>;

    const update = (currentTime: number) => {
      const elapsed = currentTime - startTime;

      const percentage = Math.min(
        (elapsed / duration) * 100,
        100
      );

      setProgress(percentage);

      if (percentage < 100) {
        animationFrame =
          requestAnimationFrame(update);
      } else {
        completeTimer = setTimeout(() => {
          setIsExiting(true);

          exitTimer = setTimeout(() => {
            onComplete?.();
          }, 750);
        }, 200);
      }
    };

    animationFrame =
      requestAnimationFrame(update);

    return () => {
      cancelAnimationFrame(animationFrame);
      clearTimeout(completeTimer);
      clearTimeout(exitTimer);
    };
  }, [onComplete]);

  /*
   * This is the important part.
   *
   * Original CodePen:
   *
   * background-position: top
   *       ↓
   * background-position: bottom
   *
   * We simply drive that same animation
   * continuously with React.
   */
  const fillPosition = `${progress}%`;

  /*
   * Typing animation timing.
   *
   * The tagline has 20 characters.
   * It will type throughout the first ~2 seconds.
   */
  const taglineLength = "CODE-COFFEE-REPEAT".length;

  const typedCharacters = Math.floor(
    (progress / 100) *
      taglineLength
  );

  const typedText =
    "CODE-COFFEE-REPEAT".slice(
      0,
      typedCharacters
    );

  return (
    <div
      className={`preloader ${
        isExiting ? "preloader-exit" : ""
      }`}
    >
      {/* =====================================
          MATRIX BACKGROUND
      ====================================== */}

      <MatrixRain />

      {/* =====================================
          CENTER DARKENING
      ====================================== */}

      <div className="matrix-vignette" />

      {/* =====================================
          MAIN CONTENT
      ====================================== */}

      <main className="preloader-content">

        {/* ===================================
            DEVS LOGO
        ==================================== */}

        <div
          className="devs-wrapper"
          style={
            {
              "--fill-position":
                `${fillPosition}`,
            } as React.CSSProperties
          }
        >
          {/* OUTLINE */}
          <div className="devs-outline">
            DEVS.
          </div>

          {/* WHITE FILL */}
          <div className="devs-liquid">
            DEVS.
          </div>
        </div>


        {/* ===================================
            TAGLINE
        ==================================== */}

        <div className="tagline">
          <span>{typedText}</span>

          <span className="typing-cursor">
            |
          </span>
        </div>

      </main>


      {/* =====================================
          PERCENTAGE
      ====================================== */}

      <div className="loading-percentage">
        {Math.floor(progress)
          .toString()
          .padStart(3, "0")}
        %
      </div>

    </div>
  );
}