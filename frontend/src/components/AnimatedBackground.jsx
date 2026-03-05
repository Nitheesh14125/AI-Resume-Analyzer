import { motion } from 'framer-motion';

export default function AnimatedBackground() {
  return (
    <div className="background-layer" aria-hidden>
      <div className="mesh mesh-cyan" />
      <div className="mesh mesh-violet" />
      <div className="mesh mesh-blue" />
      {[...Array(20)].map((_, index) => (
        <motion.span
          key={index}
          className="particle"
          initial={{ opacity: 0, y: 0 }}
          animate={{ opacity: [0.1, 0.7, 0.1], y: [0, -40, 0] }}
          transition={{
            duration: 4 + (index % 6),
            repeat: Infinity,
            delay: index * 0.2,
            ease: 'easeInOut',
          }}
          style={{
            left: `${(index * 13) % 100}%`,
            top: `${(index * 21) % 100}%`,
          }}
        />
      ))}
    </div>
  );
}
