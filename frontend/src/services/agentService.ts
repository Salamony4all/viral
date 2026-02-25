import axios from 'axios';
import type { AgentResponse, GenerationStatus, ScriptColumn } from '../types';

const API_BASE_URL = import.meta.env.VITE_API_URL || '/api';

const apiClient = axios.create({
  baseURL: API_BASE_URL,
  timeout: 300_000,
});

export const agentService = {
  async generateCampaign(
    topic: string,
  ): Promise<{ generation_id: string; status: string }> {
    const { data } = await apiClient.post('/generate', { topic });
    return data;
  },

  async getGenerationStatus(genId?: string): Promise<GenerationStatus> {
    const url = genId ? `/status/${genId}` : '/status';
    const { data } = await apiClient.get<GenerationStatus>(url);
    return data;
  },

  async proceedWithScript(
    genId: string,
    scriptColumns: ScriptColumn[],
  ): Promise<{ generation_id: string; status: string }> {
    const { data } = await apiClient.post(`/proceed/${genId}`, {
      script_columns: scriptColumns,
    });
    return data;
  },

  async brainstormWithAgent(
    agent: string,
    prompt: string,
  ): Promise<AgentResponse> {
    const { data } = await apiClient.post<AgentResponse>('/brainstorm', {
      agent,
      prompt,
    });
    return data;
  },

  async getRecentResults() {
    const { data } = await apiClient.get('/results');
    return data;
  },

  async getHistory(): Promise<{ generations: any[] }> {
    const { data } = await apiClient.get('/generations');
    return data;
  },

  async deleteGeneration(genId: string): Promise<void> {
    await apiClient.delete(`/generations/${genId}`);
  },

  async getSocialStatus(): Promise<Record<string, { connected: boolean; connected_at?: string }>> {
    const { data } = await apiClient.get('/social/status');
    return data;
  },

  async disconnectSocial(platform: string): Promise<void> {
    await apiClient.post(`/social/disconnect/${platform}`);
  },

  async publishToSocial(platform: string, genId: string): Promise<any> {
    const { data } = await apiClient.post(`/social/publish/${platform}/${genId}`);
    return data;
  },
};



export default apiClient;
