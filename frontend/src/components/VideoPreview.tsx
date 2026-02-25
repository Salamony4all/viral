import React, { useRef, useState, useEffect, useCallback } from 'react';
import {
  Play, Pause, Download, Film, Smartphone, Volume2, VolumeX,
  Maximize, Minimize, ChevronDown, ChevronUp, RotateCcw,
} from 'lucide-react';
import './VideoPreview.css';

interface VideoPreviewProps {
  src?: string;
  title?: string;
}

function formatTime(secs: number): string {
  if (isNaN(secs)) return '0:00';
  const m = Math.floor(secs / 60);
  const s = Math.floor(secs % 60);
  return `${m}:${s.toString().padStart(2, '0')}`;
}

export const VideoPreview: React.FC<VideoPreviewProps> = ({ src, title = 'Generated Video' }) => {
  const videoRef = useRef<HTMLVideoElement>(null);
  const progressRef = useRef<HTMLDivElement>(null);
  const volumeRef = useRef<HTMLDivElement>(null);
  const containerRef = useRef<HTMLDivElement>(null);
  const hideTimer = useRef<ReturnType<typeof setTimeout> | null>(null);

  const [isPlaying, setIsPlaying] = useState(false);
  const [currentTime, setCurrentTime] = useState(0);
  const [duration, setDuration] = useState(0);
  const [volume, setVolume] = useState(1);
  const [muted, setMuted] = useState(false);
  const [isFullscreen, setIsFullscreen] = useState(false);
  const [showControls, setShowControls] = useState(true);
  const [guideOpen, setGuideOpen] = useState(false);
  const [buffered, setBuffered] = useState(0);

  const hasVideo = !!(src && src.length > 0);

  // Auto-hide controls after 3s of inactivity
  const resetHideTimer = useCallback(() => {
    setShowControls(true);
    if (hideTimer.current) clearTimeout(hideTimer.current);
    hideTimer.current = setTimeout(() => {
      if (isPlaying) setShowControls(false);
    }, 3000);
  }, [isPlaying]);

  useEffect(() => () => { if (hideTimer.current) clearTimeout(hideTimer.current); }, []);

  const togglePlay = () => {
    const v = videoRef.current;
    if (!v) return;
    if (v.paused) v.play(); else v.pause();
  };

  const handleTimeUpdate = () => {
    const v = videoRef.current;
    if (!v) return;
    setCurrentTime(v.currentTime);
    if (v.buffered.length > 0) {
      setBuffered(v.buffered.end(v.buffered.length - 1));
    }
  };

  const handleLoadedMetadata = () => {
    if (videoRef.current) setDuration(videoRef.current.duration);
  };

  const seekTo = (e: React.MouseEvent<HTMLDivElement>) => {
    const v = videoRef.current;
    const bar = progressRef.current;
    if (!v || !bar) return;
    const rect = bar.getBoundingClientRect();
    const ratio = Math.max(0, Math.min(1, (e.clientX - rect.left) / rect.width));
    v.currentTime = ratio * v.duration;
  };

  const handleVolumeClick = (e: React.MouseEvent<HTMLDivElement>) => {
    const bar = volumeRef.current;
    if (!bar) return;
    const rect = bar.getBoundingClientRect();
    const ratio = Math.max(0, Math.min(1, (e.clientX - rect.left) / rect.width));
    setVolume(ratio);
    if (videoRef.current) videoRef.current.volume = ratio;
    setMuted(ratio === 0);
  };

  const toggleMute = () => {
    const v = videoRef.current;
    if (!v) return;
    v.muted = !muted;
    setMuted(!muted);
  };

  const restart = () => {
    const v = videoRef.current;
    if (!v) return;
    v.currentTime = 0;
    v.play();
  };

  const toggleFullscreen = () => {
    const el = containerRef.current;
    if (!el) return;
    if (!document.fullscreenElement) {
      el.requestFullscreen?.();
      setIsFullscreen(true);
    } else {
      document.exitFullscreen?.();
      setIsFullscreen(false);
    }
  };

  useEffect(() => {
    const handler = () => setIsFullscreen(!!document.fullscreenElement);
    document.addEventListener('fullscreenchange', handler);
    return () => document.removeEventListener('fullscreenchange', handler);
  }, []);

  const progressPct = duration ? (currentTime / duration) * 100 : 0;
  const bufferedPct = duration ? (buffered / duration) * 100 : 0;
  const volumePct = muted ? 0 : volume * 100;

  return (
    <div className="video-preview-wrapper">
      <div className="video-phone-row">
        {/* Phone + Player */}
        <div className="phone-frame" ref={containerRef}>
          <div className="phone-notch" />
          <div
            className="phone-screen"
            onMouseMove={resetHideTimer}
            onTouchStart={resetHideTimer}
            onClick={togglePlay}
          >
            {hasVideo ? (
              <>
                <video
                  ref={videoRef}
                  src={src}
                  playsInline
                  onPlay={() => setIsPlaying(true)}
                  onPause={() => setIsPlaying(false)}
                  onTimeUpdate={handleTimeUpdate}
                  onLoadedMetadata={handleLoadedMetadata}
                  onEnded={() => setIsPlaying(false)}
                  className="phone-video"
                />

                {/* Custom Controls Overlay */}
                <div
                  className={`player-controls-overlay ${showControls || !isPlaying ? 'visible' : 'hidden'}`}
                  onClick={(e) => e.stopPropagation()}
                >
                  {/* Center Play/Pause big button */}
                  <button className="center-play-btn" onClick={togglePlay}>
                    {isPlaying ? <Pause size={36} /> : <Play size={36} />}
                  </button>

                  {/* Bottom control bar */}
                  <div className="player-bottom">
                    {/* Progress bar */}
                    <div
                      className="player-progress"
                      ref={progressRef}
                      onClick={seekTo}
                    >
                      <div
                        className="progress-buffered"
                        // @ts-ignore
                        style={{ '--pct': `${bufferedPct}%` }}
                      />
                      <div
                        className="progress-fill"
                        // @ts-ignore
                        style={{ '--pct': `${progressPct}%` }}
                      />
                      <div
                        className="progress-thumb"
                        // @ts-ignore
                        style={{ '--left': `${progressPct}%` }}
                      />
                    </div>

                    {/* Control row */}
                    <div className="player-row">
                      <div className="player-left">
                        <button onClick={togglePlay} className="ctrl-btn">
                          {isPlaying ? <Pause size={16} /> : <Play size={16} />}
                        </button>
                        <button onClick={restart} className="ctrl-btn" title="Restart">
                          <RotateCcw size={14} />
                        </button>
                        <span className="time-display">
                          {formatTime(currentTime)} / {formatTime(duration)}
                        </span>
                      </div>

                      <div className="player-right">
                        {/* Volume control */}
                        <button onClick={toggleMute} className="ctrl-btn">
                          {muted || volume === 0 ? <VolumeX size={16} /> : <Volume2 size={16} />}
                        </button>
                        <div
                          className="volume-bar"
                          ref={volumeRef}
                          onClick={handleVolumeClick}
                          title="Volume"
                        >
                          <div
                            className="volume-fill"
                            // @ts-ignore
                            style={{ '--pct': `${volumePct}%` }}
                          />
                          <div
                            className="volume-thumb"
                            // @ts-ignore
                            style={{ '--left': `${volumePct}%` }}
                          />
                        </div>

                        <button onClick={toggleFullscreen} className="ctrl-btn" title="Fullscreen">
                          {isFullscreen ? <Minimize size={16} /> : <Maximize size={16} />}
                        </button>
                      </div>
                    </div>
                  </div>
                </div>
              </>
            ) : (
              <div className="video-placeholder">
                <Film size={48} strokeWidth={1.5} />
                <p>Video Preview</p>
                <small>Your generated TikTok video will appear here once the Media Forge agent finishes rendering.</small>
              </div>
            )}
          </div>
          <div className="phone-home" />
        </div>

        {/* Side panel */}
        <div className="video-side-panel">
          <div className="video-info-card">
            <Smartphone size={18} />
            <div>
              <h3>{title}</h3>
              <span className="video-meta">1080 x 1920 · 30 FPS</span>
            </div>
          </div>

          {hasVideo && (
            <a href={src} download className="video-action-btn" title="Download video">
              <Download size={16} />
              Download Video
            </a>
          )}

          <button className="guide-toggle" onClick={() => setGuideOpen((o) => !o)}>
            <span>Green Screen Posting Guide</span>
            {guideOpen ? <ChevronUp size={16} /> : <ChevronDown size={16} />}
          </button>

          {guideOpen && (
            <div className="guide-content">
              <ol>
                <li>Open <strong>TikTok</strong> on your phone</li>
                <li>Record a <strong>3-second intro/reaction</strong> using the native camera</li>
                <li>In the editor, tap <strong>Effects → Green Screen</strong></li>
                <li>Upload <strong>this video</strong> as the background</li>
                <li>This resets metadata and signals <strong>"Human Creator"</strong> to the algorithm</li>
                <li>Add caption, hashtags from the Script tab, and post during <strong>6–10 PM</strong></li>
              </ol>
              <p className="guide-tip">Engage with comments in the first 60 minutes for maximum reach.</p>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};
