import { useMemo, useState } from 'react';
import { AnimatePresence } from 'framer-motion';
import AnimatedBackground from './components/AnimatedBackground';
import UploadScreen from './screens/UploadScreen';
import ProcessingScreen from './screens/ProcessingScreen';
import ResultDashboard from './screens/ResultDashboard';
import { analyzeResume } from './lib/api';

const phases = {
  upload: 'upload',
  processing: 'processing',
  results: 'results',
};

function wait(ms) {
  return new Promise((resolve) => setTimeout(resolve, ms));
}

export default function App() {
  const [phase, setPhase] = useState(phases.upload);
  const [file, setFile] = useState(null);
  const [roleName, setRoleName] = useState('Backend Developer');
  const [analysisMode, setAnalysisMode] = useState('validate_role');
  const [result, setResult] = useState(null);
  const [progress, setProgress] = useState(0);
  const [loading, setLoading] = useState(false);
  const [errorMessage, setErrorMessage] = useState('');

  const isProcessing = useMemo(() => phase === phases.processing, [phase]);

  const runAnalyze = async () => {
    if (!file) {
      setErrorMessage('Please upload a resume first.');
      return;
    }

    setErrorMessage('');
    setLoading(true);
    setProgress(0);
    setPhase(phases.processing);

    const progressMilestones = [16, 32, 49, 67, 82, 96];
    const runner = (async () => {
      for (const point of progressMilestones) {
        await wait(380);
        setProgress(point);
      }
    })();

    try {
      const analysis = await analyzeResume({ file, roleName, analysisMode });
      await runner;
      setProgress(100);
      await wait(220);
      setResult(analysis);
      setPhase(phases.results);
    } catch (error) {
      setErrorMessage(error.message || 'Unable to analyze resume right now.');
      setPhase(phases.upload);
    } finally {
      setLoading(false);
    }
  };

  const resetFlow = () => {
    setFile(null);
    setResult(null);
    setProgress(0);
    setPhase(phases.upload);
    setErrorMessage('');
  };

  return (
    <main className="app-shell">
      <AnimatedBackground />

      <AnimatePresence mode="wait">
        {phase === phases.upload && (
          <UploadScreen
            key="upload"
            file={file}
            setFile={setFile}
            roleName={roleName}
            setRoleName={setRoleName}
            analysisMode={analysisMode}
            setAnalysisMode={setAnalysisMode}
            onAnalyze={runAnalyze}
            loading={loading}
          />
        )}

        {isProcessing && <ProcessingScreen key="processing" progress={progress} />}

        {phase === phases.results && <ResultDashboard key="results" result={result} onReset={resetFlow} />}
      </AnimatePresence>

      {errorMessage && <div className="error-toast">{errorMessage}</div>}
    </main>
  );
}
