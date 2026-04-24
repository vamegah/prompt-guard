import api from './api';
import { Prompt, PromptCreate, PromptUpdate } from '../types';

export const getPrompts = async (skip = 0, limit = 100): Promise<Prompt[]> => {
  const response = await api.get('/prompts', { params: { skip, limit } });
  return response.data;
};

export const getPrompt = async (id: string): Promise<Prompt> => {
  const response = await api.get(`/prompts/${id}`);
  return response.data;
};

export const createPrompt = async (data: PromptCreate): Promise<Prompt> => {
  const response = await api.post('/prompts', data);
  return response.data;
};

export const updatePrompt = async (id: string, data: PromptUpdate): Promise<Prompt> => {
  const response = await api.patch(`/prompts/${id}`, data);
  return response.data;
};

export const deletePrompt = async (id: string): Promise<void> => {
  await api.delete(`/prompts/${id}`);
};