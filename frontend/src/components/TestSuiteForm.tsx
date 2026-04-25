import { useEffect } from 'react';
import { useForm, useFieldArray, Controller } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import { z } from 'zod';
import { useTestSuite, useCreateTestSuite, useUpdateTestSuite } from '../hooks/useTestSuites';
import { usePrompts } from '../hooks/usePrompts';
import { useSchemas } from '../hooks/useSchemas';
import Select, { MultiValue } from 'react-select';

type SelectOption = {
  value: string;
  label: string;
};

const testInputSchema = z.object({
  input_data: z.string().min(1, 'Input data is required').refine(
    (val) => {
      try {
        JSON.parse(val);
        return true;
      } catch {
        return false;
      }
    },
    { message: 'Invalid JSON' }
  ),
  expected_output: z.string().optional().refine(
    (val) => {
      if (!val) return true;
      try {
        JSON.parse(val);
        return true;
      } catch {
        return false;
      }
    },
    { message: 'Invalid JSON' }
  ),
  description: z.string().optional(),
});

const testSuiteSchema = z.object({
  name: z.string().min(1, 'Name is required'),
  description: z.string().optional(),
  prompt_ids: z.array(z.string()).min(1, 'At least one prompt is required'),
  schema_ids: z.array(z.string()).min(1, 'At least one schema is required'),
  test_inputs: z.array(testInputSchema).min(1, 'At least one test input is required'),
});

type TestSuiteFormData = z.infer<typeof testSuiteSchema>;

interface TestSuiteFormProps {
  testSuiteId?: string | null;
  onClose: () => void;
  onSuccess: () => void;
}

