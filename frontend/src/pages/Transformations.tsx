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
  canonical_id?: number;
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
  const [rawFieldSearch, setRawFieldSearch] = useState('');
  const [showRawFieldDropdown, setShowRawFieldDropdown] = useState(false);
  const [isActivelySearching, setIsActivelySearching] = useState(false);
  const [isLoading, setIsLoading] = useState(true);
  const [searchTerm, setSearchTerm] = useState('');
  const [selectedCategory, setSelectedCategory] = useState<string>('all');
  const [mappingFilter, setMappingFilter] = useState<string>('all'); // 'all', 'mapped', 'unmapped'
  const [providerMappings, setProviderMappings] = useState<FieldMapping[]>([]);


  // Filter fields based on search, category, and mapping status
  const filteredFields = canonicalFields.filter(field => {
    const matchesSearch = field.display_name.toLowerCase().includes(searchTerm.toLowerCase()) ||
                         field.name.toLowerCase().includes(searchTerm.toLowerCase());
    const matchesCategory = selectedCategory === 'all' || field.category === selectedCategory;
    
    // Check mapping status if filter is applied
    if (mappingFilter !== 'all' && selectedProvider) {
      const hasMapping = providerMappings.some(mapping => mapping.canonical_id === field.id);
      const matchesMapping = mappingFilter === 'mapped' ? hasMapping : !hasMapping;
      return matchesSearch && matchesCategory && matchesMapping;
    }
    
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

  // Sync rawFieldSearch with currentMapping
  useEffect(() => {
    if (currentMapping?.raw_field_name) {
      setRawFieldSearch(currentMapping.raw_field_name);
      setIsActivelySearching(false); // Reset searching state when loading a mapping
    } else {
      setRawFieldSearch('');
      setIsActivelySearching(false);
    }
  }, [currentMapping]);

  useEffect(() => {
    if (selectedProvider) {
      loadAvailableRawFields(selectedProvider);
      loadProviderMappings(selectedProvider);
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

  const loadProviderMappings = async (providerId: number) => {
    try {
      const token = localStorage.getItem('token');
      const response = await fetch(`/api/transform/mappings?provider_id=${providerId}`, {
        headers: {
          'Authorization': `Bearer ${token}`,
        },
      });
      if (response.ok) {
        const data = await response.json();
        setProviderMappings(data);
      }
    } catch (error) {
      console.error('Error loading provider mappings:', error);
      setProviderMappings([]);
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
      } else {
        // If no mapping exists, initialize empty mapping
        setCurrentMapping({
          raw_field_name: '',
          transform_expression: null
        });
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
        // Refresh provider mappings to update the filtering
        if (selectedProvider) {
          loadProviderMappings(selectedProvider);
        }
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

  const deleteMapping = async (mappingId: string) => {
    try {
      const token = localStorage.getItem('token');
      const response = await fetch(`/api/transform/mappings/${mappingId}`, {
        method: 'DELETE',
        headers: {
          'Authorization': `Bearer ${token}`,
        },
      });

      if (response.ok) {
        // Refresh provider mappings
        if (selectedProvider) {
          loadProviderMappings(selectedProvider);
        }
        // Clear current mapping if it was the one being deleted
        if (currentMapping?.id === mappingId) {
          setCurrentMapping(null);
          setRawFieldSearch('');
        }
        // If we have selectedField and selectedProvider, reload the field mapping
        if (selectedField && selectedProvider) {
          loadFieldMapping(selectedProvider, selectedField.id);
        }
      }
    } catch (error) {
      console.error('Error deleting mapping:', error);
    }
  };

  if (isLoading) {
    return (
      <div className="flex justify-center items-center h-64">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 dark:border-blue-400"></div>
      </div>
    );
  }

  return (
    <div className="flex h-screen bg-gray-100 dark:bg-gray-900 transition-colors">
      {/* Left Panel - Canonical Fields */}
      <div className="w-1/2 bg-white dark:bg-gray-800 shadow-lg flex flex-col border-r-2 border-gray-300 dark:border-gray-600 transition-colors">
        <div className="p-4 border-b border-gray-200 dark:border-gray-600 bg-white dark:bg-gray-800 transition-colors">
          <h1 className="text-xl font-bold text-gray-900 dark:text-white transition-colors">Canonical Fields</h1>
          
          {/* Search and Filter */}
          <div className="mt-4 space-y-2">
            <input
              type="text"
              placeholder="Search fields..."
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-700 text-gray-900 dark:text-white rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 transition-colors"
            />
            
            <select
              value={selectedCategory}
              onChange={(e) => setSelectedCategory(e.target.value)}
              className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-700 text-gray-900 dark:text-white rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 transition-colors"
            >
              {categories.map(category => (
                <option key={category} value={category}>
                  {category === 'all' ? 'All Categories' : category.charAt(0).toUpperCase() + category.slice(1)}
                </option>
              ))}
            </select>
            
            <select
              value={mappingFilter}
              onChange={(e) => setMappingFilter(e.target.value)}
              className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-700 text-gray-900 dark:text-white rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 transition-colors"
              disabled={!selectedProvider}
            >
              <option value="all">All Fields</option>
              <option value="mapped">Fields with Mappings</option>
              <option value="unmapped">Fields without Mappings</option>
            </select>
          </div>
        </div>

        {/* Fields List - Scrollable */}
        <div className="flex-1 overflow-y-auto bg-white dark:bg-gray-800 transition-colors">
          {filteredFields.map((field) => (
            <div
              key={field.id}
              onClick={() => setSelectedField(field)}
              className={`p-4 border-b border-gray-100 dark:border-gray-700 cursor-pointer hover:bg-gray-50 dark:hover:bg-gray-700 transition-colors ${
                selectedField?.id === field.id ? 'bg-blue-50 dark:bg-blue-900/20 border-l-4 border-l-blue-500' : ''
              }`}
            >
              <div className="flex justify-between items-start">
                <div>
                  <div className="flex items-center space-x-2 mb-1">
                    <h3 className="font-medium text-gray-900 dark:text-white transition-colors">{field.display_name}</h3>
                    {selectedProvider && providerMappings.some(mapping => mapping.canonical_id === field.id) && (
                      <span className="inline-flex px-2 py-1 text-xs rounded-full bg-green-100 text-green-800">
                        Mapped
                      </span>
                    )}
                  </div>
                  <p className="text-sm text-gray-500 dark:text-gray-400 transition-colors">{field.name}</p>
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
                <span className="text-xs text-gray-400 dark:text-gray-500 transition-colors">#{field.code}</span>
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* Right Panel - Field Mapping */}
      <div className="w-1/2 bg-gray-50 dark:bg-gray-900 flex flex-col transition-colors">
        <div className="p-4 border-b border-gray-200 dark:border-gray-600 flex justify-between items-center bg-white dark:bg-gray-800 shadow-sm transition-colors">
          <h2 className="text-xl font-bold text-gray-900 dark:text-white transition-colors">Field Mapping</h2>
          <div className="flex space-x-2">
            <button
              onClick={downloadBackup}
              disabled={!selectedProvider}
              className="px-3 py-2 text-sm font-medium text-gray-700 dark:text-gray-300 bg-gray-100 dark:bg-gray-700 border border-gray-300 dark:border-gray-600 rounded-md hover:bg-gray-200 dark:hover:bg-gray-600 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
            >
              Download Backup
            </button>
            {currentMapping && currentMapping.id && (
              <button
                onClick={() => {
                  if (currentMapping.id && window.confirm('Are you sure you want to delete this mapping?')) {
                    deleteMapping(currentMapping.id);
                  }
                }}
                className="px-3 py-2 text-sm font-medium text-white bg-red-600 border border-transparent rounded-md hover:bg-red-700 transition-colors"
              >
                Delete Mapping
              </button>
            )}
            {currentMapping && (
              <button
                onClick={() => {
                  setCurrentMapping(null);
                  setSelectedField(null);
                }}
                className="px-3 py-2 text-sm font-medium text-gray-700 dark:text-gray-300 bg-gray-100 dark:bg-gray-700 border border-gray-300 dark:border-gray-600 rounded-md hover:bg-gray-200 dark:hover:bg-gray-600 transition-colors"
              >
                Clear
              </button>
            )}
            <button
              onClick={saveMapping}
              disabled={!selectedField || !currentMapping?.raw_field_name}
              className="px-3 py-2 text-sm font-medium text-white bg-blue-600 border border-transparent rounded-md hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed"
            >
              Save Mapping
            </button>
          </div>
        </div>

        <div className="flex-1 overflow-y-auto p-4 space-y-6 bg-white dark:bg-gray-800 transition-colors">
          {/* Provider Selection */}
          <div>
            <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2 transition-colors">
              Data Provider
            </label>
            <select
              value={selectedProvider || ''}
              onChange={(e) => setSelectedProvider(Number(e.target.value))}
              className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-700 text-gray-900 dark:text-white rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 transition-colors"
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
            <div className="bg-gray-50 dark:bg-gray-700 p-4 rounded-lg transition-colors">
              <h3 className="font-medium text-gray-900 dark:text-white mb-2 transition-colors dark:!text-white">Selected Field</h3>
              <div className="space-y-1 text-sm">
                <p className="text-gray-900 dark:text-white"><strong>Name:</strong> {selectedField.display_name}</p>
                <p className="text-gray-900 dark:text-white"><strong>Code:</strong> {selectedField.code}</p>
                <p className="text-gray-900 dark:text-white"><strong>Type:</strong> {selectedField.type}</p>
                <p className="text-gray-900 dark:text-white"><strong>Category:</strong> {selectedField.category}</p>
              </div>
              
              {/* Show existing mapping status */}
              {selectedProvider && (
                <div className="mt-3 pt-3 border-t border-gray-300 dark:border-gray-600">
                  {(() => {
                    const existingMapping = providerMappings.find(m => m.canonical_id === selectedField.id);
                    return existingMapping ? (
                      <div className="text-sm">
                        <p className="text-green-600 dark:text-green-400 font-medium mb-1">✓ Field Already Mapped</p>
                        <p className="text-gray-900 dark:text-white"><strong>Raw Field:</strong> {existingMapping.raw_field_name}</p>
                        {existingMapping.transform_expression && (
                          <p className="text-gray-900 dark:text-white"><strong>Has Formula:</strong> Yes</p>
                        )}
                      </div>
                    ) : (
                      <p className="text-orange-600 dark:text-orange-400 text-sm font-medium">⚠️ No mapping exists for this field</p>
                    );
                  })()}
                </div>
              )}
            </div>
          )}

          {/* Mapping Configuration */}
          {selectedField && selectedProvider && (
            <div>
              <h3 className="font-medium text-gray-900 dark:text-white mb-4 transition-colors">Field Mapping Configuration</h3>
              
              <div className="space-y-4">
                <div className="relative">
                  <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2 transition-colors">
                    Raw Field Name (from provider data)
                  </label>
                  <div className="relative">
                    <input
                      type="text"
                      value={rawFieldSearch}
                      onChange={(e) => {
                        const newValue = e.target.value;
                        setRawFieldSearch(newValue);
                        setShowRawFieldDropdown(true);
                        setIsActivelySearching(true);
                        // Update currentMapping to reflect the new raw field name while preserving other fields
                        setCurrentMapping(prev => ({
                          raw_field_name: newValue,
                          transform_expression: prev?.transform_expression,
                          id: prev?.id,
                          company_id: prev?.company_id,
                          start_date: prev?.start_date,
                          end_date: prev?.end_date
                        }));
                      }}
                      onFocus={() => setShowRawFieldDropdown(true)}
                      onBlur={(e) => {
                        // Don't close dropdown immediately if clicking on dropdown item
                        setTimeout(() => {
                          if (!e.relatedTarget?.closest('.raw-field-dropdown')) {
                            setShowRawFieldDropdown(false);
                          }
                        }, 150);
                      }}
                      placeholder="Search and select from available fields..."
                      className="w-full px-3 py-2 pr-10 border border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-700 text-gray-900 dark:text-white rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 transition-colors"
                    />
                    <button
                      type="button"
                      onClick={() => {
                        const isOpening = !showRawFieldDropdown;
                        setShowRawFieldDropdown(isOpening);
                        if (isOpening) {
                          // When opening dropdown, clear search to show all options
                          setRawFieldSearch('');
                          setIsActivelySearching(false);
                        }
                      }}
                      className="absolute inset-y-0 right-0 flex items-center pr-3 text-gray-400 hover:text-gray-600 dark:hover:text-gray-300"
                    >
                      <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 9l-7 7-7-7" />
                      </svg>
                    </button>
                  </div>
                  
                  {/* Display current selection */}
                  {currentMapping?.raw_field_name && (
                    <div className="mt-2 px-3 py-2 bg-blue-50 dark:bg-blue-900/20 border border-blue-200 dark:border-blue-700 rounded-md">
                      <p className="text-sm text-blue-800 dark:text-blue-200">
                        <strong>Selected:</strong> {currentMapping.raw_field_name}
                      </p>
                      {/* Show if this field is already mapped */}
                      {selectedProvider && providerMappings.find(m => m.raw_field_name === currentMapping.raw_field_name && m.canonical_id !== selectedField?.id) && (
                        <p className="text-xs text-orange-600 dark:text-orange-400 mt-1">
                          ⚠️ This raw field is already mapped to another canonical field
                        </p>
                      )}
                    </div>
                  )}
                  
                  {/* Dropdown with available fields */}
                  {showRawFieldDropdown && availableRawFields.length > 0 && (
                    <div className="raw-field-dropdown absolute z-10 w-full mt-1 bg-white dark:bg-gray-700 border border-gray-300 dark:border-gray-600 rounded-md shadow-lg max-h-60 overflow-y-auto">
                      {availableRawFields
                        .filter(field => {
                          // If not actively searching, show all fields
                          if (!isActivelySearching) return true;
                          // If actively searching, filter by search term
                          return field.toLowerCase().includes(rawFieldSearch.toLowerCase());
                        })
                        .map(fieldName => {
                          const hasMapping = providerMappings.some(mapping => mapping.raw_field_name === fieldName);
                          const isMappedToDifferentField = hasMapping && !providerMappings.some(mapping => 
                            mapping.raw_field_name === fieldName && mapping.canonical_id === selectedField?.id
                          );
                          return (
                            <div
                              key={fieldName}
                              onClick={() => {
                                setRawFieldSearch(fieldName);
                                setIsActivelySearching(false);
                                setCurrentMapping(prev => ({
                                  raw_field_name: fieldName,
                                  transform_expression: prev?.transform_expression,
                                  id: prev?.id,
                                  company_id: prev?.company_id,
                                  start_date: prev?.start_date,
                                  end_date: prev?.end_date
                                }));
                                setShowRawFieldDropdown(false);
                              }}
                              className={`px-3 py-2 cursor-pointer hover:bg-gray-50 dark:hover:bg-gray-600 border-b border-gray-100 dark:border-gray-600 last:border-b-0 ${
                                hasMapping ? 'bg-green-50 dark:bg-green-900/20' : ''
                              }`}
                            >
                              <div className="flex items-center justify-between">
                                <span className={`text-sm font-mono ${
                                  isMappedToDifferentField 
                                    ? 'text-orange-600 dark:text-orange-400' 
                                    : hasMapping 
                                      ? 'text-green-700 dark:text-green-300'
                                      : 'text-gray-900 dark:text-white'
                                }`}>
                                  {fieldName}
                                </span>
                                <div className="flex items-center space-x-1">
                                  {hasMapping && (
                                    <span className="text-xs px-2 py-1 rounded-full bg-green-100 text-green-800">
                                      {isMappedToDifferentField ? 'Mapped elsewhere' : 'Mapped here'}
                                    </span>
                                  )}
                                </div>
                              </div>
                              {isMappedToDifferentField && (
                                <p className="text-xs text-orange-600 dark:text-orange-400 mt-1">
                                  Already mapped to another canonical field
                                </p>
                              )}
                            </div>
                          );
                        })}
                      {availableRawFields.filter(field => {
                        if (!isActivelySearching) return true;
                        return field.toLowerCase().includes(rawFieldSearch.toLowerCase());
                      }).length === 0 && (
                        <div className="px-3 py-2 text-sm text-gray-500 dark:text-gray-400">
                          {isActivelySearching ? 'No fields match your search' : 'No raw fields available'}
                        </div>
                      )}
                    </div>
                  )}
                  
                  {/* Click outside to close dropdown */}
                  {showRawFieldDropdown && (
                    <div 
                      className="fixed inset-0 z-5" 
                      onClick={() => setShowRawFieldDropdown(false)}
                    />
                  )}
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2 transition-colors">
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
                    className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-700 text-gray-900 dark:text-white rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 font-mono text-sm transition-colors"
                  />
                  <p className="mt-2 text-xs text-gray-500 dark:text-gray-400 transition-colors">
                    Leave empty for direct mapping. Use JSON expressions for transformations.
                  </p>
                </div>
              </div>
            </div>
          )}

          {/* Existing Mappings Overview */}
          {selectedProvider && providerMappings.length > 0 && (
            <div className="mt-6">
              <h3 className="font-medium text-gray-900 dark:text-white mb-3 transition-colors">Existing Field Mappings ({providerMappings.length})</h3>
              <div className="bg-blue-50 dark:bg-blue-900/20 p-4 rounded-lg max-h-64 overflow-y-auto transition-colors">
                <div className="space-y-2">
                  {providerMappings.map(mapping => {
                    const canonicalField = canonicalFields.find(field => field.id === mapping.canonical_id);
                    return (
                      <button
                        key={mapping.id || `${mapping.raw_field_name}-${mapping.canonical_id}`}
                        onClick={() => {
                          // Auto-select the canonical field and load the mapping
                          if (canonicalField) {
                            setSelectedField(canonicalField);
                            setCurrentMapping({
                              id: mapping.id,
                              raw_field_name: mapping.raw_field_name,
                              transform_expression: mapping.transform_expression,
                              company_id: mapping.company_id,
                              start_date: mapping.start_date,
                              end_date: mapping.end_date
                            });
                          }
                        }}
                        className="w-full text-left p-3 bg-white dark:bg-gray-800 border border-blue-200 dark:border-blue-700 rounded-lg hover:bg-blue-50 dark:hover:bg-blue-900/20 hover:border-blue-300 dark:hover:border-blue-600 transition-colors group"
                      >
                        <div className="flex items-center justify-between">
                          <div className="flex-1">
                            <div className="text-sm font-medium text-gray-900 dark:text-white transition-colors">
                              {mapping.raw_field_name}
                            </div>
                            <div className="text-xs text-gray-500 dark:text-gray-400 transition-colors">
                              → {canonicalField?.display_name || canonicalField?.name || 'Unknown Field'}
                            </div>
                            {canonicalField?.category && (
                              <span className={`inline-flex px-2 py-1 text-xs rounded-full mt-1 ${
                                canonicalField.category === 'fundamental' ? 'bg-green-100 text-green-800' :
                                canonicalField.category === 'market' ? 'bg-blue-100 text-blue-800' :
                                'bg-purple-100 text-purple-800'
                              }`}>
                                {canonicalField.category}
                              </span>
                            )}
                          </div>
                          <div className="ml-2 flex items-center space-x-2">
                            {mapping.transform_expression ? (
                              <span className="inline-flex px-2 py-1 text-xs rounded-full bg-yellow-100 text-yellow-800">
                                Formula
                              </span>
                            ) : (
                              <span className="inline-flex px-2 py-1 text-xs rounded-full bg-gray-100 text-gray-800">
                                Direct
                              </span>
                            )}
                            {mapping.id && (
                              <button
                                onClick={(e) => {
                                  e.stopPropagation();
                                  if (mapping.id) {
                                    deleteMapping(mapping.id);
                                  }
                                }}
                                className="opacity-0 group-hover:opacity-100 p-1 text-red-500 hover:text-red-700 hover:bg-red-50 rounded transition-all"
                                title="Delete mapping"
                              >
                                <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" />
                                </svg>
                              </button>
                            )}
                          </div>
                        </div>
                      </button>
                    );
                  })}
                </div>
              </div>
            </div>
          )}

          {/* Available Raw Fields Helper */}
          {selectedProvider && availableRawFields.length > 0 && (
            <div className="mt-6">
              <h3 className="font-medium text-gray-900 dark:text-white mb-3 transition-colors">Available Raw Fields from Provider</h3>
              <div className="bg-gray-50 dark:bg-gray-700 p-4 rounded-lg max-h-48 overflow-y-auto transition-colors">
                <div className="grid grid-cols-2 gap-2">
                  {availableRawFields.map(fieldName => {
                    const hasMapping = providerMappings.some(mapping => mapping.raw_field_name === fieldName);
                    return (
                      <button
                        key={fieldName}
                        onClick={() => {
                          // Set the raw field name in the mapping
                          setCurrentMapping(prev => ({
                            raw_field_name: fieldName,
                            transform_expression: prev?.transform_expression,
                            id: prev?.id,
                            company_id: prev?.company_id,
                            start_date: prev?.start_date,
                            end_date: prev?.end_date
                          }));
                          
                          // Auto-select matching canonical field if there's a mapping
                          if (selectedProvider) {
                            const matchingMapping = providerMappings.find(mapping => mapping.raw_field_name === fieldName);
                            if (matchingMapping) {
                              const matchingField = canonicalFields.find(field => field.id === matchingMapping.canonical_id);
                              if (matchingField) {
                                setSelectedField(matchingField);
                              }
                            }
                          }
                        }}
                        className={`text-left text-xs px-2 py-1 rounded border font-mono transition-colors ${
                          hasMapping 
                            ? 'bg-green-50 dark:bg-green-900/20 border-green-300 dark:border-green-700 text-green-700 dark:text-green-300 hover:bg-green-100 dark:hover:bg-green-900/30' 
                            : 'bg-white dark:bg-gray-800 border-gray-300 dark:border-gray-600 text-gray-700 dark:text-gray-300 hover:bg-blue-50 dark:hover:bg-blue-900/20 hover:border-blue-300 dark:hover:border-blue-600'
                        }`}
                        title={hasMapping ? "This field has a mapping - click to view" : "Click to use this field name"}
                      >
                        <span className="flex items-center justify-between">
                          {fieldName}
                          {hasMapping && <span className="ml-1 text-green-600">✓</span>}
                        </span>
                      </button>
                    );
                  })}
                </div>
                <p className="text-xs text-gray-500 dark:text-gray-400 mt-2 transition-colors">
                  Click any field name to use it in your mapping. Green fields already have mappings.
                </p>
              </div>
            </div>
          )}

          {/* No Mappings State */}
          {selectedProvider && providerMappings.length === 0 && (
            <div className="mt-6">
              <div className="text-center py-8 text-gray-500 dark:text-gray-400 bg-gray-50 dark:bg-gray-700 rounded-lg transition-colors">
                <svg className="mx-auto h-8 w-8 text-gray-400 dark:text-gray-500 mb-2 transition-colors" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
                </svg>
                <p className="font-medium">No field mappings found</p>
                <p className="text-sm">Select a canonical field and create your first mapping</p>
              </div>
            </div>
          )}

          {/* No Selection State */}
          {!selectedField && (
            <div className="text-center py-12 text-gray-500 dark:text-gray-400 transition-colors">
              <svg className="mx-auto h-12 w-12 text-gray-400 dark:text-gray-500 mb-4 transition-colors" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
              </svg>
              <p className="font-medium">Select a canonical field</p>
              <p className="text-sm">Choose a field from the left panel to configure its mapping</p>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

export default Transformations;