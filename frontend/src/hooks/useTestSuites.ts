import { useQuery, useMutation, useQueryClient } from 'react-query';
import {
  getTestSuites,
  getTestSuite,
  createTestSuite,
  updateTestSuite,
  deleteTestSuite,
} from '../services/testSuites';
import { TestSuiteCreate, TestSuiteUpdate } from '../types';

export const useTestSuites = (skip?: number, limit?: number) => {
  return useQuery(['testSuites', skip, limit], () => getTestSuites(skip, limit));
};

export const useTestSuite = (id: string) => {
  return useQuery(['testSuite', id], () => getTestSuite(id), {
    enabled: !!id,
  });
};

export const useCreateTestSuite = () => {
  const queryClient = useQueryClient();
  return useMutation((data: TestSuiteCreate) => createTestSuite(data), {
    onSuccess: () => {
      queryClient.invalidateQueries('testSuites');
    },
  });
};

export const useUpdateTestSuite = () => {
  const queryClient = useQueryClient();
  return useMutation(
    ({ id, data }: { id: string; data: TestSuiteUpdate }) => updateTestSuite(id, data),
    {
      onSuccess: (_, { id }) => {
        queryClient.invalidateQueries('testSuites');
        queryClient.invalidateQueries(['testSuite', id]);
      },
    }
  );
};

export const useDeleteTestSuite = () => {
  const queryClient = useQueryClient();
  return useMutation((id: string) => deleteTestSuite(id), {
    onSuccess: () => {
      queryClient.invalidateQueries('testSuites');
    },
  });
};