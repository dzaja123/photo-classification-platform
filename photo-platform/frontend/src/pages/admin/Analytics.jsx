import React, { useState, useEffect } from 'react';
import Layout from '../../components/Layout';
import { adminAPI } from '../../lib/api';

export default function AdminAnalytics() {
  const [analytics, setAnalytics] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  useEffect(() => {
    fetchAnalytics();
  }, []);

  const fetchAnalytics = async () => {
    setError('');
    try {
      const response = await adminAPI.getAnalytics();
      setAnalytics(response.data);
    } catch (err) {
      setError('Failed to load analytics data.');
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  const pct = (count) => {
    if (!analytics?.total_submissions) return 0;
    return ((count / analytics.total_submissions) * 100).toFixed(1);
  };

  if (loading) {
    return (
      <Layout>
        <div className="space-y-6">
          <h1 className="text-3xl font-bold text-gray-900">Analytics Dashboard</h1>
          <div className="grid grid-cols-1 md:grid-cols-5 gap-4">
            {[1, 2, 3, 4, 5].map((i) => (
              <div key={i} className="card animate-pulse">
                <div className="h-3 bg-gray-200 rounded w-2/3 mb-3" />
                <div className="h-8 bg-gray-200 rounded w-1/2" />
              </div>
            ))}
          </div>
        </div>
      </Layout>
    );
  }

  return (
    <Layout>
      <div className="space-y-6">
        <div className="flex justify-between items-center">
          <h1 className="text-3xl font-bold text-gray-900">Analytics Dashboard</h1>
          <button onClick={fetchAnalytics} className="btn-secondary text-sm">Refresh</button>
        </div>

        {error && (
          <div className="bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded-lg text-sm">{error}</div>
        )}

        {/* KPI Cards */}
        <div className="grid grid-cols-2 md:grid-cols-5 gap-4">
          <div className="card">
            <p className="text-xs font-medium text-gray-400 uppercase tracking-wide">Total</p>
            <p className="text-3xl font-bold text-gray-900 mt-1">{analytics?.total_submissions ?? 0}</p>
          </div>
          <div className="card">
            <p className="text-xs font-medium text-gray-400 uppercase tracking-wide">Users</p>
            <p className="text-3xl font-bold text-gray-900 mt-1">{analytics?.total_users ?? 0}</p>
          </div>
          <div className="card">
            <p className="text-xs font-medium text-gray-400 uppercase tracking-wide">Today</p>
            <p className="text-3xl font-bold text-primary-600 mt-1">{analytics?.submissions_today ?? 0}</p>
          </div>
          <div className="card">
            <p className="text-xs font-medium text-gray-400 uppercase tracking-wide">This Week</p>
            <p className="text-3xl font-bold text-primary-600 mt-1">{analytics?.submissions_this_week ?? 0}</p>
          </div>
          <div className="card">
            <p className="text-xs font-medium text-gray-400 uppercase tracking-wide">This Month</p>
            <p className="text-3xl font-bold text-primary-600 mt-1">{analytics?.submissions_this_month ?? 0}</p>
          </div>
        </div>

        {/* Avg Confidence + Status */}
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          {/* Classification Status */}
          <div className="card">
            <h3 className="text-sm font-semibold text-gray-700 uppercase tracking-wide mb-4">By Status</h3>
            <div className="space-y-3">
              {Object.entries(analytics?.by_status || {}).map(([status, count]) => {
                const colors = {
                  completed: 'bg-green-500',
                  processing: 'bg-blue-500',
                  pending: 'bg-yellow-500',
                  failed: 'bg-red-500',
                };
                return (
                  <div key={status}>
                    <div className="flex justify-between text-sm mb-1">
                      <span className="capitalize text-gray-600">{status}</span>
                      <span className="font-medium">{count} ({pct(count)}%)</span>
                    </div>
                    <div className="w-full bg-gray-100 rounded-full h-2">
                      <div className={`${colors[status] || 'bg-gray-400'} h-2 rounded-full`} style={{ width: `${pct(count)}%` }} />
                    </div>
                  </div>
                );
              })}
            </div>
            {analytics?.avg_confidence > 0 && (
              <div className="mt-4 pt-4 border-t border-gray-100 text-center">
                <p className="text-xs text-gray-400 uppercase tracking-wide">Avg Confidence</p>
                <p className="text-2xl font-bold text-primary-600">{(analytics.avg_confidence * 100).toFixed(1)}%</p>
              </div>
            )}
          </div>

          {/* Gender Distribution */}
          <div className="card">
            <h3 className="text-sm font-semibold text-gray-700 uppercase tracking-wide mb-4">By Gender</h3>
            <div className="space-y-3">
              {Object.entries(analytics?.by_gender || {}).map(([gender, count]) => (
                <div key={gender}>
                  <div className="flex justify-between text-sm mb-1">
                    <span className="text-gray-600">{gender}</span>
                    <span className="font-medium">{count} ({pct(count)}%)</span>
                  </div>
                  <div className="w-full bg-gray-100 rounded-full h-2">
                    <div className="bg-primary-500 h-2 rounded-full" style={{ width: `${pct(count)}%` }} />
                  </div>
                </div>
              ))}
            </div>
          </div>
        </div>

        {/* Country + Classification */}
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          {/* Top Countries */}
          <div className="card">
            <h3 className="text-sm font-semibold text-gray-700 uppercase tracking-wide mb-4">Top Countries</h3>
            {Object.keys(analytics?.by_country || {}).length === 0 ? (
              <p className="text-sm text-gray-400">No data yet</p>
            ) : (
              <div className="space-y-2">
                {Object.entries(analytics.by_country).map(([country, count]) => (
                  <div key={country} className="flex justify-between items-center py-1">
                    <span className="text-sm text-gray-600">{country}</span>
                    <div className="flex items-center gap-2">
                      <div className="w-24 bg-gray-100 rounded-full h-1.5">
                        <div className="bg-primary-400 h-1.5 rounded-full" style={{ width: `${pct(count)}%` }} />
                      </div>
                      <span className="text-sm font-medium text-gray-700 w-8 text-right">{count}</span>
                    </div>
                  </div>
                ))}
              </div>
            )}
          </div>

          {/* Top Classifications */}
          <div className="card">
            <h3 className="text-sm font-semibold text-gray-700 uppercase tracking-wide mb-4">Top Classifications</h3>
            {Object.keys(analytics?.by_classification || {}).length === 0 ? (
              <p className="text-sm text-gray-400">No classified submissions yet</p>
            ) : (
              <div className="space-y-2">
                {Object.entries(analytics.by_classification).map(([cls, count]) => (
                  <div key={cls} className="flex justify-between items-center py-1">
                    <span className="text-sm text-gray-600 truncate max-w-[200px]">{cls}</span>
                    <span className="text-sm font-medium text-primary-600">{count}</span>
                  </div>
                ))}
              </div>
            )}
          </div>
        </div>

        {/* Age Distribution */}
        <div className="card">
          <h3 className="text-sm font-semibold text-gray-700 uppercase tracking-wide mb-4">Age Distribution</h3>
          {(!analytics?.age_distribution || analytics.age_distribution.length === 0) ? (
            <p className="text-sm text-gray-400">No data yet</p>
          ) : (
            <div className="grid grid-cols-2 sm:grid-cols-4 md:grid-cols-7 gap-3">
              {analytics.age_distribution.map((group) => (
                <div key={group.range} className="text-center p-4 bg-gray-50 rounded-lg">
                  <p className="text-xs text-gray-500 font-medium">{group.range}</p>
                  <p className="text-2xl font-bold text-primary-600 mt-1">{group.count}</p>
                </div>
              ))}
            </div>
          )}
        </div>
      </div>
    </Layout>
  );
}
