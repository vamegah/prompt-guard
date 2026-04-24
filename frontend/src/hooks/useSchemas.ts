import { useQuery, useMutation, useQueryClient } from 'react-query';
import {
  getSchemas,
  getSchema,
  createSchema,
  updateSchema,
  deleteSchema,
} from '../services/schemas';
import { SchemaCreate, SchemaUpdate } from '../types';

export const useSchemas = (skip?: number, limit?: number) => {
  return useQuery(['schemas', skip, limit], () => getSchemas(skip, limit));
};

export const useSchema = (id: string) => {
  return useQuery(['schema', id], () => getSchema(id), {
    enabled: !!id,
  });
};

export const useCreateSchema = () => {
  const queryClient = useQueryClient();
  return useMutation((data: SchemaCreate) => createSchema(data), {
    onSuccess: () => {
      queryClient.invalidateQueries('schemas');
    },
  });
};

export const useUpdateSchema = () => {
  const queryClient = useQueryClient();
  return useMutation(
    ({ id, data }: { id: string; data: SchemaUpdate }) => updateSchema(id, data),
    {
      onSuccess: (_, { id }) => {
        queryClient.invalidateQueries('schemas');
        queryClient.invalidateQueries(['schema', id]);
      },
    }
  );
};

export const useDeleteSchema = () => {
  const queryClient = useQueryClient();
  return useMutation((id: string) => deleteSchema(id), {
    onSuccess: () => {
      queryClient.invalidateQueries('schemas');
    },
  });
};