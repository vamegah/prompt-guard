import { useQuery, useMutation, useQueryClient } from 'react-query';
import {
  getPrompts,
  getPrompt,
  createPrompt,
  updatePrompt,
  deletePrompt,
} from '../services/prompts';
import { PromptCreate, PromptUpdate } from '../types';

export const usePrompts = (skip?: number, limit?: number) => {
  return useQuery(['prompts', skip, limit], () => getPrompts(skip, limit));
};

export const usePrompt = (id: string) => {
  return useQuery(['prompt', id], () => getPrompt(id), {
    enabled: !!id,
  });
};

export const useCreatePrompt = () => {
  const queryClient = useQueryClient();
  return useMutation((data: PromptCreate) => createPrompt(data), {
    onSuccess: () => {
      queryClient.invalidateQueries('prompts');
    },
  });
};

export const useUpdatePrompt = () => {
  const queryClient = useQueryClient();
  return useMutation(
    ({ id, data }: { id: string; data: PromptUpdate }) => updatePrompt(id, data),
    {
      onSuccess: (_, { id }) => {
        queryClient.invalidateQueries('prompts');
        queryClient.invalidateQueries(['prompt', id]);
      },
    }
  );
};

export const useDeletePrompt = () => {
  const queryClient = useQueryClient();
  return useMutation((id: string) => deletePrompt(id), {
    onSuccess: () => {
      queryClient.invalidateQueries('prompts');
    },
  });
};