function resolveApiUrl() {
  const hostname = window.location.hostname;
  const isLocalhost =
    hostname === 'localhost' ||
    hostname === '127.0.0.1' ||
    hostname === '0.0.0.0';

  if (isLocalhost) {
    return 'http://localhost:8081';
  }

  const configuredUrl = process.env.REACT_APP_API_URL?.trim();
  if (configuredUrl) {
    return configuredUrl;
  }

  throw new Error(
    'REACT_APP_API_URL is required for non-local frontend builds.'
  );
}

const API_URL = resolveApiUrl();

export const API_ENDPOINTS = {
  RESUME_PARSE: `${API_URL}/api/resumes/parse`,
  RESUME_EXPORT: `${API_URL}/api/resumes/export`,
  DEBUG_RESUME_LAYOUT: `${API_URL}/api/debug/resumes/layout`,
  DEBUG_RESUME_LINES: `${API_URL}/api/debug/resumes/lines`,
  DEBUG_RESUME_SECTIONS: `${API_URL}/api/debug/resumes/sections`,
};

export default API_URL;
