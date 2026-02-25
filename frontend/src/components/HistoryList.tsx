import React, { useEffect, useState } from 'react';
import { History, Play, CheckCircle2, AlertCircle, FileText, Film, X } from 'lucide-react';
import { agentService } from '../services/agentService';
import './HistoryList.css';

interface GenerationHistory {
    id: string;
    topic: string;
    status: string;
    started_at: string;
    result?: any;
}

interface HistoryListProps {
    onSelectResult: (result: any) => void;
    onDelete?: (id: string) => Promise<void>;
}

export const HistoryList: React.FC<HistoryListProps> = ({ onSelectResult, onDelete }) => {
    const [history, setHistory] = useState<GenerationHistory[]>([]);
    const [loading, setLoading] = useState(true);

    const fetchHistory = async () => {
        try {
            const data = await agentService.getHistory();
            setHistory(data.generations);
        } catch (e) {
            console.error('Failed to load history:', e);
        } finally {
            setLoading(false);
        }
    };

    useEffect(() => {
        fetchHistory();
    }, []);

    const handleDelete = async (e: React.MouseEvent, id: string) => {
        e.stopPropagation();
        if (!onDelete) return;
        await onDelete(id);
        setHistory(prev => prev.filter(item => item.id !== id));
    };

    const getStatusIcon = (status: string) => {
        switch (status) {
            case 'completed': return <CheckCircle2 size={16} className="status-icon success" />;
            case 'failed': return <AlertCircle size={16} className="status-icon error" />;
            case 'script_ready': return <FileText size={16} className="status-icon info" />;
            default: return <Play size={16} className="status-icon running" />;
        }
    };

    if (loading) return <div className="history-loading">Loading history...</div>;

    return (
        <div className="history-list-container">
            <div className="history-header">
                <History size={18} />
                <h3>Previous Campaigns</h3>
                <span className="history-count">{history.length}</span>
            </div>
            {history.length === 0 ? (
                <div className="no-history">No past campaigns found.</div>
            ) : (
                <div className="history-grid">
                    {history.map((item) => (
                        <div
                            key={item.id}
                            className={`history-item ${item.status}`}
                            onClick={() => item.result && onSelectResult(item.result)}
                        >
                            {onDelete && (
                                <button
                                    className="delete-item-btn"
                                    onClick={(e) => handleDelete(e, item.id)}
                                    title="Delete campaign"
                                >
                                    <X size={14} />
                                </button>
                            )}
                            <div className="item-main">
                                <span className="item-topic">{item.topic}</span>
                                <span className="item-date">{new Date(item.started_at).toLocaleDateString()}</span>
                            </div>
                            <div className="item-footer">
                                <div className="item-status">
                                    {getStatusIcon(item.status)}
                                    <span>{item.status.replace('_', ' ')}</span>
                                </div>
                                {item.result && (
                                    <div className="item-assets-badge">
                                        <Film size={12} />
                                        Ready
                                    </div>
                                )}
                            </div>
                        </div>
                    ))}
                </div>
            )}
        </div>
    );
};
