import React, { useState, useEffect } from 'react';
import Layout from '../../components/Layout';
import { adminAPI } from '../../lib/api';

export default function AuditLogs() {
  const [logs, setLogs] = useState([]);
  const [loading, setLoading] = useState(true);
  const [filters, setFilters] = useState({
    event_type: '',
    user_id: '',
    page: 1,
    page_size: 50,
  });
  const [total, setTotal] = useState(0);

  useEffect(() => {
    fetchLogs();
  }, [filters]);

  const fetchLogs = async () => {
    setLoading(true);
    try {
      const params = {
        page: filters.page,
        page_size: filters.page_size,
      };
      if (filters.event_type) params.event_type = filters.event_type;
      if (filters.user_id) params.user_id = filters.user_id;

      const response = await adminAPI.getAuditLogs(params);
      console.log('Audit logs response:', response.data);
      setLogs(response.data.logs || []);
      setTotal(response.data.total || 0);
    } catch (error) {
      console.error('Failed to fetch audit logs:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleFilterChange = (e) => {
    setFilters({
      ...filters,
      [e.target.name]: e.target.value,
      page: 1, // Reset to first page on filter change
    });
  };

  const getEventBadgeColor = (eventType) => {
    if (eventType.startsWith('auth')) return 'bg-blue-100 text-blue-800';
    if (eventType.startsWith('admin')) return 'bg-purple-100 text-purple-800';
    if (eventType.startsWith('submission')) return 'bg-green-100 text-green-800';
    if (eventType.startsWith('security')) return 'bg-red-100 text-red-800';
    return 'bg-gray-100 text-gray-800';
  };

  const getStatusBadgeColor = (status) => {
    if (status === 'success') return 'bg-green-100 text-green-800';
    if (status === 'failure') return 'bg-red-100 text-red-800';
    return 'bg-yellow-100 text-yellow-800';
  };

  return (
    <Layout>
      <div className="space-y-6">
        <h1 className="text-3xl font-bold text-gray-900">Audit Logs</h1>

        {/* Filters */}
        <div className="card">
          <h3 className="font-semibold mb-4">Filters</h3>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <select
              name="event_type"
              className="input-field"
              value={filters.event_type}
              onChange={handleFilterChange}
            >
              <option value="">All Event Types</option>
              <option value="auth">Authentication</option>
              <option value="admin">Admin Actions</option>
              <option value="submission">Submissions</option>
              <option value="security">Security</option>
            </select>
            <input
              type="text"
              name="user_id"
              placeholder="User ID"
              className="input-field"
              value={filters.user_id}
              onChange={handleFilterChange}
            />
            <button onClick={fetchLogs} className="btn-primary">
              Refresh
            </button>
          </div>
        </div>

        {/* Audit Logs Table */}
        {loading ? (
          <div className="text-center py-12">Loading...</div>
        ) : logs.length === 0 ? (
          <div className="card text-center py-12">
            <p className="text-gray-500 text-lg">No audit logs found</p>
            <p className="text-gray-400 mt-2">Audit logs will appear here as users interact with the system</p>
          </div>
        ) : (
          <div className="card overflow-x-auto">
            <div className="mb-4 text-sm text-gray-600">
              Total: {total} logs
            </div>
            <table className="min-w-full divide-y divide-gray-200">
              <thead className="bg-gray-50">
                <tr>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Timestamp</th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Event Type</th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">User</th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Action</th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">IP Address</th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Status</th>
                </tr>
              </thead>
              <tbody className="bg-white divide-y divide-gray-200">
                {logs.map((log, index) => (
                  <tr key={log._id || index}>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                      <div>{new Date(log.timestamp).toLocaleDateString()}</div>
                      <div className="text-xs">{new Date(log.timestamp).toLocaleTimeString()}</div>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm">
                      <span className={`px-2 py-1 text-xs rounded-full ${getEventBadgeColor(log.event_type)}`}>
                        {log.event_type}
                      </span>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm">
                      <div className="font-medium">{log.username || 'N/A'}</div>
                      <div className="text-xs text-gray-500">{log.user_id?.substring(0, 8)}...</div>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                      {log.action}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                      {log.ip_address || 'N/A'}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm">
                      <span className={`px-2 py-1 text-xs rounded-full ${getStatusBadgeColor(log.status)}`}>
                        {log.status || 'unknown'}
                      </span>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>

            {/* Pagination */}
            {total > filters.page_size && (
              <div className="mt-4 flex justify-between items-center">
                <button
                  onClick={() => setFilters({ ...filters, page: filters.page - 1 })}
                  disabled={filters.page === 1}
                  className="btn-secondary disabled:opacity-50"
                >
                  Previous
                </button>
                <span className="text-sm text-gray-600">
                  Page {filters.page} of {Math.ceil(total / filters.page_size)}
                </span>
                <button
                  onClick={() => setFilters({ ...filters, page: filters.page + 1 })}
                  disabled={filters.page >= Math.ceil(total / filters.page_size)}
                  className="btn-secondary disabled:opacity-50"
                >
                  Next
                </button>
              </div>
            )}
          </div>
        )}
      </div>
    </Layout>
  );
}
