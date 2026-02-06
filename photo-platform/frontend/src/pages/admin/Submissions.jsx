import React, { useState, useEffect } from 'react';
import Layout from '../../components/Layout';
import { adminAPI } from '../../lib/api';

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
      const response = await adminAPI.exportCSV(filters);
      const url = window.URL.createObjectURL(new Blob([response.data]));
      const link = document.createElement('a');
      link.href = url;
      link.setAttribute('download', `submissions_${Date.now()}.csv`);
      document.body.appendChild(link);
      link.click();
      link.remove();
    } catch (err) {
      console.error('Export failed:', err);
    }
  };

  return (
    <Layout>
      <div className="space-y-6">
        <div className="flex justify-between items-center">
          <h1 className="text-3xl font-bold text-gray-900">All Submissions</h1>
          <button onClick={handleExportCSV} className="btn-primary">
            Export CSV
          </button>
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
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Name</th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Age</th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Gender</th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Location</th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Status</th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Classification</th>
                </tr>
              </thead>
              <tbody className="bg-white divide-y divide-gray-200">
                {submissions.map((sub) => (
                  <tr key={sub.id}>
                    <td className="px-6 py-4 whitespace-nowrap text-sm">{sub.name}</td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm">{sub.age}</td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm">{sub.gender}</td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm">{sub.location}, {sub.country}</td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm">{sub.classification_status}</td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm">
                      {sub.classification_results?.[0]?.class || '-'}
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
