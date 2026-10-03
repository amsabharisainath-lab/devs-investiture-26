import { useEffect, useMemo, useRef, useState } from "react";
import type { CSSProperties, ReactNode } from "react";

interface PacmanTileProps {
  children: ReactNode;
  className?: string;
}

interface DotStyle extends CSSProperties {
  "--dot-position": string;
}

const DEFAULT_SPEED_MS = 5000;

/*
 * The SIGN IN tile is the speed reference.
 *
 * SIGN IN:
 *   --pacman-speed = 5s
 *
 * Every other tile calculates its duration from its perimeter so that
 * Pac-Man travels at the same physical pixels/second as the SIGN IN Pac-Man.
 */
const SIGNIN_DOT_SPACING_PX = 14;
const NORMAL_DOT_SPACING_PX = 12;

/* Keep exactly 3 dots eaten at any moment. */
const EATEN_DOT_BUFFER = 3;

function getBaseSpeedMs() {
  if (typeof window === "undefined") return DEFAULT_SPEED_MS;

  const value = getComputedStyle(document.documentElement)
    .getPropertyValue("--pacman-speed")
    .trim();

  if (value.endsWith("ms")) {
    const ms = Number.parseFloat(value);
    return Number.isFinite(ms) && ms > 0 ? ms : DEFAULT_SPEED_MS;
  }

  if (value.endsWith("s")) {
    const seconds = Number.parseFloat(value);
    return Number.isFinite(seconds) && seconds > 0
      ? seconds * 1000
      : DEFAULT_SPEED_MS;
  }

  return DEFAULT_SPEED_MS;
}

/*
 * Approximate the length of the CSS offset-path:
 * inset(2px round 5px)
 */
function getPathPerimeter(element: HTMLElement) {
  const rect = element.getBoundingClientRect();

  const width = Math.max(rect.width - 4, 1);
  const height = Math.max(rect.height - 4, 1);

  return Math.max(2 * (width + height), 1);
}

function isSignInTile(className: string) {
  return className.split(/\s+/).includes("pacman-signin");
}

export default function PacmanTile({
  children,
  className = "",
}: PacmanTileProps) {
  const tileRef = useRef<HTMLDivElement | null>(null);
  const isSignin = isSignInTile(className);

  const [pacmanProgress, setPacmanProgress] = useState(0);
  const [animationDuration, setAnimationDuration] =
    useState(DEFAULT_SPEED_MS);
  const [dotCount, setDotCount] = useState(40);

  /*
   * Measure each tile.
   *
   * The SIGN IN tile publishes its perimeter as the global reference.
   * Every other tile uses that reference to calculate its own duration.
   */
  useEffect(() => {
    const element = tileRef.current;
    if (!element) return;

    const updateMeasurements = () => {
      const perimeter = getPathPerimeter(element);
      const baseSpeed = getBaseSpeedMs();

      if (isSignin) {
        /* SIGN IN always runs at the configured base duration. */
        document.documentElement.style.setProperty(
          "--pacman-reference-perimeter",
          `${perimeter}px`,
        );

        document.documentElement.dispatchEvent(
          new Event("pacman-reference-updated"),
        );

        setAnimationDuration(baseSpeed);

        /* Keep SIGN IN comparatively sparse. */
        setDotCount(
          Math.max(20, Math.round(perimeter / SIGNIN_DOT_SPACING_PX)),
        );
        return;
      }

      const referenceValue = getComputedStyle(document.documentElement)
        .getPropertyValue("--pacman-reference-perimeter")
        .trim();

      const referencePerimeter = Number.parseFloat(referenceValue);

      if (!Number.isFinite(referencePerimeter) || referencePerimeter <= 0) {
        /* Temporary fallback until the SIGN IN tile publishes its size. */
        setAnimationDuration(baseSpeed);
      } else {
        /*
         * Same physical speed:
         *
         *   duration / perimeter = constant
         *
         * Therefore larger tiles take longer for a full lap, while the
         * Pac-Man itself moves at the same speed as the SIGN IN Pac-Man.
         */
        const duration =
          baseSpeed * (perimeter / referencePerimeter);

        setAnimationDuration(Math.max(baseSpeed * 0.35, duration));
      }

      /* More dots on normal/larger tiles than on SIGN IN. */
      setDotCount(
        Math.max(48, Math.ceil(perimeter / NORMAL_DOT_SPACING_PX)),
      );
    };

    updateMeasurements();

    const handleReferenceUpdate = () => {
      if (!isSignin) updateMeasurements();
    };

    document.documentElement.addEventListener(
      "pacman-reference-updated",
      handleReferenceUpdate,
    );

    const resizeObserver = new ResizeObserver(updateMeasurements);
    resizeObserver.observe(element);

    window.addEventListener("resize", updateMeasurements);

    return () => {
      document.documentElement.removeEventListener(
        "pacman-reference-updated",
        handleReferenceUpdate,
      );
      window.removeEventListener("resize", updateMeasurements);
      resizeObserver.disconnect();
    };
  }, [isSignin]);

  /*
   * The JS dot clock uses the EXACT SAME duration as the CSS Pac-Man
   * animation, keeping eating perfectly synchronized with Pac-Man.
   */
  useEffect(() => {
    let animationFrame = 0;
    const startTime = performance.now();

    const tick = (now: number) => {
      const elapsed = now - startTime;
      const progress =
        animationDuration > 0
          ? (elapsed % animationDuration) / animationDuration
          : 0;

      setPacmanProgress(progress);
      animationFrame = requestAnimationFrame(tick);
    };

    animationFrame = requestAnimationFrame(tick);

    return () => cancelAnimationFrame(animationFrame);
  }, [animationDuration]);

  const dots = useMemo(() => {
    return Array.from({ length: dotCount }, (_, index) => {
      const position = (index / dotCount) * 100;
      const dotProgress = index / dotCount;

      /* Circular distance behind Pac-Man. */
      const distanceBehind =
        ((pacmanProgress - dotProgress + 1) % 1) * dotCount;

      const isBeingEaten =
        distanceBehind >= 0 &&
        distanceBehind < EATEN_DOT_BUFFER;

      const style: DotStyle = {
        "--dot-position": `${position}%`,
        opacity: isBeingEaten ? 0 : 1,
        transform: isBeingEaten ? "scale(0.15)" : "scale(1)",
      };

      return (
        <span
          key={index}
          className="pacman-dot"
          style={style}
          aria-hidden="true"
        />
      );
    });
  }, [pacmanProgress, dotCount]);

  const tileStyle = {
    "--pacman-duration": `${animationDuration}ms`,
  } as CSSProperties;

  return (
    <div
      ref={tileRef}
      className={`pacman-tile ${className}`.trim()}
      style={tileStyle}
    >
      <div className="pacman-tile-content">{children}</div>

      {dots}

      <span className="pacman-eater" aria-hidden="true" />
      <span className="pacman" aria-hidden="true" />
    </div>
  );
}
