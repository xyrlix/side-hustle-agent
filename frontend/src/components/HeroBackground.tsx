import { useEffect, useRef } from "react";

function Orb({ className, color }: { className: string; color: string }) {
  return (
    <div
      className={`absolute rounded-full blur-3xl opacity-25 pointer-events-none ${className}`}
      style={{ background: color }}
    />
  );
}

export default function HeroBackground() {
  const canvasRef = useRef<HTMLCanvasElement>(null);

  useEffect(() => {
    const canvas = canvasRef.current;
    if (!canvas) return;
    const ctx = canvas.getContext("2d");
    if (!ctx) return;

    let animId: number;
    let angle = 0;

    const resize = () => {
      canvas.width = canvas.offsetWidth;
      canvas.height = canvas.offsetHeight;
    };
    resize();

    const draw = () => {
      ctx.clearRect(0, 0, canvas.width, canvas.height);
      const cx = canvas.width / 2;
      const cy = canvas.height / 2;
      const maxR = Math.min(cx, cy) * 0.9;

      // Grid rings — more visible
      for (let i = 1; i <= 3; i++) {
        ctx.beginPath();
        ctx.arc(cx, cy, (maxR / 3) * i, 0, Math.PI * 2);
        ctx.strokeStyle = `rgba(196, 181, 253, ${0.12 + i * 0.04})`;
        ctx.lineWidth = 1;
        ctx.stroke();
      }

      // Cross lines
      for (let a = 0; a < Math.PI * 2; a += Math.PI / 4) {
        ctx.beginPath();
        ctx.moveTo(cx, cy);
        ctx.lineTo(cx + Math.cos(a) * maxR, cy + Math.sin(a) * maxR);
        ctx.strokeStyle = "rgba(196, 181, 253, 0.15)";
        ctx.lineWidth = 1;
        ctx.stroke();
      }

      // Sweep cone — brighter purple glow
      const sweepAngle = (angle * Math.PI) / 180;
      ctx.save();
      ctx.beginPath();
      ctx.moveTo(cx, cy);
      ctx.arc(cx, cy, maxR, sweepAngle - 0.8, sweepAngle);
      ctx.closePath();
      try {
        const sweepGrad = ctx.createConicGradient(sweepAngle, cx, cy);
        sweepGrad.addColorStop(0, "rgba(196, 181, 253, 0)");
        sweepGrad.addColorStop(0.7, "rgba(196, 181, 253, 0.28)");
        sweepGrad.addColorStop(1, "rgba(196, 181, 253, 0)");
        ctx.fillStyle = sweepGrad;
      } catch {
        ctx.fillStyle = "rgba(139, 92, 246, 0.2)";
      }
      ctx.fill();
      ctx.restore();

      // Sweep line — bright
      ctx.beginPath();
      ctx.moveTo(cx, cy);
      ctx.lineTo(cx + Math.cos(sweepAngle) * maxR, cy + Math.sin(sweepAngle) * maxR);
      ctx.strokeStyle = "rgba(233, 213, 255, 0.95)";
      ctx.lineWidth = 2.5;
      ctx.stroke();

      // Ping ring — more visible
      const pingPhase = (Date.now() % 3000) / 3000;
      const pingR = maxR * pingPhase * 1.2;
      ctx.beginPath();
      ctx.arc(cx, cy, pingR, 0, Math.PI * 2);
      ctx.strokeStyle = `rgba(196, 181, 253, ${(1 - pingPhase) * 0.55})`;
      ctx.lineWidth = 2;
      ctx.stroke();

      // Center dot — bright white-purple
      ctx.beginPath();
      ctx.arc(cx, cy, 5, 0, Math.PI * 2);
      ctx.fillStyle = "rgba(233, 213, 255, 1)";
      ctx.fill();

      // Outer glow ring
      ctx.beginPath();
      ctx.arc(cx, cy, 10, 0, Math.PI * 2);
      ctx.fillStyle = "rgba(196, 181, 253, 0.3)";
      ctx.fill();

      angle += 0.4;
      animId = requestAnimationFrame(draw);
    };

    draw();
    return () => cancelAnimationFrame(animId);
  }, []);

  const particles = Array.from({ length: 20 }, (_, i) => ({
    id: i,
    left: `${5 + Math.random() * 90}%`,
    bottom: `${5 + Math.random() * 30}%`,
    delay: `${Math.random() * 4}s`,
    duration: `${3 + Math.random() * 3}s`,
    size: 1.5 + Math.random() * 2.5,
  }));

  return (
    <div className="relative w-full h-full overflow-hidden rounded-3xl">
      {/* Ambient orbs — brighter */}
      <Orb className="w-[500px] h-[500px] -top-40 -left-40" color="rgba(139,92,246,0.7)" />
      <Orb className="w-[400px] h-[400px] top-10 right-[-100px]" color="rgba(236,72,153,0.5)" />
      <Orb className="w-[350px] h-[350px] bottom-0 left-[20%]" color="rgba(99,102,241,0.5)" />

      {/* Radar canvas */}
      <canvas
        ref={canvasRef}
        className="absolute inset-0 w-full h-full"
        style={{ opacity: 0.9 }}
      />

      {/* Floating particles */}
      {particles.map(p => (
        <div
          key={p.id}
          className="absolute rounded-full"
          style={{
            left: p.left,
            bottom: p.bottom,
            width: p.size,
            height: p.size,
            background: "rgba(196, 181, 253, 0.8)",
            animation: `float-up ${p.duration} ${p.delay} ease-out infinite`,
          }}
        />
      ))}

      {/* Grid pattern overlay */}
      <div
        className="absolute inset-0 opacity-20"
        style={{
          backgroundImage: "linear-gradient(rgba(167,139,250,0.15) 1px, transparent 1px), linear-gradient(90deg, rgba(167,139,250,0.15) 1px, transparent 1px)",
          backgroundSize: "40px 40px",
        }}
      />

      {/* Gradient vignette */}
      <div
        className="absolute inset-0 rounded-3xl"
        style={{
          background: "radial-gradient(ellipse at center, transparent 20%, rgba(30,27,75,0.5) 100%)",
        }}
      />
    </div>
  );
}
