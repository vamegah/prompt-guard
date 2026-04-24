import api from './api';
import { Schema, SchemaCreate, SchemaUpdate } from '../types';

export const getSchemas = async (skip = 0, limit = 100): Promise<Schema[]> => {
  const response = await api.get('/schemas', { params: { skip, limit } });
  return response.data;
};

export const getSchema = async (id: string): Promise<Schema> => {
  const response = await api.get(`/schemas/${id}`);
  return response.data;
};

export const createSchema = async (data: SchemaCreate): Promise<Schema> => {
  const response = await api.post('/schemas', data);
  return response.data;
};

export const updateSchema = async (id: string, data: SchemaUpdate): Promise<Schema> => {
  const response = await api.patch(`/schemas/${id}`, data);
  return response.data;
};

export const deleteSchema = async (id: string): Promise<void> => {
  await api.delete(`/schemas/${id}`);
};