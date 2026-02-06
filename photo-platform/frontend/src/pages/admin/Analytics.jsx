import React, { useState, useEffect } from 'react';
import Layout from '../../components/Layout';
import { adminAPI } from '../../lib/api';

export default function AdminAnalytics() {
  const [analytics, setAnalytics] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchAnalytics();
  }, []);

  const fetchAnalytics = async () => {
    try {
      const response = await adminAPI.getAnalytics();
      setAnalytics(response.data);
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return (
      <Layout>
        <div className="text-center py-12">Loading...</div>
      </Layout>
    );
  }

  return (
    <Layout>
      <div className="space-y-6">
        <h1 className="text-3xl font-bold text-gray-900">Analytics Dashboard</h1>

        {/* Stats Cards */}
        <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
          <div className="card">
            <h3 className="text-sm font-medium text-gray-500">Total Submissions</h3>
            <p className="text-3xl font-bold text-primary-600 mt-2">{analytics?.total_submissions || 0}</p>
          </div>
          <div className="card">
            <h3 className="text-sm font-medium text-gray-500">Total Users</h3>
            <p className="text-3xl font-bold text-primary-600 mt-2">{analytics?.total_users || 0}</p>
          </div>
          <div className="card">
            <h3 className="text-sm font-medium text-gray-500">Today</h3>
            <p className="text-3xl font-bold text-primary-600 mt-2">{analytics?.submissions_today || 0}</p>
          </div>
          <div className="card">
            <h3 className="text-sm font-medium text-gray-500">This Week</h3>
            <p className="text-3xl font-bold text-primary-600 mt-2">{analytics?.submissions_this_week || 0}</p>
          </div>
        </div>

        {/* Gender Distribution */}
        <div className="card">
          <h3 className="text-lg font-semibold mb-4">Gender Distribution</h3>
          <div className="space-y-2">
            {Object.entries(analytics?.by_gender || {}).map(([gender, count]) => (
              <div key={gender} className="flex items-center">
                <span className="w-24 text-sm text-gray-600">{gender}</span>
                <div className="flex-1 bg-gray-200 rounded-full h-6 ml-4">
                  <div
                    className="bg-primary-600 h-6 rounded-full flex items-center justify-end pr-2"
                    style={{ width: `${(count / analytics.total_submissions) * 100}%` }}
                  >
                    <span className="text-xs text-white font-medium">{count}</span>
                  </div>
                </div>
              </div>
            ))}
          </div>
        </div>

        {/* Country Distribution */}
        <div className="card">
          <h3 className="text-lg font-semibold mb-4">Top Countries</h3>
          <div className="space-y-2">
            {Object.entries(analytics?.by_country || {}).slice(0, 10).map(([country, count]) => (
              <div key={country} className="flex justify-between items-center">
                <span className="text-sm text-gray-600">{country}</span>
                <span className="font-medium text-primary-600">{count}</span>
              </div>
            ))}
          </div>
        </div>

        {/* Age Distribution */}
        <div className="card">
          <h3 className="text-lg font-semibold mb-4">Age Distribution</h3>
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
            {analytics?.age_distribution?.map((group) => (
              <div key={group.range} className="text-center p-4 bg-gray-50 rounded-lg">
                <p className="text-sm text-gray-600">{group.range}</p>
                <p className="text-2xl font-bold text-primary-600 mt-1">{group.count}</p>
              </div>
            ))}
          </div>
        </div>
      </div>
    </Layout>
  );
}
