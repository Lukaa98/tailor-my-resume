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
  const [activeEntryKey, setActiveEntryKey] = useState(null);
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
    setActiveEntryKey(null);

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

  const getEntryIds = (entry) =>
    lineMap.slice(entry.start_line, entry.end_line + 1).flat();

  const previewSection = (index) => {
    const section = sections[index];
    if (!section) return;
    setHighlightedIds(getSectionIds(section));
  };

  const clearPreview = () => {
    if (activeEntryKey) {
      const [sectionIndex, entryIndex] = activeEntryKey.split(':').map(Number);
      const activeEntry = sections[sectionIndex]?.entries?.[entryIndex];
      setHighlightedIds(activeEntry ? getEntryIds(activeEntry) : []);
      return;
    }

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
      setActiveEntryKey(null);
      setHighlightedIds([]);
      return;
    }

    setActiveSectionIndex(index);
    setActiveEntryKey(null);
    previewSection(index);
  };

  const previewEntry = (sectionIndex, entryIndex) => {
    const entry = sections[sectionIndex]?.entries?.[entryIndex];
    if (!entry) return;
    setHighlightedIds(getEntryIds(entry));
  };

  const toggleEntrySelection = (sectionIndex, entryIndex) => {
    const nextKey = `${sectionIndex}:${entryIndex}`;
    if (activeEntryKey === nextKey) {
      setActiveEntryKey(null);
      if (activeSectionIndex !== null) {
        previewSection(activeSectionIndex);
      } else {
        setHighlightedIds([]);
      }
      return;
    }

    setActiveSectionIndex(sectionIndex);
    setActiveEntryKey(nextKey);
    previewEntry(sectionIndex, entryIndex);
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
                {!!section.entries?.length && (
                  <Stack spacing={1} sx={{ mt: 1.5 }}>
                    {section.entries.map((entry, entryIndex) => (
                      <Box
                        key={`${section.index}-${entryIndex}`}
                        sx={{
                          p: 1,
                          borderRadius: 1,
                          cursor: 'pointer',
                          bgcolor:
                            activeEntryKey === `${section.index}:${entryIndex}`
                              ? 'rgba(25, 118, 210, 0.12)'
                              : 'rgba(25, 118, 210, 0.04)',
                        }}
                        onMouseEnter={() => previewEntry(section.index, entryIndex)}
                        onMouseLeave={clearPreview}
                        onClick={(event) => {
                          event.stopPropagation();
                          toggleEntrySelection(section.index, entryIndex);
                        }}
                      >
                        <Typography variant="body2" sx={{ fontWeight: 600 }}>
                          {entry.header}
                        </Typography>
                        {entry.title && (
                          <Typography
                            variant="caption"
                            color="text.secondary"
                            sx={{ display: 'block', mb: entry.bullets?.length ? 0.75 : 0 }}
                          >
                            {entry.title}
                          </Typography>
                        )}
                        {!!entry.bullets?.length && (
                          <Typography variant="caption" color="text.secondary">
                            {entry.bullets.length} bullet
                            {entry.bullets.length === 1 ? '' : 's'}
                          </Typography>
                        )}
                      </Box>
                    ))}
                  </Stack>
                )}
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
