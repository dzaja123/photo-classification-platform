import React, { useState, useEffect } from 'react';
import Layout from '../../components/Layout';
import { adminAPI, appAPI } from '../../lib/api';

export default function AdminSubmissions() {
  const [submissions, setSubmissions] = useState([]);
  const [loading, setLoading] = useState(true);
  const [filters, setFilters] = useState({
    age_min: '',
    age_max: '',
    gender: '',
    country: '',
  });

  useEffect(() => {
    fetchSubmissions();
  }, []);

  const fetchSubmissions = async () => {
    try {
      const params = Object.fromEntries(
        Object.entries(filters).filter(([_, v]) => v !== '')
      );
      const response = await adminAPI.getSubmissions(params);
      setSubmissions(response.data.submissions || []);
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  const handleFilterChange = (e) => {
    setFilters({
      ...filters,
      [e.target.name]: e.target.value,
    });
  };

  const handleApplyFilters = () => {
    setLoading(true);
    fetchSubmissions();
  };

  const handleExportCSV = async () => {
    try {
      const params = Object.fromEntries(
        Object.entries(filters).filter(([_, v]) => v !== '')
      );
      const response = await adminAPI.exportCSV(params);
      const url = window.URL.createObjectURL(new Blob([response.data]));
      const link = document.createElement('a');
      link.href = url;
      link.setAttribute('download', `submissions_${Date.now()}.csv`);
      document.body.appendChild(link);
      link.click();
      link.remove();
    } catch (err) {
      console.error('CSV export failed:', err);
    }
  };

  const handleExportJSON = async () => {
    try {
      const params = Object.fromEntries(
        Object.entries(filters).filter(([_, v]) => v !== '')
      );
      const response = await adminAPI.exportJSON(params);
      const url = window.URL.createObjectURL(new Blob([response.data]));
      const link = document.createElement('a');
      link.href = url;
      link.setAttribute('download', `submissions_${Date.now()}.json`);
      document.body.appendChild(link);
      link.click();
      link.remove();
    } catch (err) {
      console.error('JSON export failed:', err);
    }
  };

  return (
    <Layout>
      <div className="space-y-6">
        <div className="flex justify-between items-center">
          <h1 className="text-3xl font-bold text-gray-900">All Submissions</h1>
          <div className="flex gap-2">
            <button onClick={handleExportCSV} className="btn-primary">
              Export CSV
            </button>
            <button onClick={handleExportJSON} className="px-4 py-2 bg-gray-600 text-white rounded-lg hover:bg-gray-700 transition-colors">
              Export JSON
            </button>
          </div>
        </div>

        {/* Filters */}
        <div className="card">
          <h3 className="font-semibold mb-4">Filters</h3>
          <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
            <input
              type="number"
              name="age_min"
              placeholder="Min Age"
              className="input-field"
              value={filters.age_min}
              onChange={handleFilterChange}
            />
            <input
              type="number"
              name="age_max"
              placeholder="Max Age"
              className="input-field"
              value={filters.age_max}
              onChange={handleFilterChange}
            />
            <select
              name="gender"
              className="input-field"
              value={filters.gender}
              onChange={handleFilterChange}
            >
              <option value="">All Genders</option>
              <option value="Male">Male</option>
              <option value="Female">Female</option>
              <option value="Other">Other</option>
            </select>
            <input
              type="text"
              name="country"
              placeholder="Country"
              className="input-field"
              value={filters.country}
              onChange={handleFilterChange}
            />
          </div>
          <button onClick={handleApplyFilters} className="btn-primary mt-4">
            Apply Filters
          </button>
        </div>

        {/* Submissions Table */}
        {loading ? (
          <div className="text-center py-12">Loading...</div>
        ) : (
          <div className="card overflow-x-auto">
            <table className="min-w-full divide-y divide-gray-200">
              <thead className="bg-gray-50">
                <tr>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Photo</th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Name</th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Age</th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Gender</th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Location</th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Status</th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Classification</th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Submitted</th>
                </tr>
              </thead>
              <tbody className="bg-white divide-y divide-gray-200">
                {submissions.map((sub) => (
                  <tr key={sub.id}>
                    <td className="px-6 py-4 whitespace-nowrap text-sm">
                      <div className="flex items-center">
                        <img
                          src={appAPI.getPhotoUrl(sub.id)}
                          alt={sub.photo_filename}
                          className="h-10 w-10 flex-shrink-0 rounded object-cover bg-gray-200"
                          onError={(e) => { e.target.style.display = 'none'; e.target.nextSibling.style.display = 'flex'; }}
                        />
                        <div className="h-10 w-10 flex-shrink-0 bg-gray-200 rounded items-center justify-center" style={{ display: 'none' }}>
                          <svg className="h-6 w-6 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M4 16l4.586-4.586a2 2 0 012.828 0L16 16m-2-2l1.586-1.586a2 2 0 012.828 0L20 14m-6-6h.01M6 20h12a2 2 0 002-2V6a2 2 0 00-2-2H6a2 2 0 00-2 2v12a2 2 0 002 2z" />
                          </svg>
                        </div>
                        <div className="ml-2 text-xs text-gray-500">{sub.photo_filename}</div>
                      </div>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm font-medium">{sub.name}</td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm">{sub.age}</td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm">{sub.gender}</td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm">{sub.location}, {sub.country}</td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm">
                      <span className={`px-2 py-1 text-xs rounded-full ${
                        sub.classification_status === 'completed' ? 'bg-green-100 text-green-800' :
                        sub.classification_status === 'processing' ? 'bg-blue-100 text-blue-800' :
                        sub.classification_status === 'failed' ? 'bg-red-100 text-red-800' :
                        'bg-yellow-100 text-yellow-800'
                      }`}>
                        {sub.classification_status}
                      </span>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm">
                      {sub.classification_results?.[0]?.class || '-'}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                      <div>{new Date(sub.created_at).toLocaleDateString()}</div>
                      <div className="text-xs">{new Date(sub.created_at).toLocaleTimeString()}</div>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>
    </Layout>
  );
}
