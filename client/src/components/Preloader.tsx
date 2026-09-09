import { useEffect, useState } from "react";
import "./Preloader.css";
import MatrixRain from "./MatrixRain";

export default function Preloader() {
  const [progress, setProgress] = useState(0);
  const [exiting, setExiting] = useState(false);
  const [visible, setVisible] = useState(true);

  useEffect(() => {
    const duration = 4500;
    const start = performance.now();

    let animationFrame: number;
    let exitTimer: ReturnType<typeof setTimeout>;
    let hideTimer: ReturnType<typeof setTimeout>;

    const updateProgress = (time: number) => {
      const elapsed = time - start;

      const percentage = Math.min(
        100,
        Math.floor((elapsed / duration) * 100)
      );

      setProgress(percentage);

      if (elapsed < duration) {
        animationFrame = requestAnimationFrame(updateProgress);
      } else {
        setProgress(100);

        exitTimer = setTimeout(() => {
          setExiting(true);

          hideTimer = setTimeout(() => {
            setVisible(false);
          }, 850);
        }, 450);
      }
    };

    animationFrame = requestAnimationFrame(updateProgress);

    return () => {
      cancelAnimationFrame(animationFrame);
      clearTimeout(exitTimer);
      clearTimeout(hideTimer);
    };
  }, []);

  if (!visible) {
    return null;
  }

  const letters = ["D", "E", "V", "S"];

  return (
    <div
      className={`preloader ${
        exiting ? "preloader-exiting" : ""
      }`}
    >

      {/* ================================
          MATRIX BACKGROUND
         ================================= */}

      <MatrixRain />


      {/* ================================
          DEVS
         ================================= */}

      <div className="devs-loader">

        {letters.map((letter, index) => (
          <div
            className={`devs-letter letter-${index}`}
            key={letter}
          >

            {/* Hollow outline */}

            <span className="letter-outline">
              {letter}
            </span>


            {/* Liquid fill */}

            <span className="letter-fill">
              {letter}
            </span>

          </div>
        ))}

      </div>


      {/* ================================
          CODE-COFFEE-REPEAT
         ================================= */}

      <div className="preloader-tagline">

        {"CODE-COFFEE-REPEAT".split("").map(
          (character, index) => (
            <span
              key={index}
              style={{
                animationDelay: `${0.18 + index * 0.075}s`,
              }}
            >
              {character === " "
                ? "\u00A0"
                : character}
            </span>
          )
        )}

      </div>


      {/* ================================
          PERCENTAGE
         ================================= */}

      <div className="preloader-percentage">
        {progress}%
      </div>

    </div>
  );
}