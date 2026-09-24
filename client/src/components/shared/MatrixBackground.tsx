import { useEffect, useRef } from "react";

export default function MatrixBackground() {
  const canvasRef = useRef<HTMLCanvasElement>(null);

  useEffect(() => {
    const canvas = canvasRef.current;
    if (!canvas) return;

    const ctx = canvas.getContext("2d");
    if (!ctx) return;

    let animationId: number;

    const resizeCanvas = () => {
      canvas.width = window.innerWidth;
      canvas.height = window.innerHeight;
    };

    resizeCanvas();
    window.addEventListener("resize", resizeCanvas);

    // Subtle sparse letters to drift down
    const chars = "0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZDEVSINVESTITURE";
    const fontSize = 10;
    const columns = Math.floor(canvas.width / 20); // Sparse spacing
    const drops: number[] = Array(columns).fill(1);

    const draw = () => {
      // Extremely high transparency black fade to create trails
      ctx.fillStyle = "rgba(0, 0, 0, 0.08)";
      ctx.fillRect(0, 0, canvas.width, canvas.height);

      // Low contrast white-gray characters
      ctx.fillStyle = "rgba(255, 255, 255, 0.035)";
      ctx.font = `${fontSize}px monospace`;

      for (let i = 0; i < drops.length; i++) {
        // Draw characters slowly and sparsely
        if (Math.random() > 0.96 || drops[i] > 1) {
          const char = chars[Math.floor(Math.random() * chars.length)];
          const x = i * 20;
          const y = drops[i] * fontSize;

          ctx.fillText(char, x, y);

          // Reset when character flows past height or randomly
          if (y > canvas.height && Math.random() > 0.985) {
            drops[i] = 0;
          }
          drops[i] += 0.5; // Very slow crawl
        }
      }
      animationId = requestAnimationFrame(draw);
    };

    draw();

    return () => {
      window.removeEventListener("resize", resizeCanvas);
      cancelAnimationFrame(animationId);
    };
  }, []);

  return (
    <canvas
      ref={canvasRef}
      style={{
        position: "fixed",
        inset: 0,
        zIndex: -1,
        pointerEvents: "none",
        backgroundColor: "#000000",
      }}
    />
  );
}
