import { useEffect, useState } from "react";
import MatrixBackground from "./MatrixBackground";
import BrandLogo from "./BrandLogo";

interface LoadingStateProps {
  onComplete?: () => void;
  duration?: number;
}

export default function LoadingState({ onComplete, duration = 2500 }: LoadingStateProps) {
  const [progress, setProgress] = useState(0);
  const [isFadingOut, setIsFadingOut] = useState(false);

  useEffect(() => {
    const startTime = Date.now();

    const updateProgress = () => {
      const elapsed = Date.now() - startTime;
      const t = Math.min(elapsed / duration, 1);

      // Deceleration easing curve to simulate organic liquid flow slowing down near top
      const easedT = 1 - Math.pow(1 - t, 2.5);
      const pct = Math.min(Math.round(easedT * 100), 100);
      setProgress(pct);

      if (pct < 100) {
        requestAnimationFrame(updateProgress);
      } else {
        // Hold for 1 second (1000ms) at 100% progress
        const holdTimer = setTimeout(() => {
          setIsFadingOut(true);
          // Wait 600ms for slide-up transition to complete before unmounting
          const doneTimer = setTimeout(() => {
            if (onComplete) onComplete();
          }, 600);
          return () => clearTimeout(doneTimer);
        }, 1000);
        return () => clearTimeout(holdTimer);
      }
    };

    const frameId = requestAnimationFrame(updateProgress);
    return () => cancelAnimationFrame(frameId);
  }, [duration, onComplete]);

  return (
    <div className={`loading-overlay ${isFadingOut ? "fade-out" : ""}`}>
      {/* Matrix background is rendered inside the loader only */}
      <MatrixBackground />

      <div className="loading-container">
        <div className="loading-visual-area">
          <div className="loader-logo-wrapper">
            {/* Reusable Brand Logo component in animated state */}
            <BrandLogo size="lg" progress={progress} />

            {/* INVESTITURE Subtext */}
            <div className="loader-subtext">INVESTITURE</div>

            {/* DEVS Monospace Signature */}
            <div className="loader-signature">INVESTITURE OPERATIONS</div>
          </div>
        </div>

        <div className="loading-status-area">
          <div className="status-row">
            <span className="status-label">LOADING</span>
            <span className="status-percentage">{progress}%</span>
          </div>
          <div className="progress-bar-container">
            <div className="progress-bar-fill" style={{ width: `${progress}%` }}></div>
          </div>
        </div>
      </div>
    </div>
  );
}
