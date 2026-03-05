import {
  Bar,
  BarChart,
  Cell,
  Pie,
  PieChart,
  PolarAngleAxis,
  PolarGrid,
  Radar,
  RadarChart,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from 'recharts';
import { motion } from 'framer-motion';

function Badge({ children, variant = 'good' }) {
  const cls = variant === 'good' ? 'chip-good' : 'chip-missing';
  return <span className={cls}>{children}</span>;
}

export default function ResultDashboard({ result, onReset }) {
  const score = Number(result?.resume_score || 0);
  const matched = result?.matched_skills || [];
  const missing = result?.missing_skills || [];
  const learningPaths = result?.learning_paths || [];
  const recommendedCourses = result?.recommended_courses || [];
  const profileExperienceYears = Number(result?.profile_experience_years || 0);

  const pieData = [
    { name: 'Matched', value: matched.length || 1 },
    { name: 'Missing', value: missing.length || 1 },
  ];

  const barData = (result?.role_scores?.length ? result.role_scores : [{ role_name: result.predicted_role, score }])
    .map((item) => ({
      role: item.role_name,
      score: Number(item.score || 0),
    }))
    .sort((a, b) => b.score - a.score)
    .slice(0, 8);

  const radarData = [
    { dimension: 'Technical Depth', value: Math.min(100, score + 8) },
    { dimension: 'Core Match', value: score },
    { dimension: 'Tooling', value: Math.max(25, score - 10) },
    { dimension: 'Role Fit', value: Math.min(100, score + 5) },
    { dimension: 'Completeness', value: Math.max(20, score - 15) },
  ];

  return (
    <section className="min-h-screen px-4 py-8 md:py-12">
      <div className="mx-auto max-w-6xl grid gap-6">
        <div className="glass-card p-6 md:p-8">
          <p className="eyebrow">ANALYSIS COMPLETE</p>
          <div className="mt-2 flex flex-wrap items-end justify-between gap-4">
            <div>
              <h2 className="text-3xl md:text-4xl font-bold text-zinc-100">Resume Score</h2>
              <p className="text-zinc-400 mt-2">Best Matching Role: {result.predicted_role}</p>
              {!!profileExperienceYears && (
                <p className="text-zinc-500 mt-1 text-sm">Detected Experience: {profileExperienceYears}+ years</p>
              )}
            </div>
            <motion.div
              initial={{ scale: 0.8, opacity: 0 }}
              animate={{ scale: 1, opacity: 1 }}
              className="score-pill"
            >
              {score}%
            </motion.div>
          </div>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          <div className="glass-card p-6">
            <h3 className="panel-title">Matched Skills</h3>
            <div className="mt-4 flex flex-wrap gap-2">
              {matched.length ? matched.map((skill) => <Badge key={skill}>{skill}</Badge>) : <p className="text-zinc-500">No skills matched.</p>}
            </div>
          </div>

          <div className="glass-card p-6">
            <h3 className="panel-title">Missing Skills</h3>
            <div className="mt-4 flex flex-wrap gap-2">
              {missing.length
                ? missing.map((skill) => (
                    <Badge key={skill} variant="missing">
                      {skill}
                    </Badge>
                  ))
                : <p className="text-zinc-500">No critical missing skills.</p>}
            </div>
          </div>
        </div>

        <div className="glass-card p-6">
          <h3 className="panel-title">Suggestions</h3>
          <ul className="mt-4 grid gap-2 text-zinc-300">
            {(result.suggestions?.length ? result.suggestions : ['Add cloud deployment and production-focused project examples.']).map(
              (item) => (
                <li key={item} className="suggestion-item">
                  {item}
                </li>
              )
            )}
          </ul>
        </div>

        {!!learningPaths.length && (
          <div className="glass-card p-6">
            <h3 className="panel-title">Recommended Learning Path</h3>
            <ul className="mt-4 grid gap-2 text-zinc-300">
              {learningPaths.map((item) => (
                <li key={item} className="suggestion-item">
                  {item}
                </li>
              ))}
            </ul>
          </div>
        )}

        {!!recommendedCourses.length && (
          <div className="glass-card p-6">
            <h3 className="panel-title">Recommended Courses</h3>
            <ul className="mt-4 grid gap-2 text-zinc-300">
              {recommendedCourses.map((item) => (
                <li key={item} className="suggestion-item">
                  {item}
                </li>
              ))}
            </ul>
          </div>
        )}

        <div className="grid grid-cols-1 xl:grid-cols-3 gap-6">
          <div className="glass-card p-6 h-[320px]">
            <h3 className="panel-title">Skill Match Pie</h3>
            <ResponsiveContainer width="100%" height="90%">
              <PieChart>
                <Pie data={pieData} dataKey="value" nameKey="name" outerRadius={92} innerRadius={48}>
                  <Cell fill="#16f2ff" />
                  <Cell fill="#ff5370" />
                </Pie>
                <Tooltip />
              </PieChart>
            </ResponsiveContainer>
          </div>

          <div className="glass-card p-6 h-[320px]">
            <h3 className="panel-title">Role Compatibility</h3>
            <ResponsiveContainer width="100%" height="90%">
              <BarChart data={barData} layout="vertical" margin={{ top: 8, right: 10, left: 28, bottom: 6 }}>
                <XAxis type="number" domain={[0, 100]} stroke="#a3a3a3" />
                <YAxis type="category" width={130} dataKey="role" stroke="#a3a3a3" tick={{ fontSize: 11 }} />
                <Tooltip />
                <Bar dataKey="score" fill="#7f5cff" radius={[0, 8, 8, 0]} />
              </BarChart>
            </ResponsiveContainer>
          </div>

          <div className="glass-card p-6 h-[320px]">
            <h3 className="panel-title">Strength Radar</h3>
            <ResponsiveContainer width="100%" height="90%">
              <RadarChart outerRadius={95} data={radarData}>
                <PolarGrid stroke="#3f3f46" />
                <PolarAngleAxis dataKey="dimension" tick={{ fill: '#d4d4d8', fontSize: 11 }} />
                <Radar dataKey="value" stroke="#16f2ff" fill="#16f2ff" fillOpacity={0.38} />
              </RadarChart>
            </ResponsiveContainer>
          </div>
        </div>

        <div>
          <button type="button" onClick={onReset} className="analyze-btn">
            Analyze Another Resume
          </button>
        </div>
      </div>
    </section>
  );
}
