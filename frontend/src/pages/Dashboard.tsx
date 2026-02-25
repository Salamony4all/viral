import React, { useState, useEffect, useRef, useCallback } from 'react';
import {
  Sparkles,
  Play,
  Loader,
  Zap,
  CheckCircle2,
  RotateCcw,
  Trash2,
  Plus,
  Film,
  PenLine,
  Home,
  Settings,
  Send,
  Link2,
  ToggleLeft,
  ToggleRight,
} from 'lucide-react';
import { ChatBox } from '@/components/ChatBox';
import { VideoPreview } from '@/components/VideoPreview';
import { ScriptDisplay } from '@/components/ScriptDisplay';
import { MonetizationBrief } from '@/components/MonetizationBrief';
import { ToastContainer, useToast } from '@/components/Toast';
import { LogConsole } from '@/components/LogConsole';
import { HistoryList } from '@/components/HistoryList';
import { agentService } from '@/services/agentService';
import type { GenerationResult, ScriptColumn } from '@/types';
import './Dashboard.css';

const PHASE_LABELS: Record<string, string> = {
  initializing: 'Initializing pipeline...',
  infrastructure_check: 'Checking infrastructure...',
  trend_hunting: 'Agent Alpha: Hunting trends on TikTok & YouTube...',
  script_generation: 'Agent Beta: Writing viral script from trends...',
  script_ready: 'Script ready — review & edit below',
  media_generation: 'Agent Gamma: Downloading footage & generating narration...',
  monetization: 'Agent Delta: Building monetization strategy...',
  done: 'Pipeline complete!',
  error: 'Pipeline encountered an error',
};

const TOPIC_SUGGESTIONS = [
  'productivity hack for students',
  'morning routine that changed my life',
  'budget travel tips 2026',
  'AI tools nobody talks about',
  'fitness transformation in 30 days',
  '5-minute cooking hacks',
  'money-saving tips for Gen Z',
  'side hustle ideas from home',
];

const TOPIC_SUGGESTIONS_AR = [
  'نصائح للدراسة الفعالة',
  'روتين صباحي غير حياتي',
  'حيل طبخ سريعة بـ5 دقائق',
  'أدوات ذكاء اصطناعي ما حد يعرفها',
  'نصائح توفير المال للشباب',
  'تحول لياقة بدنية في 30 يوم',
];

const ARABIC_RE = /[\u0600-\u06FF\u0750-\u077F\u08A0-\u08FF\uFB50-\uFDFF\uFE70-\uFEFF]/;
const isArabic = (text: string) => {
  const arabicChars = (text.match(new RegExp(ARABIC_RE.source, 'g')) || []).length;
  return arabicChars > text.length * 0.3;
};

