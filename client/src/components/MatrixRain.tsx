import "./MatrixRain.css";

const CHARACTERS =
  "ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789#$%&*+=<>";

const COLUMN_COUNT = 72;

function random(seed: number) {
  const x = Math.sin(seed * 12.9898) * 43758.5453;
  return x - Math.floor(x);
}

function makeString(seed: number) {
  const length = 8 + Math.floor(random(seed) * 14);

  return Array.from({ length }, (_, index) => {
    const value = Math.floor(
      random(seed * 100 + index * 17.37) * CHARACTERS.length
    );

    return CHARACTERS[value];
  }).join("");
}

export default function MatrixRain() {
  const columns = Array.from({ length: COLUMN_COUNT }, (_, index) => {
    return {
      id: index,
      characters: makeString(index + 1),
      left: random(index + 10) * 100,
      duration: 3.4 + random(index + 30) * 3.8,
      delay: -(random(index + 60) * 7),
      scale: 0.8 + random(index + 90) * 0.45,
    };
  });

  return (
    <div className="matrix-rain" aria-hidden="true">
      {columns.map((column) => (
        <div
          className="matrix-column"
          key={column.id}
          style={
            {
              "--matrix-left": `${column.left}%`,
              "--matrix-duration": `${column.duration}s`,
              "--matrix-delay": `${column.delay}s`,
              "--matrix-scale": column.scale,
            } as React.CSSProperties
          }
        >
          {column.characters.split("").map((character, charIndex) => (
            <span
              key={charIndex}
              className={
                charIndex === 0
                  ? "matrix-character matrix-head"
                  : "matrix-character"
              }
            >
              {character}
            </span>
          ))}
        </div>
      ))}
    </div>
  );
}
