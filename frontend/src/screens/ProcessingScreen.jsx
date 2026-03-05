import { motion } from 'framer-motion';

const defaultSteps = [
  'Uploading Resume',
  'Extracting Skills',
  'Analyzing Experience',
  'Matching Job Roles',
  'Calculating Score',
];

const floatingSkills = ['Python', 'FastAPI', 'React', 'SQL', 'Docker', 'Kubernetes', 'AWS'];

export default function ProcessingScreen({ progress }) {
  return (
    <section className="min-h-screen flex items-center justify-center px-4">
      <div className="w-full max-w-4xl rounded-3xl border border-cyan-500/20 bg-zinc-950/60 p-8 md:p-10 backdrop-blur-md">
        <h2 className="text-3xl font-bold text-zinc-100">Analyzing your resume</h2>
        <p className="text-zinc-400 mt-2">Our AI is scanning your profile against role knowledge graphs.</p>

        <div className="mt-8 scanner-card">
          <motion.div
            className="scanner-line"
            animate={{ x: ['-10%', '110%'] }}
            transition={{ duration: 2.2, repeat: Infinity, ease: 'linear' }}
          />
          <div className="progress-shell">
            <motion.div
              className="progress-core"
              animate={{ width: `${Math.max(progress, 8)}%` }}
              transition={{ duration: 0.35 }}
            />
          </div>
        </div>

        <div className="mt-8 grid gap-3">
          {defaultSteps.map((step, index) => {
            const reached = progress >= ((index + 1) / defaultSteps.length) * 100;
            return (
              <motion.div
                key={step}
                initial={{ opacity: 0, x: -10 }}
                animate={{ opacity: 1, x: 0 }}
                transition={{ delay: index * 0.1 }}
                className={`step-item ${reached ? 'step-item-active' : ''}`}
              >
                <span>{step}</span>
                <span>{reached ? 'Done' : '...'}</span>
              </motion.div>
            );
          })}
        </div>

        <div className="mt-10 relative h-20 overflow-hidden rounded-xl border border-zinc-800 bg-zinc-900/60">
          {floatingSkills.map((skill, index) => (
            <motion.span
              key={skill}
              className="float-skill"
              initial={{ x: '-15%' }}
              animate={{ x: '110%' }}
              transition={{
                duration: 6 + index,
                delay: index * 0.35,
                repeat: Infinity,
                ease: 'linear',
              }}
              style={{ top: `${8 + (index % 3) * 24}px` }}
            >
              {skill}
            </motion.span>
          ))}
        </div>
      </div>
    </section>
  );
}
