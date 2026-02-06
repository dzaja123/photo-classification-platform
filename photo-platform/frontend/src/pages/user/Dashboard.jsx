import React, { useState, useEffect } from 'react';
import Layout from '../../components/Layout';
import { appAPI } from '../../lib/api';

export default function Dashboard() {
  const [submissions, setSubmissions] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  useEffect(() => {
    fetchSubmissions();
  }, []);

  const fetchSubmissions = async () => {
    try {
      const response = await appAPI.getSubmissions();
      setSubmissions(response.data.submissions || []);
    } catch (err) {
      setError('Failed to load submissions');
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  const getStatusBadge = (status) => {
    const colors = {
      pending: 'bg-yellow-100 text-yellow-800',
      processing: 'bg-blue-100 text-blue-800',
      completed: 'bg-green-100 text-green-800',
      failed: 'bg-red-100 text-red-800',
    };
    return colors[status] || 'bg-gray-100 text-gray-800';
  };

  if (loading) {
    return (
      <Layout>
        <div className="text-center py-12">
          <div className="text-xl">Loading...</div>
        </div>
      </Layout>
    );
  }

  return (
    <Layout>
      <div className="space-y-6">
        <div className="flex justify-between items-center">
          <h1 className="text-3xl font-bold text-gray-900">My Submissions</h1>
          <a href="/upload" className="btn-primary">
            Upload New Photo
          </a>
        </div>

        {error && (
          <div className="bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded">
            {error}
          </div>
        )}

        {submissions.length === 0 ? (
          <div className="card text-center py-12">
            <p className="text-gray-500 text-lg">No submissions yet</p>
            <p className="text-gray-400 mt-2">Upload your first photo to get started!</p>
          </div>
        ) : (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {submissions.map((submission) => (
              <div key={submission.id} className="card hover:shadow-lg transition-shadow">
                <div className="space-y-3">
                  <div className="flex justify-between items-start">
                    <h3 className="font-semibold text-lg">{submission.name}</h3>
                    <span className={`px-2 py-1 text-xs rounded-full ${getStatusBadge(submission.classification_status)}`}>
                      {submission.classification_status}
                    </span>
                  </div>
                  
                  <div className="text-sm text-gray-600 space-y-1">
                    <p>Age: {submission.age}</p>
                    <p>Gender: {submission.gender}</p>
                    <p>Location: {submission.location}, {submission.country}</p>
                  </div>

                  {submission.classification_results && submission.classification_results.length > 0 && (
                    <div className="mt-4 pt-4 border-t border-gray-200">
                      <p className="text-sm font-medium text-gray-700 mb-2">Classification:</p>
                      <div className="space-y-1">
                        {submission.classification_results.slice(0, 3).map((result, idx) => (
                          <div key={idx} className="flex justify-between text-sm">
                            <span className="text-gray-600">{result.class}</span>
                            <span className="font-medium text-primary-600">
                              {(result.confidence * 100).toFixed(1)}%
                            </span>
                          </div>
                        ))}
                      </div>
                    </div>
                  )}

                  <div className="text-xs text-gray-400 mt-4">
                    Uploaded: {new Date(submission.created_at).toLocaleDateString()}
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
