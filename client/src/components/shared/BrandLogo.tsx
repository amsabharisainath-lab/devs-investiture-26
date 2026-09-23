import devsLogo from "../../assets/logo.png";

interface BrandLogoProps {
  size?: "sm" | "lg";
  progress?: number; // 0 to 100. If undefined, renders as static solid white.
}

export default function BrandLogo({ size = "sm", progress }: BrandLogoProps) {
  const isStatic = progress === undefined;

  // y = 0 is fully filled, y = 82 is empty (for lg size loader viewport height)
  const getWaveY = () => {
    if (progress === undefined) return 0;
    const slosh = Math.sin(progress * 0.22) * 3 * (1 - progress / 100);
    return 82 - (progress / 100) * 82 + slosh;
  };

  const yLevel = getWaveY();

  return (
    <div className={`brand-logo-container size-${size}`}>
      <div className="brand-logo-wrapper" style={{ position: "relative", display: "inline-flex", alignItems: "flex-end" }}>
        {isStatic ? (
          // Use the authoritative logo PNG directly for static header displays
          <img
            src={devsLogo}
            alt="DEVS"
            className="brand-logo-img"
            style={{ display: "block", width: "auto" }}
          />
        ) : (
          // Liquid animation wordmark using CSS mask image to clip sloshing wave
          <div
            className="brand-logo-mask-container"
            style={{
              position: "relative",
              width: "280px",
              height: "82px",
              overflow: "hidden",
            }}
          >
            {/* Outline background layer */}
            <img
              src={devsLogo}
              alt=""
              style={{
                position: "absolute",
                inset: 0,
                width: "100%",
                height: "100%",
                opacity: 0.15,
                objectFit: "contain",
                pointerEvents: "none",
              }}
            />

            {/* Sloshing Progress Layer masked to logo shape */}
            <div
              style={{
                position: "absolute",
                inset: 0,
                width: "100%",
                height: "100%",
                WebkitMaskImage: `url(${devsLogo})`,
                maskImage: `url(${devsLogo})`,
                WebkitMaskSize: "contain",
                maskSize: "contain",
                WebkitMaskRepeat: "no-repeat",
                maskRepeat: "no-repeat",
              }}
            >
              {/* Sloshing Wave translating vertically */}
              <div
                style={{
                  position: "absolute",
                  inset: 0,
                  width: "100%",
                  height: "100%",
                  transform: `translateY(${yLevel}px)`,
                  transition: "transform 80ms linear",
                }}
              >
                <svg
                  viewBox="0 0 340 100"
                  width="100%"
                  height="100%"
                  xmlns="http://www.w3.org/2000/svg"
                  className="brand-logo-svg"
                  style={{ display: "block", overflow: "visible" }}
                >
                  <path
                    className="wave-path"
                    d="M -200 0 C -100 8, -100 -8, 0 0 C 100 8, 100 -8, 200 0 C 300 8, 300 -8, 400 0 C 500 8, 500 -8, 600 0 L 600 200 L -200 200 Z"
                    fill="white"
                  />
                </svg>
              </div>
            </div>
          </div>
        )}

        {/* Separately styled baseline dot next to the logo image */}
        <span className="brand-dot" />
      </div>
    </div>
  );
}
