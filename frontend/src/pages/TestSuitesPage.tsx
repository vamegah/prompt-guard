import { useState } from 'react';
import { useTestSuites, useDeleteTestSuite } from '../hooks/useTestSuites';
import TestSuiteForm from '../components/TestSuiteForm';

const TestSuitesPage = () => {
  const [showForm, setShowForm] = useState(false);
  const [editingTestSuite, setEditingTestSuite] = useState<string | null>(null);
  const { data: testSuites, isLoading, error } = useTestSuites();
  const deleteMutation = useDeleteTestSuite();

  const handleDelete = (id: string) => {
    if (confirm('Are you sure?')) {
      deleteMutation.mutate(id);
    }
  };

  if (isLoading) return <div>Loading...</div>;
  if (error) return <div>Error loading test suites</div>;

  return (
    <div>
      <div className="flex justify-between items-center mb-6">
        <h1 className="text-2xl font-semibold text-gray-900">Test Suites</h1>
        <button
          onClick={() => setShowForm(true)}
          className="bg-indigo-600 text-white px-4 py-2 rounded-md hover:bg-indigo-700"
        >
          Create Test Suite
        </button>
      </div>

      {showForm && (
        <TestSuiteForm
          onClose={() => setShowForm(false)}
          onSuccess={() => setShowForm(false)}
        />
      )}

      <div className="bg-white shadow overflow-hidden sm:rounded-md">
        <ul className="divide-y divide-gray-200">
          {testSuites?.map((testSuite) => (
            <li key={testSuite.id} className="px-6 py-4">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm font-medium text-indigo-600 truncate">{testSuite.name}</p>
                  <p className="text-sm text-gray-500">
                    {testSuite.description || 'No description'} • {testSuite.test_inputs?.length || 0} test inputs
                  </p>
                </div>
                <div className="flex space-x-2">
                  <button
                    onClick={() => setEditingTestSuite(testSuite.id)}
                    className="text-indigo-600 hover:text-indigo-900"
                  >
                    Edit
                  </button>
                  <button
                    onClick={() => handleDelete(testSuite.id)}
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

      {editingTestSuite && (
        <TestSuiteForm
          testSuiteId={editingTestSuite}
          onClose={() => setEditingTestSuite(null)}
          onSuccess={() => setEditingTestSuite(null)}
        />
      )}
    </div>
  );
};

export default TestSuitesPage;