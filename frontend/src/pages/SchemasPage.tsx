import { useState } from 'react';
import { useSchemas, useDeleteSchema } from '../hooks/useSchemas';
import SchemaForm from '../components/SchemaForm';

const SchemasPage = () => {
  const [showForm, setShowForm] = useState(false);
  const [editingSchema, setEditingSchema] = useState<string | null>(null);
  const { data: schemas, isLoading, error } = useSchemas();
  const deleteMutation = useDeleteSchema();

  const handleDelete = (id: string) => {
    if (confirm('Are you sure?')) {
      deleteMutation.mutate(id);
    }
  };

  if (isLoading) return <div>Loading...</div>;
  if (error) return <div>Error loading schemas</div>;

  return (
    <div>
      <div className="flex justify-between items-center mb-6">
        <h1 className="text-2xl font-semibold text-gray-900">JSON Schemas</h1>
        <button
          onClick={() => setShowForm(true)}
          className="bg-indigo-600 text-white px-4 py-2 rounded-md hover:bg-indigo-700"
        >
          Create Schema
        </button>
      </div>

      {showForm && (
        <SchemaForm
          onClose={() => setShowForm(false)}
          onSuccess={() => setShowForm(false)}
        />
      )}

      <div className="bg-white shadow overflow-hidden sm:rounded-md">
        <ul className="divide-y divide-gray-200">
          {schemas?.map((schema) => (
            <li key={schema.id} className="px-6 py-4">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm font-medium text-indigo-600 truncate">{schema.name}</p>
                  <p className="text-sm text-gray-500">
                    {schema.description || 'No description'}
                  </p>
                </div>
                <div className="flex space-x-2">
                  <button
                    onClick={() => setEditingSchema(schema.id)}
                    className="text-indigo-600 hover:text-indigo-900"
                  >
                    Edit
                  </button>
                  <button
                    onClick={() => handleDelete(schema.id)}
                    className="text-red-600 hover:text-red-900"
                  >
                    Delete
                  </button>
                </div>
              </div>
            </li>
          ))}
        </ul>
      </div>

      {editingSchema && (
        <SchemaForm
          schemaId={editingSchema}
          onClose={() => setEditingSchema(null)}
          onSuccess={() => setEditingSchema(null)}
        />
      )}
    </div>
  );
};

export default SchemasPage;