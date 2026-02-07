import React, { useState, useEffect, useCallback } from 'react';
import { Link } from 'react-router-dom';
import Layout from '../../components/Layout';
import { appAPI } from '../../lib/api';

export default function Dashboard() {
  const [submissions, setSubmissions] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [deletingId, setDeletingId] = useState(null);

  const fetchSubmissions = useCallback(async () => {
    setError('');
    try {
      const response = await appAPI.getSubmissions();
      setSubmissions(response.data.submissions || []);
    } catch (err) {
      setError('Failed to load submissions. Please try again.');
      console.error(err);
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    fetchSubmissions();
  }, [fetchSubmissions]);

  const handleDelete = async (id) => {
    if (!window.confirm('Are you sure you want to delete this submission?')) return;
    setDeletingId(id);
    try {
      await appAPI.deleteSubmission(id);
      setSubmissions((prev) => prev.filter((s) => s.id !== id));
    } catch (err) {
      setError('Failed to delete submission.');
      console.error(err);
    } finally {
      setDeletingId(null);
    }
  };

  const getStatusBadge = (status) => {
    const map = {
      pending: 'bg-yellow-100 text-yellow-800',
      processing: 'bg-blue-100 text-blue-800',
      completed: 'bg-green-100 text-green-800',
      failed: 'bg-red-100 text-red-800',
    };
    return map[status] || 'bg-gray-100 text-gray-800';
  };

  return (
    <Layout>
      <div className="space-y-6">
        {/* Header */}
        <div className="flex flex-col sm:flex-row sm:justify-between sm:items-center gap-4">
          <div>
            <h1 className="text-3xl font-bold text-gray-900">My Submissions</h1>
            <p className="text-gray-500 text-sm mt-1">
              {submissions.length} submission{submissions.length !== 1 ? 's' : ''}
            </p>
          </div>
          <div className="flex gap-3">
            <button onClick={fetchSubmissions} disabled={loading} className="btn-secondary text-sm">
              {loading ? 'Refreshing...' : 'Refresh'}
            </button>
            <Link to="/upload" className="btn-primary text-sm">
              Upload New Photo
            </Link>
          </div>
        </div>

        {error && (
          <div className="bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded-lg text-sm">
            {error}
          </div>
        )}

        {/* Loading skeleton */}
        {loading && submissions.length === 0 ? (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {[1, 2, 3].map((i) => (
              <div key={i} className="card animate-pulse">
                <div className="h-4 bg-gray-200 rounded w-3/4 mb-3" />
                <div className="h-3 bg-gray-200 rounded w-1/2 mb-2" />
                <div className="h-3 bg-gray-200 rounded w-2/3 mb-2" />
                <div className="h-3 bg-gray-200 rounded w-1/3" />
              </div>
            ))}
          </div>
        ) : submissions.length === 0 ? (
          /* Empty state */
          <div className="card text-center py-16">
            <svg className="mx-auto h-16 w-16 text-gray-300" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="1.5" d="M4 16l4.586-4.586a2 2 0 012.828 0L16 16m-2-2l1.586-1.586a2 2 0 012.828 0L20 14m-6-6h.01M6 20h12a2 2 0 002-2V6a2 2 0 00-2-2H6a2 2 0 00-2 2v12a2 2 0 002 2z" />
            </svg>
            <h3 className="mt-4 text-lg font-semibold text-gray-700">No submissions yet</h3>
            <p className="text-gray-400 mt-1">Upload your first photo to get ML classification results.</p>
            <Link to="/upload" className="inline-block btn-primary mt-6">Upload Photo</Link>
          </div>
        ) : (
          /* Submissions grid */
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {submissions.map((submission) => (
              <div key={submission.id} className="card hover:shadow-lg transition-shadow relative group">
                <div className="space-y-3">
                  {/* Photo thumbnail */}
                  <div className="w-full h-40 bg-gray-100 rounded-lg overflow-hidden -mt-2">
                    <img
                      src={appAPI.getPhotoUrl(submission.id)}
                      alt={submission.photo_filename}
                      className="w-full h-full object-cover"
                      onError={(e) => {
                        e.target.style.display = 'none';
                        e.target.parentElement.classList.add('flex', 'items-center', 'justify-center');
                        e.target.parentElement.innerHTML = '<svg class="h-12 w-12 text-gray-300" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5" d="M4 16l4.586-4.586a2 2 0 012.828 0L16 16m-2-2l1.586-1.586a2 2 0 012.828 0L20 14m-6-6h.01M6 20h12a2 2 0 002-2V6a2 2 0 00-2-2H6a2 2 0 00-2 2v12a2 2 0 002 2z" /></svg>';
                      }}
                    />
                  </div>

                  <div className="flex justify-between items-start">
                    <h3 className="font-semibold text-lg truncate pr-2">{submission.name}</h3>
                    <span className={`flex-shrink-0 px-2 py-1 text-xs rounded-full ${getStatusBadge(submission.classification_status)}`}>
                      {submission.classification_status}
                    </span>
                  </div>

                  <div className="text-sm text-gray-600 space-y-1">
                    <p><span className="text-gray-400">Age:</span> {submission.age} &middot; <span className="text-gray-400">Gender:</span> {submission.gender}</p>
                    <p><span className="text-gray-400">Location:</span> {submission.location}, {submission.country}</p>
                    {submission.description && (
                      <p className="text-xs text-gray-500 italic mt-2 line-clamp-2">{submission.description}</p>
                    )}
                  </div>

                  {submission.classification_results && submission.classification_results.length > 0 && (
                    <div className="pt-3 border-t border-gray-100">
                      <p className="text-xs font-medium text-gray-500 uppercase tracking-wide mb-2">Classification</p>
                      <div className="space-y-1.5">
                        {submission.classification_results.slice(0, 3).map((result, idx) => (
                          <div key={idx} className="flex items-center gap-2">
                            <div className="flex-1 bg-gray-100 rounded-full h-2">
                              <div
                                className="bg-primary-500 h-2 rounded-full"
                                style={{ width: `${(result.confidence * 100).toFixed(0)}%` }}
                              />
                            </div>
                            <span className="text-xs text-gray-600 w-28 truncate text-right">{result.class}</span>
                            <span className="text-xs font-semibold text-primary-600 w-12 text-right">
                              {(result.confidence * 100).toFixed(1)}%
                            </span>
                          </div>
                        ))}
                      </div>
                    </div>
                  )}

                  {submission.classification_status === 'failed' && submission.classification_error && (
                    <div className="pt-3 border-t border-red-100">
                      <p className="text-xs text-red-500">Error: {submission.classification_error}</p>
                    </div>
                  )}

                  <div className="flex justify-between items-center pt-3 border-t border-gray-100">
                    <span className="text-xs text-gray-400">
                      {new Date(submission.created_at).toLocaleDateString()} {new Date(submission.created_at).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
                    </span>
                    <button
                      onClick={() => handleDelete(submission.id)}
                      disabled={deletingId === submission.id}
                      className="text-xs text-red-400 hover:text-red-600 opacity-0 group-hover:opacity-100 transition-opacity disabled:opacity-50"
                    >
                      {deletingId === submission.id ? 'Deleting...' : 'Delete'}
                    </button>
                  </div>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>
    </Layout>
  );
}
