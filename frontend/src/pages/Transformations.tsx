import React, { useState, useEffect } from 'react';

interface CanonicalField {
  id: number;
  code: number;
  name: string;
  display_name: string;
  type: string;
  category: string;
  is_computed: boolean;
}

interface Provider {
  id: number;
  name: string;
  description: string;
}

interface FieldMapping {
  id?: string;
  raw_field_name: string;
  transform_expression?: any;
  company_id?: string;
  start_date?: string;
  end_date?: string;
}

const Transformations: React.FC = () => {
  const [canonicalFields, setCanonicalFields] = useState<CanonicalField[]>([]);
  const [providers, setProviders] = useState<Provider[]>([]);
  const [selectedField, setSelectedField] = useState<CanonicalField | null>(null);
  const [selectedProvider, setSelectedProvider] = useState<number | null>(null);
  const [currentMapping, setCurrentMapping] = useState<FieldMapping | null>(null);
  const [availableRawFields, setAvailableRawFields] = useState<string[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [searchTerm, setSearchTerm] = useState('');
  const [selectedCategory, setSelectedCategory] = useState<string>('all');


  // Filter fields based on search and category
  const filteredFields = canonicalFields.filter(field => {
    const matchesSearch = field.display_name.toLowerCase().includes(searchTerm.toLowerCase()) ||
                         field.name.toLowerCase().includes(searchTerm.toLowerCase());
    const matchesCategory = selectedCategory === 'all' || field.category === selectedCategory;
    return matchesSearch && matchesCategory;
  });

  const categories = ['all', ...Array.from(new Set(canonicalFields.map(f => f.category)))];

  useEffect(() => {
    loadCanonicalFields();
    loadProviders();
  }, []);

  useEffect(() => {
    if (selectedField && selectedProvider) {
      loadFieldMapping(selectedProvider, selectedField.id);
    }
  }, [selectedField, selectedProvider]);

  useEffect(() => {
    if (selectedProvider) {
      loadAvailableRawFields(selectedProvider);
    }
  }, [selectedProvider]);

  const loadCanonicalFields = async () => {
    try {
      const token = localStorage.getItem('token');
      const response = await fetch('/api/transform/canonical-fields', {
        headers: {
          'Authorization': `Bearer ${token}`,
        },
      });
      if (response.ok) {
        const data = await response.json();
        setCanonicalFields(data);
      }
    } catch (error) {
      console.error('Error loading canonical fields:', error);
    }
  };

  const loadProviders = async () => {
    try {
      const token = localStorage.getItem('token');
      const response = await fetch('/api/providers/', {
        headers: {
          'Authorization': `Bearer ${token}`,
        },
      });
      if (response.ok) {
        const data = await response.json();
        setProviders(data);
        if (data.length > 0) {
          setSelectedProvider(data[0].id);
        }
      }
    } catch (error) {
      console.error('Error loading providers:', error);
    } finally {
      setIsLoading(false);
    }
  };

  const loadAvailableRawFields = async (providerId: number) => {
    try {
      const token = localStorage.getItem('token');
      const response = await fetch(`/api/transform/providers/${providerId}/raw-fields`, {
        headers: {
          'Authorization': `Bearer ${token}`,
        },
      });
      if (response.ok) {
        const data = await response.json();
        setAvailableRawFields(data.raw_fields);
      }
    } catch (error) {
      console.error('Error loading raw fields:', error);
      setAvailableRawFields([]);
    }
  };

  const loadFieldMapping = async (providerId: number, canonicalId: number) => {
    try {
      const token = localStorage.getItem('token');
      const response = await fetch(`/api/transform/mappings/${providerId}/${canonicalId}`, {
        headers: {
          'Authorization': `Bearer ${token}`,
        },
      });
      if (response.ok) {
        const data = await response.json();
        setCurrentMapping(data);
      }
    } catch (error) {
      console.error('Error loading field mapping:', error);
    }
  };

  const saveMapping = async () => {
    if (!selectedField || !selectedProvider || !currentMapping) return;

    try {
      const token = localStorage.getItem('token');
      const mappingData = {
        provider_id: selectedProvider,
        canonical_id: selectedField.id,
        raw_field_name: currentMapping.raw_field_name,
        transform_expression: currentMapping.transform_expression
      };

      const url = currentMapping.id 
        ? `/api/transform/mappings/${currentMapping.id}`
        : '/api/transform/mappings';
      
      const method = currentMapping.id ? 'PUT' : 'POST';

      const response = await fetch(url, {
        method,
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(mappingData),
      });

      if (response.ok) {
        const updatedMapping = await response.json();
        setCurrentMapping(updatedMapping);
        // Show success message or notification
      }
    } catch (error) {
      console.error('Error saving mapping:', error);
    }
  };

  const downloadBackup = async () => {
    if (!selectedProvider) return;

    try {
      const token = localStorage.getItem('token');
      const response = await fetch(`/api/transform/backup/${selectedProvider}`, {
        headers: {
          'Authorization': `Bearer ${token}`,
        },
      });

      if (response.ok) {
        const blob = await response.blob();
        const url = window.URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = `mappings_backup_${selectedProvider}.json`;
        document.body.appendChild(a);
        a.click();
        window.URL.revokeObjectURL(url);
        document.body.removeChild(a);
      }
    } catch (error) {
      console.error('Error downloading backup:', error);
    }
  };

  if (isLoading) {
    return (
      <div className="flex justify-center items-center h-64">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
      </div>
    );
  }

  return (
    <div className="flex h-screen bg-gray-100">
      {/* Left Panel - Canonical Fields */}
      <div className="w-1/2 bg-white shadow-lg flex flex-col border-r-2 border-gray-300">
        <div className="p-4 border-b border-gray-200 bg-white">
          <h1 className="text-xl font-bold text-gray-900">Canonical Fields</h1>
          
          {/* Search and Filter */}
          <div className="mt-4 space-y-2">
            <input
              type="text"
              placeholder="Search fields..."
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
            />
            
            <select
              value={selectedCategory}
              onChange={(e) => setSelectedCategory(e.target.value)}
              className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
            >
              {categories.map(category => (
                <option key={category} value={category}>
                  {category === 'all' ? 'All Categories' : category.charAt(0).toUpperCase() + category.slice(1)}
                </option>
              ))}
            </select>
          </div>
        </div>

        {/* Fields List - Scrollable */}
        <div className="flex-1 overflow-y-auto bg-white">
          {filteredFields.map((field) => (
            <div
              key={field.id}
              onClick={() => setSelectedField(field)}
              className={`p-4 border-b border-gray-100 cursor-pointer hover:bg-gray-50 ${
                selectedField?.id === field.id ? 'bg-blue-50 border-l-4 border-l-blue-500' : ''
              }`}
            >
              <div className="flex justify-between items-start">
                <div>
                  <h3 className="font-medium text-gray-900">{field.display_name}</h3>
                  <p className="text-sm text-gray-500">{field.name}</p>
                  <div className="mt-1 flex items-center space-x-2">
                    <span className={`inline-flex px-2 py-1 text-xs rounded-full ${
                      field.category === 'fundamental' ? 'bg-green-100 text-green-800' :
                      field.category === 'market' ? 'bg-blue-100 text-blue-800' :
                      'bg-purple-100 text-purple-800'
                    }`}>
                      {field.category}
                    </span>
                    {field.is_computed && (
                      <span className="inline-flex px-2 py-1 text-xs rounded-full bg-yellow-100 text-yellow-800">
                        Computed
                      </span>
                    )}
                  </div>
                </div>
                <span className="text-xs text-gray-400">#{field.code}</span>
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* Right Panel - Field Mapping */}
      <div className="w-1/2 bg-gray-50 flex flex-col">
        <div className="p-4 border-b border-gray-200 flex justify-between items-center bg-white shadow-sm">
          <h2 className="text-xl font-bold text-gray-900">Field Mapping</h2>
          <div className="flex space-x-2">
            <button
              onClick={downloadBackup}
              disabled={!selectedProvider}
              className="px-3 py-2 text-sm font-medium text-gray-700 bg-gray-100 border border-gray-300 rounded-md hover:bg-gray-200 disabled:opacity-50 disabled:cursor-not-allowed"
            >
              Download Backup
            </button>
            <button
              onClick={saveMapping}
              disabled={!selectedField || !currentMapping?.raw_field_name}
              className="px-3 py-2 text-sm font-medium text-white bg-blue-600 border border-transparent rounded-md hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed"
            >
              Save Mapping
            </button>
          </div>
        </div>

        <div className="flex-1 overflow-y-auto p-4 space-y-6 bg-white">
          {/* Provider Selection */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Data Provider
            </label>
            <select
              value={selectedProvider || ''}
              onChange={(e) => setSelectedProvider(Number(e.target.value))}
              className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
            >
              <option value="">Select a provider...</option>
              {providers.map(provider => (
                <option key={provider.id} value={provider.id}>
                  {provider.name}
                </option>
              ))}
            </select>
          </div>

          {/* Selected Field Info */}
          {selectedField && (
            <div className="bg-gray-50 p-4 rounded-lg">
              <h3 className="font-medium text-gray-900 mb-2">Selected Field</h3>
              <div className="space-y-1 text-sm">
                <p><strong>Name:</strong> {selectedField.display_name}</p>
                <p><strong>Code:</strong> {selectedField.code}</p>
                <p><strong>Type:</strong> {selectedField.type}</p>
                <p><strong>Category:</strong> {selectedField.category}</p>
              </div>
            </div>
          )}

          {/* Mapping Configuration */}
          {selectedField && selectedProvider && (
            <div>
              <h3 className="font-medium text-gray-900 mb-4">Field Mapping Configuration</h3>
              
              <div className="space-y-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Raw Field Name (from provider data)
                  </label>
                  <input
                    type="text"
                    value={currentMapping?.raw_field_name || ''}
                    onChange={(e) => setCurrentMapping(prev => ({
                      raw_field_name: e.target.value,
                      transform_expression: prev?.transform_expression,
                      id: prev?.id,
                      company_id: prev?.company_id,
                      start_date: prev?.start_date,
                      end_date: prev?.end_date
                    }))}
                    placeholder="e.g., Total_Revenue, Cash_From_Operating"
                    className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                  />
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Transform Expression (JSON)
                  </label>
                  <textarea
                    rows={6}
                    value={currentMapping?.transform_expression ? JSON.stringify(currentMapping.transform_expression, null, 2) : ''}
                    onChange={(e) => {
                      try {
                        const parsed = e.target.value ? JSON.parse(e.target.value) : null;
                        setCurrentMapping(prev => ({
                          raw_field_name: prev?.raw_field_name || '',
                          transform_expression: parsed,
                          id: prev?.id,
                          company_id: prev?.company_id,
                          start_date: prev?.start_date,
                          end_date: prev?.end_date
                        }));
                      } catch (error) {
                        // Invalid JSON, keep the raw value for editing
                      }
                    }}
                    placeholder={`{
  "op": "multiply",
  "args": [
    {"field": "raw_field_name"},
    {"constant": 1000000}
  ]
}`}
                    className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 font-mono text-sm"
                  />
                  <p className="mt-2 text-xs text-gray-500">
                    Leave empty for direct mapping. Use JSON expressions for transformations.
                  </p>
                </div>
              </div>
            </div>
          )}

          {/* Available Raw Fields Helper */}
          {selectedProvider && availableRawFields.length > 0 && (
            <div className="mt-6">
              <h3 className="font-medium text-gray-900 mb-3">Available Raw Fields from Provider</h3>
              <div className="bg-gray-50 p-4 rounded-lg max-h-48 overflow-y-auto">
                <div className="grid grid-cols-2 gap-2">
                  {availableRawFields.map(fieldName => (
                    <button
                      key={fieldName}
                      onClick={() => setCurrentMapping(prev => ({
                        raw_field_name: fieldName,
                        transform_expression: prev?.transform_expression,
                        id: prev?.id,
                        company_id: prev?.company_id,
                        start_date: prev?.start_date,
                        end_date: prev?.end_date
                      }))}
                      className="text-left text-xs px-2 py-1 bg-white rounded border hover:bg-blue-50 hover:border-blue-300 text-gray-700 font-mono"
                      title="Click to use this field name"
                    >
                      {fieldName}
                    </button>
                  ))}
                </div>
                <p className="text-xs text-gray-500 mt-2">
                  Click any field name to use it in your mapping
                </p>
              </div>
            </div>
          )}

          {/* No Selection State */}
          {!selectedField && (
            <div className="text-center py-12 text-gray-500">
              <p>Select a canonical field from the left panel to configure its mapping</p>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

export default Transformations;