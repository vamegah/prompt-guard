import { useState } from 'react';
import { usePrompts, useDeletePrompt } from '../hooks/usePrompts';
import PromptForm from '../components/PromptForm';

const PromptsPage = () => {
  const [showForm, setShowForm] = useState(false);
  const [editingPrompt, setEditingPrompt] = useState<string | null>(null);
  const { data: prompts, isLoading, error } = usePrompts();
  const deleteMutation = useDeletePrompt();

  const handleDelete = (id: string) => {
    if (confirm('Are you sure?')) {
      deleteMutation.mutate(id);
    }
  };

  if (isLoading) return <div>Loading...</div>;
  if (error) return <div>Error loading prompts</div>;

  return (
    <div>
      <div className="flex justify-between items-center mb-6">
        <h1 className="text-2xl font-semibold text-gray-900">Prompts</h1>
        <button
          onClick={() => setShowForm(true)}
          className="bg-indigo-600 text-white px-4 py-2 rounded-md hover:bg-indigo-700"
        >
          Create Prompt
        </button>
      </div>

      {showForm && (
        <PromptForm
          onClose={() => setShowForm(false)}
          onSuccess={() => setShowForm(false)}
        />
      )}

      <div className="bg-white shadow overflow-hidden sm:rounded-md">
        <ul className="divide-y divide-gray-200">
          {prompts?.map((prompt) => (
            <li key={prompt.id} className="px-6 py-4">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm font-medium text-indigo-600 truncate">{prompt.name}</p>
                  <p className="text-sm text-gray-500">{prompt.template.substring(0, 100)}...</p>
                </div>
                <div className="flex space-x-2">
                  <button
                    onClick={() => setEditingPrompt(prompt.id)}
                    className="text-indigo-600 hover:text-indigo-900"
                  >
                    Edit
                  </button>
                  <button
                    onClick={() => handleDelete(prompt.id)}
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

      {editingPrompt && (
        <PromptForm
          promptId={editingPrompt}
          onClose={() => setEditingPrompt(null)}
          onSuccess={() => setEditingPrompt(null)}
        />
      )}
    </div>
  );
};

export default PromptsPage;
