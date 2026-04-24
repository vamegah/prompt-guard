import api from './api';
import { TestSuite, TestSuiteCreate, TestSuiteUpdate } from '../types';

export const getTestSuites = async (skip = 0, limit = 100): Promise<TestSuite[]> => {
  const response = await api.get('/test-suites', { params: { skip, limit } });
  return response.data;
};

export const getTestSuite = async (id: string): Promise<TestSuite> => {
  const response = await api.get(`/test-suites/${id}`);
  return response.data;
};

export const createTestSuite = async (data: TestSuiteCreate): Promise<TestSuite> => {
  const response = await api.post('/test-suites', data);
  return response.data;
};

export const updateTestSuite = async (id: string, data: TestSuiteUpdate): Promise<TestSuite> => {
  const response = await api.patch(`/test-suites/${id}`, data);
  return response.data;
};

export const deleteTestSuite = async (id: string): Promise<void> => {
  await api.delete(`/test-suites/${id}`);
};