const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://127.0.0.1:8000';

export async function analyzeResume({ file, roleName, analysisMode }) {
  const formData = new FormData();
  formData.append('file', file);
  formData.append('analysis_mode', analysisMode || 'validate_role');
  if (roleName && (analysisMode || 'validate_role') === 'validate_role') {
    formData.append('role_name', roleName);
  }

  let response = await fetch(`${API_BASE_URL}/analyze-resume`, {
    method: 'POST',
    body: formData,
  });

  if (!response.ok && roleName) {
    response = await fetch(`${API_BASE_URL}/api/resumes/analyze`, {
      method: 'POST',
      body: formData,
    });
  }

  if (!response.ok) {
    const errorBody = await response.json().catch(() => ({}));
    const detail = errorBody?.detail;
    const message = typeof detail === 'string'
      ? detail
      : detail?.message || 'Failed to analyze resume.';
    throw new Error(message);
  }

  const payload = await response.json();

  return {
    analysis_mode: payload.analysis_mode || analysisMode || 'validate_role',
    resume_score: payload.resume_score ?? 0,
    predicted_role: payload.predicted_role || payload.role_name || roleName || 'Unknown',
    matched_skills: payload.matched_skills || [],
    missing_skills: payload.missing_skills || [],
    suggestions: Array.isArray(payload.suggestions)
      ? payload.suggestions
      : payload.suggestion
        ? [payload.suggestion]
        : [],
    learning_paths: payload.learning_paths || [],
    recommended_courses: payload.recommended_courses || [],
    top_role_insights: payload.top_role_insights || [],
    role_scores: payload.role_scores || [],
    profile_experience_years: payload.profile_experience_years || 0,
  };
}

export { API_BASE_URL };
