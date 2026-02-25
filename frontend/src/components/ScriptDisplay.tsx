import React, { useState } from 'react';
import {
  Check,
  Copy,
  AlertCircle,
  Download,
  ChevronDown,
  ChevronUp,
} from 'lucide-react';
import './ScriptDisplay.css';

interface ScriptDisplayProps {
  script?: string;
  variations?: string[];
  captions?: string[];
}

export const ScriptDisplay: React.FC<ScriptDisplayProps> = ({
  script,
  variations = [],
  captions = [],
}) => {
  const [copied, setCopied] = useState(false);
  const [variationsOpen, setVariationsOpen] = useState(false);

  const handleCopy = async () => {
    if (!script) return;
    await navigator.clipboard.writeText(script);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  const isArabic = (text: string) => /[\u0600-\u06FF]/.test(text);
  const isRtl = script ? isArabic(script) : false;

  const handleDownload = () => {
    if (!script) return;
    let content = '# Main Script\n\n' + script;
    if (variations.length > 0) {
      content += '\n\n---\n\n# Variations\n';
      variations.forEach((v, i) => {
        content += `\n## Variation ${i + 1}\n\n${v}\n`;
      });
    }
    if (captions.length > 0) {
      content += '\n\n---\n\n# Captions\n\n';
      captions.forEach((c, i) => {
        content += `${i + 1}. ${c}\n`;
      });
    }
    const blob = new Blob([content], { type: 'text/markdown' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = 'viral-script.md';
    a.click();
    URL.revokeObjectURL(url);
  };

  return (
    <div className={`script-display ${isRtl ? 'rtl' : ''}`} dir={isRtl ? 'rtl' : 'ltr'}>
      {/* Main Script */}
      <div className="script-section">
        <div className="script-section-header">
          <h3>Main Script</h3>
          <div className="script-actions">
            {script && (
              <>
                <button onClick={handleCopy} className="script-action-btn" title="Copy">
                  {copied ? <Check size={14} /> : <Copy size={14} />}
                  {copied ? 'Copied' : 'Copy'}
                </button>
                <button onClick={handleDownload} className="script-action-btn" title="Download">
                  <Download size={14} />
                  Download
                </button>
              </>
            )}
          </div>
        </div>
        {script ? (
          <div className="script-content">
            <pre>{script}</pre>
          </div>
        ) : (
          <div className="script-empty">
            <AlertCircle size={18} />
            <p>Generate content to see the script</p>
          </div>
        )}
      </div>

      {/* Variations - collapsible */}
      {variations.length > 0 && (
        <div className="script-section">
          <button
            className="section-toggle"
            onClick={() => setVariationsOpen((o) => !o)}
          >
            <h3>Script Variations ({variations.length})</h3>
            <span className="toggle-hint">A/B Testing</span>
            {variationsOpen ? <ChevronUp size={16} /> : <ChevronDown size={16} />}
          </button>
          {variationsOpen && (
            <div className="variations-list">
              {variations.map((variant, idx) => (
                <div key={idx} className="variant-item">
                  <div className="variant-header">
                    <span>Variation {idx + 1}</span>
                  </div>
                  <pre>{variant || '(empty variation)'}</pre>
                </div>
              ))}
            </div>
          )}
        </div>
      )}

      {/* Captions */}
      {captions.length > 0 && (
        <div className="script-section">
          <h3>Video Captions</h3>
          <p className="captions-info">
            Hard-coded, yellow bold, center screen — critical for silent-watch retention
          </p>
          <div className="captions-list">
            {captions.map((caption, idx) => (
              <div key={idx} className="caption-item">
                <span className="caption-number">{idx + 1}</span>
                <p>{caption || '(empty caption)'}</p>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
};
