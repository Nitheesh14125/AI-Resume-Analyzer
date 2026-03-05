import { motion } from 'framer-motion';
import FileDropzone from '../components/FileDropzone';

const roles = [
  'Fresher',
  'Intern',
  'Junior Software Engineer',
  'Software Engineer',
  'Backend Developer',
  'Frontend Developer',
  'Full Stack Developer',
  'Data Analyst',
  'Data Scientist',
  'Machine Learning Engineer',
  'AI Engineer',
  'Cyber Security Analyst',
  'SOC Analyst',
  'Cloud Engineer',
  'DevOps Engineer',
  'Android Developer',
  'iOS Developer',
  'System Administrator',
  'Network Engineer',
  'Tech Lead',
  'Senior Software Engineer',
];

const analysisModes = [
  { value: 'validate_role', label: 'Validate Resume for a Role' },
  { value: 'discover_roles', label: 'Find Best Roles for My Resume' },
];

export default function UploadScreen({
  file,
  setFile,
  onAnalyze,
  roleName,
  setRoleName,
  analysisMode,
  setAnalysisMode,
  loading,
}) {
  return (
    <motion.section
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      exit={{ opacity: 0, y: -20 }}
      transition={{ duration: 0.5 }}
      className="min-h-screen flex items-center justify-center px-4"
    >
      <div className="w-full max-w-4xl text-center">
        <p className="eyebrow">NEXT-GEN RESUME INTELLIGENCE</p>
        <h1 className="hero-title">AI Resume Analyzer</h1>
        <p className="hero-subtitle">Discover how well your resume matches modern tech roles.</p>

        <div className="mt-10 flex flex-col items-center gap-6">
          <FileDropzone file={file} setFile={setFile} />

          <div className="w-full max-w-3xl text-left">
            <label htmlFor="analysis-mode" className="text-zinc-300 text-sm block mb-2">
              Analysis type
            </label>
            <select
              id="analysis-mode"
              className="role-select"
              value={analysisMode}
              onChange={(event) => setAnalysisMode(event.target.value)}
            >
              {analysisModes.map((mode) => (
                <option key={mode.value} value={mode.value}>
                  {mode.label}
                </option>
              ))}
            </select>
          </div>

          {analysisMode === 'validate_role' && (
            <div className="w-full max-w-3xl text-left">
              <label htmlFor="role" className="text-zinc-300 text-sm block mb-2">
                Target role
              </label>
            <select
              id="role"
              className="role-select"
              value={roleName}
              onChange={(event) => setRoleName(event.target.value)}
            >
              {roles.map((role) => (
                <option key={role} value={role}>
                  {role}
                </option>
                ))}
              </select>
            </div>
          )}

          <button type="button" className="analyze-btn" disabled={!file || loading} onClick={onAnalyze}>
            {loading ? 'Analyzing...' : 'Analyze My Resume'}
          </button>
        </div>
      </div>
    </motion.section>
  );
}
