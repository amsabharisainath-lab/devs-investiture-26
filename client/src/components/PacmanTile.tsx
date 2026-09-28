import type { ReactNode } from "react";

interface PacmanTileProps {
  children: ReactNode;
  className?: string;
}

export default function PacmanTile({
  children,
  className = "",
}: PacmanTileProps) {
  return (
    <div className={`pacman-tile ${className}`.trim()}>
      <div className="pacman-tile-content">
        {children}
      </div>

      <span
        className="pacman-eater"
        aria-hidden="true"
      />

      <span
        className="pacman"
        aria-hidden="true"
      />
    </div>
  );
}