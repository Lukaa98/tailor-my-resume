const API_URL = process.env.REACT_APP_API_URL || 'http://localhost:8081';

export const API_ENDPOINTS = {
  RESUME_PARSE: `${API_URL}/api/resumes/parse`,
  RESUME_EXPORT: `${API_URL}/api/resumes/export`,
  DEBUG_RESUME_LAYOUT: `${API_URL}/api/debug/resumes/layout`,
  DEBUG_RESUME_LINES: `${API_URL}/api/debug/resumes/lines`,
  DEBUG_RESUME_SECTIONS: `${API_URL}/api/debug/resumes/sections`,
};

export default API_URL;
