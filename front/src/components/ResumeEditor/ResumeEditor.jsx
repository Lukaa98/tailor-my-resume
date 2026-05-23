import { useState } from 'react';
import {
  Box,
  Button,
  Chip,
  Paper,
  Stack,
  Typography,
} from '@mui/material';
import LosslessResumeViewer from './LosslessResumeViewer';
import {
  parseResume,
  exportResumePdf,
} from '../../services/resumeService';

export default function ResumeEditor() {
  const [layout, setLayout] = useState(null);
  const [semantic, setSemantic] = useState(null);
  const [lineMap, setLineMap] = useState([]);
  const [highlightedIds, setHighlightedIds] = useState([]);
  const [activeSectionIndex, setActiveSectionIndex] = useState(null);
  const [error, setError] = useState('');

  const sections = semantic?.sections || [];
  const parserName = semantic?.parser || '';

  const sectionSummaries = sections.map((section, index) => ({
    ...section,
    index,
    label: section.header || formatSectionType(section.type),
  }));

  const handleUpload = async (file) => {
    if (!file) return;

    setError('');
    setLayout(null);
    setSemantic(null);
    setLineMap([]);
    setHighlightedIds([]);
    setActiveSectionIndex(null);

    console.log('Uploading resume...');

    try {
      const parsedResume = await parseResume(file);
      console.log('Resume parsed');
      setLayout(parsedResume.layout);
      setLineMap(parsedResume.lines?.line_map || []);
      setSemantic(parsedResume.sections || null);
    } catch (err) {
      console.error(err);
      setLayout(null);
      setError(err.message || 'Resume parsing failed');
    }
  };

  const getSectionIds = (section) =>
    lineMap.slice(section.start_line, section.end_line + 1).flat();

  const previewSection = (index) => {
    const section = sections[index];
    if (!section) return;
    setHighlightedIds(getSectionIds(section));
  };

  const clearPreview = () => {
    if (activeSectionIndex === null) {
      setHighlightedIds([]);
      return;
    }

    const activeSection = sections[activeSectionIndex];
    setHighlightedIds(activeSection ? getSectionIds(activeSection) : []);
  };

  const toggleSectionSelection = (index) => {
    if (activeSectionIndex === index) {
      setActiveSectionIndex(null);
      setHighlightedIds([]);
      return;
    }

    setActiveSectionIndex(index);
    previewSection(index);
  };

  return (
    <Box sx={{ p: 3 }}>
      <Stack direction="row" spacing={2} mb={2}>
        <Button variant="contained" component="label">
          Upload Resume
          <input
            hidden
            type="file"
            accept="application/pdf"
            onChange={(e) => handleUpload(e.target.files[0])}
          />
        </Button>

        <Button
          variant="contained"
          color="success"
          disabled={!layout}
          onClick={() => exportResumePdf(layout)}
        >
          Export PDF
        </Button>

        {parserName && (
          <Chip
            label={`Parser: ${parserName}`}
            color="primary"
            variant="outlined"
          />
        )}
      </Stack>

      {error && (
        <Box sx={{ color: 'error.main', mb: 2 }}>
          {error}
        </Box>
      )}

      <Stack
        direction={{ xs: 'column', lg: 'row' }}
        spacing={3}
        alignItems="flex-start"
      >
        <Paper
          elevation={2}
          sx={{
            width: { xs: '100%', lg: 340 },
            p: 2,
            position: { lg: 'sticky' },
            top: { lg: 24 },
            maxHeight: { lg: 'calc(100vh - 48px)' },
            overflowY: 'auto',
          }}
        >
          <Typography variant="h6" gutterBottom>
            Parsed Sections
          </Typography>

          {!sectionSummaries.length && (
            <Typography variant="body2" color="text.secondary">
              Upload a resume to inspect detected sections.
            </Typography>
          )}

          <Stack spacing={1.5}>
            {sectionSummaries.map((section) => (
              <Paper
                key={`${section.type}-${section.index}`}
                variant="outlined"
                sx={{
                  p: 1.5,
                  cursor: 'pointer',
                  borderColor:
                    activeSectionIndex === section.index
                      ? 'primary.main'
                      : 'divider',
                  bgcolor:
                    activeSectionIndex === section.index
                      ? 'rgba(25, 118, 210, 0.08)'
                      : 'background.paper',
                }}
                onMouseEnter={() => previewSection(section.index)}
                onMouseLeave={clearPreview}
                onClick={() => toggleSectionSelection(section.index)}
              >
                <Typography variant="subtitle2">
                  {section.label}
                </Typography>
                <Typography variant="caption" color="text.secondary">
                  {formatSectionType(section.type)} | lines {section.start_line}-
                  {section.end_line}
                </Typography>
              </Paper>
            ))}
          </Stack>
        </Paper>

        <Box sx={{ flex: 1, minWidth: 0 }}>
          {layout && (
            <LosslessResumeViewer
              layout={layout}
              highlightedIds={highlightedIds}
            />
          )}
        </Box>
      </Stack>
    </Box>
  );
}

function formatSectionType(type = '') {
  return type
    .split('_')
    .filter(Boolean)
    .map((word) => word[0].toUpperCase() + word.slice(1))
    .join(' ');
}
