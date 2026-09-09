import "./MatrixRain.css";

const columns = [
  "7F2A91",
  "K4X8P",
  "01D9",
  "V7M2Q",
  "A83Z",
  "9X4B71",
  "R2K8",
  "5NQ",
  "D7F91",
  "3X8M",
  "P4V6",
  "81ZQ",
  "L9C2",
  "7A5K",
  "M3R8",
  "Q1F7",
  "6D2X",
  "B9V4",
  "8K3P",
  "Z7N1",
  "4Q8A",
  "F2M9",
  "6X7R",
  "C5V1",
  "9P3K",
  "H8D2",
  "2W7F",
  "N4X9",
  "5B8Q",
  "T1M6",
];

export default function MatrixRain() {
  return (
    <div className="matrix-rain" aria-hidden="true">
      {columns.map((characters, index) => (
        <div
          className="matrix-column"
          key={index}
          style={{
            left: `${(index / columns.length) * 100}%`,
            animationDelay: `${(index * 0.37) % 4}s`,
            animationDuration: `${3.5 + ((index * 0.73) % 3)}s`,
          }}
        >
          {characters.split("").map((character, charIndex) => (
            <span
              key={charIndex}
              className={
                charIndex === characters.length - 1
                  ? "matrix-character matrix-head"
                  : "matrix-character"
              }
              style={{
                animationDelay: `${charIndex * 0.08}s`,
              }}
            >
              {character}
            </span>
          ))}
        </div>
      ))}
    </div>
  );
}