import { useMemo } from 'react';
import { useDropzone } from 'react-dropzone';
import { motion } from 'framer-motion';

const acceptedTypes = {
  'application/pdf': ['.pdf'],
  'application/vnd.openxmlformats-officedocument.wordprocessingml.document': ['.docx'],
};

export default function FileDropzone({ file, setFile }) {
  const { getRootProps, getInputProps, isDragActive, fileRejections } = useDropzone({
    accept: acceptedTypes,
    maxFiles: 1,
    onDrop: (acceptedFiles) => {
      if (acceptedFiles.length > 0) {
        setFile(acceptedFiles[0]);
      }
    },
  });

  const errorMessage = useMemo(() => {
    if (!fileRejections.length) {
      return '';
    }
    return 'Only PDF and DOCX files are supported.';
  }, [fileRejections]);

  return (
    <div className="w-full max-w-3xl">
      <motion.div
        {...getRootProps()}
        whileHover={{ scale: 1.01 }}
        className={`dropzone ${isDragActive ? 'dropzone-active' : ''}`}
      >
        <input {...getInputProps()} />
        <motion.div
          animate={{ y: [0, -6, 0], rotate: [0, 2, -2, 0] }}
          transition={{ duration: 2.8, repeat: Infinity, ease: 'easeInOut' }}
          className="text-5xl"
        >
          {isDragActive ? '⚡' : '📄'}
        </motion.div>
        <p className="text-xl font-semibold text-zinc-100 mt-4">Drop your resume here</p>
        <p className="text-sm text-zinc-400 mt-2">or click to browse (PDF / DOCX)</p>
      </motion.div>

      {file && (
        <div className="mt-4 rounded-xl border border-cyan-400/30 bg-zinc-900/70 p-4">
          <p className="text-cyan-300 text-sm">Selected file</p>
          <p className="text-zinc-100 font-medium truncate">{file.name}</p>
        </div>
      )}

      {errorMessage && <p className="text-red-400 text-sm mt-3">{errorMessage}</p>}
    </div>
  );
}
