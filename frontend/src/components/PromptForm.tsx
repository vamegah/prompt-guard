import { useEffect } from 'react';
import { useForm, Controller } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import { z } from 'zod';
import { usePrompt, useCreatePrompt, useUpdatePrompt } from '../hooks/usePrompts';
import { PromptCreate } from '../types';
import Select, { MultiValue } from 'react-select';

type SelectOption = {
  value: string;
  label: string;
};

const promptSchema = z.object({
  name: z.string().min(1, 'Name is required'),
  template: z.string().min(1, 'Template is required'),
  description: z.string().optional(),
  version: z.string().min(1, 'Version is required'),
  metadata: z.record(z.any()).optional(),
  // Hypothetical field to demonstrate multi-select
  tags: z.array(z.string()).optional(),
});

type PromptFormData = z.infer<typeof promptSchema>;

interface PromptFormProps {
  promptId?: string | null;
  onClose: () => void;
  onSuccess: () => void;
}

const PromptForm = ({ promptId, onClose, onSuccess }: PromptFormProps) => {
  const { data: existingPrompt, isLoading } = usePrompt(promptId || '');
  const createMutation = useCreatePrompt();
  const updateMutation = useUpdatePrompt();

  // For demonstration, we'll use mock data for tags.
  // In a real app, this would come from a hook like `useTags()`.
  const tagOptions: SelectOption[] = [
    { value: 'translator', label: 'Translator' },
    { value: 'summarizer', label: 'Summarizer' },
    { value: 'experimental', label: 'Experimental' },
    { value: 'pii-scrubbing', label: 'PII Scrubbing' },
  ];

  const {
    register,
    handleSubmit,
    reset,
    control,
    formState: { errors, isSubmitting }
  } = useForm<PromptFormData>({
    resolver: zodResolver(promptSchema),
    defaultValues: {
      version: '1.0.0',
    },
  });

  useEffect(() => {
    if (existingPrompt) {
      reset({
        name: existingPrompt.name,
        template: existingPrompt.template,
        description: existingPrompt.description,
        version: existingPrompt.version,
        metadata: existingPrompt.metadata,
        tags: existingPrompt.tags || [],
      });
    }
  }, [existingPrompt, reset]);

  const onSubmit = async (data: PromptFormData) => {
    if (promptId) {
      await updateMutation.mutateAsync({ id: promptId, data });
    } else {
      await createMutation.mutateAsync(data as PromptCreate);
    }
    onSuccess();
  };

  if (isLoading) return <div>Loading...</div>;

  return (
    <div className="fixed inset-0 bg-gray-600 bg-opacity-50 overflow-y-auto h-full w-full z-50">
      <div className="relative top-20 mx-auto p-5 border w-96 shadow-lg rounded-md bg-white">
        <div className="mt-3">
          <h3 className="text-lg font-medium leading-6 text-gray-900 mb-4">
            {promptId ? 'Edit Prompt' : 'Create Prompt'}
          </h3>
          <form onSubmit={handleSubmit(onSubmit)} className="space-y-4">
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
              <label className="block text-sm font-medium text-gray-700">Template</label>
              <textarea
                rows={4}
                {...register('template')}
                className="mt-1 block w-full border border-gray-300 rounded-md shadow-sm p-2"
              />
              {errors.template && <p className="text-red-500 text-xs mt-1">{errors.template.message}</p>}
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
              <label className="block text-sm font-medium text-gray-700">Version</label>
              <input
                type="text"
                {...register('version')}
                className="mt-1 block w-full border border-gray-300 rounded-md shadow-sm p-2"
              />
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700">Tags (Example)</label>
              <Controller
                name="tags"
                control={control}
                render={({ field }) => (
                  <Select
                    isMulti
                    instanceId="prompt-tags-select"
                    options={tagOptions}
                    value={tagOptions.filter(option => field.value?.includes(option.value))}
                    onChange={(selected: MultiValue<SelectOption>) =>
                      field.onChange(selected.map((option: SelectOption) => option.value))
                    }
                    className="mt-1"
                    classNamePrefix="select"
                  />
                )}
              />
            </div>
            <div className="flex justify-end space-x-2">
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
    </div>
  );
};

export default PromptForm;