export const Dashboard: React.FC = () => {
  const [topic, setTopic] = useState('');
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState<GenerationResult | null>(null);
  const [activeTab, setActiveTab] = useState<
    'video' | 'script' | 'monetization' | 'chat' | 'history'
  >('video');
  const [progress, setProgress] = useState(0);
  const [phase, setPhase] = useState('');
  const [selectedAgent, setSelectedAgent] = useState('Agent Beta');

  // Two-phase state
  const [genId, setGenId] = useState<string | null>(null);
  const [editableScript, setEditableScript] = useState<ScriptColumn[]>([]);
  const [scriptSource, setScriptSource] = useState<string>('');
  const [scriptReady, setScriptReady] = useState(false);
  const [phase2Loading, setPhase2Loading] = useState(false);
  const [language, setLanguage] = useState<string>('en');
  const [showHistory, setShowHistory] = useState(false);

  // Social media connections
  const [socialConnections, setSocialConnections] = useState<Record<string, boolean>>({
    tiktok: false,
    instagram: false,
    youtube: false,
    twitter: false,
  });
  const [publishTarget, setPublishTarget] = useState<string>('');

  const isRtl = language === 'ar';
  const dir = isRtl ? 'rtl' as const : 'ltr' as const;

  const { toasts, addToast, dismissToast } = useToast();
  const pollingRef = useRef<ReturnType<typeof setInterval> | null>(null);

  /* ---- Polling ---- */

  const stopPolling = useCallback(() => {
    if (pollingRef.current) {
      clearInterval(pollingRef.current);
      pollingRef.current = null;
    }
  }, []);

  const startPolling = useCallback(
    (id: string) => {
      stopPolling();
      pollingRef.current = setInterval(async () => {
        try {
          const status = await agentService.getGenerationStatus(id);
          setProgress(status.progress);
          setPhase(status.phase || '');

          if (status.status === 'script_ready' && status.script_data) {
            setEditableScript(status.script_data.script_columns || []);
            setScriptSource(status.script_data.script_source || '');
            if (status.language) setLanguage(status.language);
            setScriptReady(true);
            setLoading(false);
            stopPolling();
            addToast(
              'info',
              'Script Generated',
              'Review and edit the script below, then click "Generate Video".',
            );
          } else if (status.status === 'completed' && status.result) {
            setResult(status.result);
            setLoading(false);
            setPhase2Loading(false);
            setScriptReady(false);
            setActiveTab('video');
            stopPolling();
            addToast(
              'success',
              'Campaign Ready!',
              'Video with narration, script, and monetization brief generated.',
            );
          } else if (status.status === 'failed') {
            addToast('error', 'Generation Failed', status.error || 'Unknown error');
            setLoading(false);
            setPhase2Loading(false);
            stopPolling();
          }
        } catch {
          /* network blip */
        }
      }, 2000);
    },
    [stopPolling, addToast],
  );

  useEffect(() => () => stopPolling(), [stopPolling]);

  /* removed variation fetching — single script only */

  /* ---- Handlers ---- */

  const handleGenerateCampaign = async () => {
    if (!topic.trim()) return;

    setLoading(true);
    setResult(null);
    setEditableScript([]);
    setScriptReady(false);
    setProgress(0);
    setPhase('initializing');
    addToast(
      'info',
      isRtl ? 'المرحلة 1 بدأت' : 'Phase 1 Started',
      isRtl ? `جاري البحث وكتابة السكربت لـ "${topic}"...` : `Hunting trends & writing script for "${topic}"...`,
    );

    try {
      const response = await agentService.generateCampaign(topic);
      setGenId(response.generation_id);
      startPolling(response.generation_id);
    } catch (err) {
      addToast(
        'error',
        'Failed to start',
        err instanceof Error ? err.message : 'Could not reach the backend.',
      );
      setLoading(false);
    }
  };

  const handleProceedWithScript = async () => {
    if (!genId || editableScript.length === 0) return;

    setPhase2Loading(true);
    setPhase('media_generation');
    setProgress(55);
    addToast('info', 'Phase 2 Started', 'Downloading footage, generating narration & monetization...');

    try {
      await agentService.proceedWithScript(genId, editableScript);
      startPolling(genId);
    } catch (err) {
      addToast(
        'error',
        'Failed to proceed',
        err instanceof Error ? err.message : 'Could not reach the backend.',
      );
      setPhase2Loading(false);
    }
  };

  const handleBrainstorm = async (message: string): Promise<string> => {
    const response = await agentService.brainstormWithAgent(selectedAgent, message);
    return response.content;
  };

  const handleNewCampaign = () => {
    setResult(null);
    setTopic('');
    setProgress(0);
    setPhase('');
    setGenId(null);
    setEditableScript([]);
    setScriptSource('');
    setScriptReady(false);
    setPhase2Loading(false);
    setLanguage('en');
    setActiveTab('video');
    setShowHistory(false);
  };

  /* ---- Social Media OAuth ---- */

  const API_BASE = (import.meta as any).env?.VITE_API_URL || 'http://localhost:8000';

  // Fetch initial connection status from backend
  useEffect(() => {
    agentService.getSocialStatus().then((status) => {
      setSocialConnections(
        Object.fromEntries(
          Object.entries(status).map(([p, v]: [string, any]) => [p, v.connected])
        )
      );
    }).catch(() => { });
  }, []);

  // Listen for OAuth popup callbacks
  useEffect(() => {
    const handler = (event: MessageEvent) => {
      if (event.origin !== API_BASE.replace(/\/$/, '')) return;
      const { type, platform } = event.data || {};
      if (type === 'oauth_success' && platform) {
        setSocialConnections(prev => ({ ...prev, [platform]: true }));
        addToast('success', `${platform} Connected`, `Your ${platform} account is now linked.`);
      } else if (type === 'oauth_error' && platform) {
        addToast('error', `${platform} Failed`, event.data.error || 'OAuth failed');
      }
    };
    window.addEventListener('message', handler);
    return () => window.removeEventListener('message', handler);
  }, [API_BASE, addToast]);

  const connectPlatform = (platform: string) => {
    const url = `${API_BASE}/social/connect/${platform}`;
    const popup = window.open(url, `${platform}_oauth`, 'width=600,height=700,scrollbars=yes');
    if (!popup) {
      addToast('error', 'Popup blocked', 'Please allow popups for this site to connect accounts.');
    }
  };

  const disconnectPlatform = async (platform: string) => {
    try {
      await agentService.disconnectSocial(platform);
      setSocialConnections(prev => ({ ...prev, [platform]: false }));
      if (publishTarget === platform) setPublishTarget('');
      addToast('info', `${platform} Disconnected`, `Account unlinked.`);
    } catch {
      addToast('error', 'Error', 'Could not disconnect.');
    }
  };

  const connectedPlatforms = Object.entries(socialConnections)
    .filter(([, connected]) => connected)
    .map(([platform]) => platform);


  /* ---- Script editor helpers ---- */

  const updateScene = (idx: number, field: keyof ScriptColumn, value: string) => {
    setEditableScript((prev) =>
      prev.map((s, i) => (i === idx ? { ...s, [field]: value } : s)),
    );
  };

  const removeScene = (idx: number) => {
    setEditableScript((prev) => prev.filter((_, i) => i !== idx));
  };

  const addScene = () => {
    const last = editableScript[editableScript.length - 1];
    const lastEnd = last?.timecode?.split('-')[1]?.replace('s', '').trim() || '15';
    const newStart = parseInt(lastEnd) || 15;
    setEditableScript((prev) => [
      ...prev,
      {
        timecode: `${newStart}-${newStart + 3}s`,
        visual_cue: isRtl ? 'مشهد جديد' : 'New scene visual',
        audio: isRtl ? '"أدخل النص المنطوق هنا"' : '"Your narration text here"',
      },
    ]);
  };

  /* ---- Render ---- */

  return (
    <div className="dashboard">
      <ToastContainer toasts={toasts} onDismiss={dismissToast} />

      {/* Header */}
      <header className="dashboard-header">
        <div className="header-content">
          <h1 onClick={handleNewCampaign} style={{ cursor: 'pointer' }}>
            <Sparkles size={30} />
            Viral Engine
          </h1>
          <p className="header-subtitle">
            AI-Powered TikTok Content Creation &amp; Monetization
          </p>
        </div>
        <div className="header-badges">
          {(result || scriptReady || loading) && (
            <button className="home-btn" onClick={handleNewCampaign} title="Back to Home">
              <Home size={18} />
              Home
            </button>
          )}
          <button
            className={`gear-btn ${showHistory ? 'active' : ''}`}
            onClick={() => setShowHistory(!showHistory)}
            title="Previous Campaigns"
          >
            <Settings size={18} />
          </button>
        </div>
      </header>

      <div className="dashboard-container">
        {/* Input Section */}
        <section className="input-section">
          <div className="input-card">
            <div className="input-card-header">
              <Zap size={20} />
              <h2>Start Your Campaign</h2>
            </div>
            <div className="input-group">
              <input
                type="text"
                value={topic}
                onChange={(e) => {
                  setTopic(e.target.value);
                  setLanguage(isArabic(e.target.value) ? 'ar' : 'en');
                }}
                onKeyDown={(e) => e.key === 'Enter' && handleGenerateCampaign()}
                placeholder={isRtl
                  ? "أدخل موضوع (مثال: نصائح للدراسة الفعالة)"
                  : "Enter a topic (e.g., 'productivity hack for students')"
                }
                dir={dir}
                disabled={loading || scriptReady || phase2Loading}
                className="topic-input"
              />
              <button
                onClick={handleGenerateCampaign}
                disabled={!topic.trim() || loading || scriptReady || phase2Loading}
                className="generate-btn"
              >
                {loading ? (
                  <>
                    <Loader className="spinner" size={18} />
                    Generating...
                  </>
                ) : (
                  <>
                    <Play size={18} />
                    Generate
                  </>
                )}
              </button>
            </div>

            {!loading && !result && !scriptReady && (
              <div className="topic-suggestions" dir={dir}>
                <span className="suggestions-label">{isRtl ? 'جرب:' : 'Try:'}</span>
                {(isRtl ? TOPIC_SUGGESTIONS_AR : TOPIC_SUGGESTIONS).slice(0, 4).map((s) => (
                  <button key={s} className="suggestion-chip" onClick={() => {
                    setTopic(s);
                    setLanguage(isArabic(s) ? 'ar' : 'en');
                  }}>
                    {s}
                  </button>
                ))}
              </div>
            )}
          </div>
        </section>

        {/* Progress & Log Console Integration */}
        {(loading || phase2Loading || scriptReady) && (
          <section className="engine-status-section">
            <div className={`status-grid ${scriptReady && !phase2Loading ? 'compact' : ''}`}>
              {(loading || phase2Loading) && (
                <div className="progress-card premium">
                  <div className="progress-header">
                    <div className="phase-indicator">
                      <Loader className="spinner" size={20} />
                      <span className="progress-phase">
                        {PHASE_LABELS[phase] || phase || 'Working...'}
                      </span>
                    </div>
                    <span className="progress-pct">{progress}%</span>
                  </div>
                  <div className="progress-bar-track">
                    <div
                      className="progress-bar-fill animated"
                      style={{ width: `${progress}%` }}
                    />
                  </div>
                  <div className="progress-agents">
                    {[
                      { label: 'Alpha', emoji: '🔍', threshold: 10 },
                      { label: 'Beta', emoji: '✍️', threshold: 35 },
                      { label: 'Gamma', emoji: '🎨', threshold: 60 },
                      { label: 'Delta', emoji: '💹', threshold: 85 },
                    ].map((a) => (
                      <div key={a.label} className={`agent-pill ${progress >= a.threshold ? 'active' : ''}`}>
                        <span className="agent-emoji">{a.emoji}</span>
                        <span className="agent-name">{a.label}</span>
                      </div>
                    ))}
                  </div>
                </div>
              )}
              <LogConsole />
            </div>
          </section>
        )}

        {/* ================================================================ */}
        {/*  SCRIPT EDITOR — shown after Phase 1, before Phase 2            */}
        {/* ================================================================ */}
        {scriptReady && !result && !phase2Loading && (
          <section className="script-editor-section">
            <div className="script-editor-card" dir={dir}>
              <div className="script-editor-header">
                <div className="script-editor-title">
                  <PenLine size={20} />
                  <h2>{isRtl ? 'راجع وعدّل السكربت' : 'Review & Edit Your Script'}</h2>
                  {scriptSource && (
                    <span className="script-source-badge" title={scriptSource === 'baidu' ? 'Generated by Baidu AI (Ernie)' : scriptSource === 'ollama' ? 'Generated by Ollama' : 'Template fallback'}>
                      {scriptSource === 'baidu' ? '🤖 Baidu AI' : scriptSource === 'ollama' ? '🦙 Ollama' : '📋 Template'}
                    </span>
                  )}
                </div>
                <p className="script-editor-sub">
                  {isRtl
                    ? 'الذكاء الاصطناعي كتب هالسكربت من البيانات الرائجة. عدّل النص والمشاهد، ثم ولّد الفيديو.'
                    : 'The AI generated this script from trending data. Edit the narration and visual cues, then generate the video.'}
                </p>
              </div>

              {/* Single script — no variation selector needed */}

              <div className="scene-list">
                {editableScript.map((scene, idx) => (
                  <div key={idx} className="scene-card">
                    <div className="scene-number">{idx + 1}</div>
                    <div className="scene-fields">
                      <div className="scene-field">
                        <label>{isRtl ? 'الوقت' : 'Timecode'}</label>
                        <input
                          value={scene.timecode}
                          onChange={(e) => updateScene(idx, 'timecode', e.target.value)}
                          dir="ltr"
                          title="Scene duration/timestamp"
                        />
                      </div>
                      <div className="scene-field">
                        <label>{isRtl ? 'وصف المشهد' : 'Visual Cue'}</label>
                        <input
                          value={scene.visual_cue}
                          onChange={(e) => updateScene(idx, 'visual_cue', e.target.value)}
                          dir={dir}
                          title="What appears on screen"
                        />
                      </div>
                      <div className="scene-field scene-field-wide">
                        <label>{isRtl ? 'النص المنطوق' : 'Narration (spoken audio)'}</label>
                        <textarea
                          value={scene.audio}
                          onChange={(e) => updateScene(idx, 'audio', e.target.value)}
                          rows={2}
                          dir={dir}
                          title="The text to be narrated"
                        />
                      </div>
                    </div>
                    <button
                      className="scene-delete-btn"
                      onClick={() => removeScene(idx)}
                      title={isRtl ? 'حذف المشهد' : 'Remove scene'}
                    >
                      <Trash2 size={16} />
                    </button>
                  </div>
                ))}
              </div>

              <div className="script-editor-actions">
                <button className="add-scene-btn" onClick={addScene}>
                  <Plus size={16} /> {isRtl ? 'أضف مشهد' : 'Add Scene'}
                </button>
                <button
                  className="generate-video-btn"
                  onClick={handleProceedWithScript}
                  disabled={editableScript.length === 0}
                >
                  <Film size={18} />
                  {isRtl ? 'ولّد الفيديو والتسويق' : 'Generate Video & Monetization'}
                </button>
              </div>
            </div>
          </section>
        )}

        {/* Result Banner */}
        {result && (
          <section className="result-banner">
            <div className="result-banner-inner">
              <CheckCircle2 size={22} />
              <div className="result-banner-text">
                <strong>Campaign for &quot;{result.topic}&quot; is ready!</strong>
                <span>Script, video with narration, and monetization brief generated.</span>
              </div>
              <button className="new-campaign-btn" onClick={handleNewCampaign}>
                <RotateCcw size={14} />
                New Campaign
              </button>
            </div>
          </section>
        )}

        {/* Results Tabs */}
        {result && (
          <section className="results-section">
            <div className="tabs">
              {(
                [
                  ['video', '🎬 Video'],
                  ['script', '📝 Script'],
                  ['monetization', '💰 Monetization'],
                  ['chat', '💭 Brainstorm'],
                ] as const
              ).map(([key, label]) => (
                <button
                  key={key}
                  className={`tab ${activeTab === key ? 'active' : ''}`}
                  onClick={() => setActiveTab(key)}
                >
                  {label}
                </button>
              ))}
            </div>

            <div className="tab-content">
              {activeTab === 'video' && (
                <>
                  <VideoPreview
                    src={result.video_path ? `/api${result.video_path}` : undefined}
                    title={`Video: ${result.topic}`}
                  />

                  {/* Social Media Publish Section */}
                  <div className="social-publish-section">
                    <h3><Link2 size={18} /> Publish To Social Media</h3>
                    <div className="social-connections">
                      {Object.entries(socialConnections).map(([platform, connected]) => (
                        <div key={platform} className="social-row">
                          <div className="social-info">
                            <span className="social-icon">
                              {platform === 'tiktok' ? '🎵' : platform === 'instagram' ? '📸' : platform === 'youtube' ? '▶️' : '🐦'}
                            </span>
                            <span className="social-name">{platform.charAt(0).toUpperCase() + platform.slice(1)}</span>
                          </div>
                          {connected ? (
                            <button
                              className="social-toggle connected"
                              onClick={() => disconnectPlatform(platform)}
                              title={`Disconnect ${platform}`}
                            >
                              <ToggleRight size={28} />
                              <span>Connected ✓</span>
                            </button>
                          ) : (
                            <button
                              className="social-toggle"
                              onClick={() => connectPlatform(platform)}
                              title={`Connect ${platform} account`}
                            >
                              <ToggleLeft size={28} />
                              <span>Connect Account</span>
                            </button>
                          )}
                        </div>
                      ))}
                    </div>
                    {connectedPlatforms.length > 0 && (
                      <div className="publish-controls">
                        <select
                          className="publish-target-select"
                          value={publishTarget}
                          onChange={(e) => setPublishTarget(e.target.value)}
                        >
                          <option value="">Select platform to publish...</option>
                          {connectedPlatforms.map(p => (
                            <option key={p} value={p}>{p.charAt(0).toUpperCase() + p.slice(1)}</option>
                          ))}
                        </select>
                        <button
                          className="publish-btn"
                          disabled={!publishTarget || phase2Loading}
                          onClick={async () => {
                            if (!genId || !publishTarget) return;
                            addToast('info', 'Publishing...', `Agent Omega is uploading your video to ${publishTarget}...`);
                            try {
                              const res = await agentService.publishToSocial(publishTarget, genId);
                              addToast('success', 'Published!', `Your video is now live on ${publishTarget}!`);
                              window.open(res.share_url, '_blank');
                            } catch (err) {
                              addToast('error', 'Publishing Failed', err instanceof Error ? err.message : 'Could not publish video.');
                            }
                          }}
                        >
                          <Send size={16} /> Publish
                        </button>
                      </div>
                    )}
                  </div>
                </>
              )}
              {activeTab === 'script' && (
                <ScriptDisplay
                  script={result.script}
                  variations={result.variations}
                  captions={result.captions}
                />
              )}
              {activeTab === 'monetization' && (
                <MonetizationBrief
                  brief={result.monetization_brief}
                  products={result.products}
                  earnings_projection={result.earnings_projection}
                />
              )}
              {activeTab === 'chat' && (
                <div className="chat-tab-wrapper">
                  <div className="agent-selector">
                    <label htmlFor="agent-select">Talk to:</label>
                    <select
                      id="agent-select"
                      value={selectedAgent}
                      onChange={(e) => setSelectedAgent(e.target.value)}
                    >
                      <option value="Agent Alpha">🔍 Agent Alpha – Trend Hunter</option>
                      <option value="Agent Beta">✍️ Agent Beta – Narrative Architect</option>
                      <option value="Agent Gamma">🎨 Agent Gamma – Media Forge</option>
                      <option value="Agent Delta">💹 Agent Delta – Profit Oracle</option>
                    </select>
                  </div>
                  <ChatBox agent={selectedAgent} onSendMessage={handleBrainstorm} />
                </div>
              )}
            </div>
          </section>
        )}

        {/* History Panel — toggled via gear icon */}
        {showHistory && (
          <section className="results-section landing-history">
            <div className="tabs">
              <button className="tab active">📜 Previous Campaigns</button>
            </div>
            <div className="tab-content">
              <HistoryList
                onSelectResult={(res) => {
                  setResult(res);
                  setActiveTab('video');
                  setShowHistory(false);
                }}
                onDelete={async (id) => {
                  try {
                    await agentService.deleteGeneration(id);
                    addToast('success', 'Deleted', 'Campaign removed.');
                  } catch {
                    addToast('error', 'Error', 'Could not delete campaign.');
                  }
                }}
              />
            </div>
          </section>
        )}
      </div>

      <footer className="dashboard-footer">
        <p>Powered by Veo 3.1 · Baidu AI · FFmpeg</p>
      </footer>
    </div>
  );
};
