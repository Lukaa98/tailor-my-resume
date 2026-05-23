import { API_ENDPOINTS } from '../config/api';

export const parseResume = async (file) => {
  const formData = new FormData();
  formData.append('file', file);

  const res = await fetch(API_ENDPOINTS.RESUME_PARSE, {
    method: 'POST',
    body: formData,
  });

  if (!res.ok) throw new Error('Resume parsing failed');
  return res.json();
};

export const exportResumePdf = async (layout) => {
  const res = await fetch(API_ENDPOINTS.RESUME_EXPORT, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(layout),
  });

  if (!res.ok) throw new Error('Resume export failed');

  const blob = await res.blob();
  const url = URL.createObjectURL(blob);

  const anchor = document.createElement('a');
  anchor.href = url;
  anchor.download = 'resume.pdf';
  anchor.click();

  URL.revokeObjectURL(url);
};
