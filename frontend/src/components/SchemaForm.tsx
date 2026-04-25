import { useEffect } from 'react';
import { useForm, Controller } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import { z } from 'zod';
import { useSchema, useCreateSchema, useUpdateSchema } from '../hooks/useSchemas';
import Select, { MultiValue } from 'react-select';

type SelectOption = {
  value: string;
  label: string;
};

const schemaSchema = z.object({
  name: z.string().min(1, 'Name is required'),
  schema_dict: z.string().min(1, 'Schema JSON is required').refine(
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
  description: z.string().optional(),
  // Hypothetical field to demonstrate multi-select
  tags: z.array(z.string()).optional(),
});

type SchemaFormData = z.infer<typeof schemaSchema>;

interface SchemaFormProps {
  schemaId?: string | null;
  onClose: () => void;
  onSuccess: () => void;
}

const SchemaForm = ({ schemaId, onClose, onSuccess }: SchemaFormProps) => {
  const { data: existingSchema, isLoading } = useSchema(schemaId || '');
  const createMutation = useCreateSchema();
  const updateMutation = useUpdateSchema();

  // For demonstration, we'll use mock data for tags.
  // In a real app, this would come from a hook like `useTags()`.
  const tagOptions: SelectOption[] = [
    { value: 'user-profile', label: 'User Profile' },
    { value: 'product-catalog', label: 'Product Catalog' },
    { value: 'pii', label: 'PII' },
    { value: 'finance', label: 'Finance' },
  ];

  const {
    register,
    handleSubmit,
    reset,
    control,
    formState: { errors, isSubmitting }
  } = useForm<SchemaFormData>({
    resolver: zodResolver(schemaSchema),
    defaultValues: {
      schema_dict: '{}',
    },
  });

  useEffect(() => {
    if (existingSchema) {
      reset({
        name: existingSchema.name,
        schema_dict: JSON.stringify(existingSchema.schema_dict, null, 2),
        description: existingSchema.description,
      });
    }
  }, [existingSchema, reset]);

  const onSubmit = async (data: SchemaFormData) => {
    const parsedSchemaDict = JSON.parse(data.schema_dict);
    if (schemaId) {
      await updateMutation.mutateAsync({
        id: schemaId,
        data: { ...data, schema_dict: parsedSchemaDict },
      });
    } else {
      await createMutation.mutateAsync({ ...data, schema_dict: parsedSchemaDict });
    }
    onSuccess();
  };

  if (isLoading) return <div>Loading...</div>;

  return (
    <div className="fixed inset-0 bg-gray-600 bg-opacity-50 overflow-y-auto h-full w-full z-50">
      <div className="relative top-20 mx-auto p-5 border w-96 shadow-lg rounded-md bg-white">
        <h3 className="text-lg font-medium leading-6 text-gray-900 mb-4">
          {schemaId ? 'Edit Schema' : 'Create Schema'}
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
            <label className="block text-sm font-medium text-gray-700">Schema JSON</label>
            <textarea
              rows={8}
              {...register('schema_dict')}
              className="mt-1 block w-full border border-gray-300 rounded-md shadow-sm p-2 font-mono text-sm"
              placeholder='{"type": "object", "properties": {...}}'
            />
            {errors.schema_dict && <p className="text-red-500 text-xs mt-1">{errors.schema_dict.message}</p>}
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
            <label className="block text-sm font-medium text-gray-700">Tags (Example)</label>
            <Controller
              name="tags"
              control={control}
              render={({ field }) => (
                <Select
                  isMulti
                  instanceId="schema-tags-select"
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
  );
};

export default SchemaForm;