const TestSuiteForm = ({ testSuiteId, onClose, onSuccess }: TestSuiteFormProps) => {
  const { data: existingTestSuite, isLoading: isLoadingTestSuite } = useTestSuite(testSuiteId || '');
  const { data: prompts, isLoading: isLoadingPrompts } = usePrompts();
  const { data: schemas, isLoading: isLoadingSchemas } = useSchemas();
  const createMutation = useCreateTestSuite();
  const updateMutation = useUpdateTestSuite();

  const {
    register,
    handleSubmit,
    control,
    reset,
    formState: { errors, isSubmitting },
  } = useForm<TestSuiteFormData>({
    resolver: zodResolver(testSuiteSchema),
    defaultValues: {
      prompt_ids: [],
      schema_ids: [],
      test_inputs: [{ input_data: '{}', expected_output: '', description: '' }],
    },
  });

  const { fields, append, remove } = useFieldArray({
    control,
    name: 'test_inputs',
  });

  const promptOptions: SelectOption[] = prompts?.map(p => ({ value: p.id, label: p.name })) || [];
  const schemaOptions: SelectOption[] = schemas?.map(s => ({ value: s.id, label: s.name })) || [];

  useEffect(() => {
    if (existingTestSuite) {
      reset({
        name: existingTestSuite.name,
        description: existingTestSuite.description,
        prompt_ids: existingTestSuite.prompt_ids,
        schema_ids: existingTestSuite.schema_ids,
        test_inputs: existingTestSuite.test_inputs.map(ti => ({
          input_data: JSON.stringify(ti.input_data, null, 2),
          expected_output: ti.expected_output ? JSON.stringify(ti.expected_output, null, 2) : '',
          description: ti.description || '',
        })),
      });
    }
  }, [existingTestSuite, reset]);

  const onSubmit = async (data: TestSuiteFormData) => {
    const formattedData = {
      ...data,
      test_inputs: data.test_inputs.map(ti => ({
        input_data: JSON.parse(ti.input_data),
        expected_output: ti.expected_output ? JSON.parse(ti.expected_output) : undefined,
        description: ti.description,
      })),
    };
    if (testSuiteId) {
      await updateMutation.mutateAsync({ id: testSuiteId, data: formattedData });
    } else {
      await createMutation.mutateAsync(formattedData);
    }
    onSuccess();
  };

  if (isLoadingTestSuite || isLoadingPrompts || isLoadingSchemas) return <div>Loading...</div>;

  return (
    <div className="fixed inset-0 bg-gray-600 bg-opacity-50 overflow-y-auto h-full w-full z-50">
      <div className="relative top-20 mx-auto p-5 border w-full max-w-3xl shadow-lg rounded-md bg-white">
        <h3 className="text-lg font-medium leading-6 text-gray-900 mb-4">
          {testSuiteId ? 'Edit Test Suite' : 'Create Test Suite'}
        </h3>
        <form onSubmit={handleSubmit(onSubmit)} className="space-y-4 max-h-[80vh] overflow-y-auto p-2">
          <div>
            <label className="block text-sm font-medium text-gray-700">Name</label>
            <input
              type="text"
              {...register('name')}
              className="mt-1 block w-full border border-gray-300 rounded-md shadow-sm p-2"
            />
            {errors.name && <p className="text-red-500 text-xs mt-1">{errors.name.message}</p>}
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-700">Description</label>
            <textarea
              rows={2}
              {...register('description')}
              className="mt-1 block w-full border border-gray-300 rounded-md shadow-sm p-2"
            />
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700">Prompts</label>
            <Controller
              name="prompt_ids"
              control={control}
              render={({ field }) => (
                <Select
                  isMulti
                  instanceId="prompts-select"
                  options={promptOptions}
                  value={promptOptions.filter(option => field.value?.includes(option.value))}
                  onChange={(selected: MultiValue<SelectOption>) =>
                    field.onChange(selected.map((option: SelectOption) => option.value))
                  }
                  className="mt-1"
                  classNamePrefix="select"
                />
              )}
            />
            {errors.prompt_ids && <p className="text-red-500 text-xs mt-1">{errors.prompt_ids.message}</p>}
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700">Schemas</label>
            <Controller
              name="schema_ids"
              control={control}
              render={({ field }) => (
                <Select
                  isMulti
                  instanceId="schemas-select"
                  options={schemaOptions}
                  value={schemaOptions.filter(option => field.value?.includes(option.value))}
                  onChange={(selected: MultiValue<SelectOption>) =>
                    field.onChange(selected.map((option: SelectOption) => option.value))
                  }
                  className="mt-1"
                  classNamePrefix="select"
                />
              )}
            />
            {errors.schema_ids && <p className="text-red-500 text-xs mt-1">{errors.schema_ids.message}</p>}
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">Test Inputs</label>
            {fields.map((field, index) => (
              <div key={field.id} className="border p-4 mb-2 rounded">
                <div className="flex justify-between">
                  <h4 className="font-medium">Input #{index + 1}</h4>
                  {fields.length > 1 && (
                    <button
                      type="button"
                      onClick={() => remove(index)}
                      className="text-red-600 hover:text-red-900 text-sm"
                    >
                      Remove
                    </button>
                  )}
                </div>
                <div className="mt-2">
                  <label className="block text-sm font-medium text-gray-700">Input Data (JSON)</label>
                  <textarea
                    rows={3}
                    {...register(`test_inputs.${index}.input_data`)}
                    className="mt-1 block w-full border border-gray-300 rounded-md shadow-sm p-2 font-mono text-sm"
                  />
                  {errors.test_inputs?.[index]?.input_data && (
                    <p className="text-red-500 text-xs mt-1">{errors.test_inputs[index]?.input_data?.message}</p>
                  )}
                </div>
                <div className="mt-2">
                  <label className="block text-sm font-medium text-gray-700">Expected Output (JSON, optional)</label>
                  <textarea
                    rows={2}
                    {...register(`test_inputs.${index}.expected_output`)}
                    className="mt-1 block w-full border border-gray-300 rounded-md shadow-sm p-2 font-mono text-sm"
                  />
                  {errors.test_inputs?.[index]?.expected_output && (
                    <p className="text-red-500 text-xs mt-1">{errors.test_inputs[index]?.expected_output?.message}</p>
                  )}
                </div>
                <div className="mt-2">
                  <label className="block text-sm font-medium text-gray-700">Description</label>
                  <input
                    type="text"
                    {...register(`test_inputs.${index}.description`)}
                    className="mt-1 block w-full border border-gray-300 rounded-md shadow-sm p-2"
                  />
                </div>
              </div>
            ))}
            <button
              type="button"
              onClick={() => append({ input_data: '{}', expected_output: '', description: '' })}
              className="mt-2 text-indigo-600 hover:text-indigo-900 text-sm"
            >
              + Add Test Input
            </button>
            {errors.test_inputs && !Array.isArray(errors.test_inputs) && (
              <p className="text-red-500 text-xs mt-1">{errors.test_inputs.message}</p>
            )}
          </div>

          <div className="flex justify-end space-x-2 pt-4">
            <button
              type="button"
              onClick={onClose}
              className="px-4 py-2 bg-gray-200 text-gray-800 rounded-md hover:bg-gray-300"
            >
              Cancel
            </button>
            <button
              type="submit"
              disabled={isSubmitting}
              className="px-4 py-2 bg-indigo-600 text-white rounded-md hover:bg-indigo-700 disabled:opacity-50"
            >
              {isSubmitting ? 'Saving...' : 'Save'}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
};

export default TestSuiteForm;
