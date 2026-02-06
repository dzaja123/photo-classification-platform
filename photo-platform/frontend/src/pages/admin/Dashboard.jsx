import React from 'react';
import { Link } from 'react-router-dom';
import Layout from '../../components/Layout';

export default function AdminDashboard() {
  return (
    <Layout>
      <div className="space-y-6">
        <h1 className="text-3xl font-bold text-gray-900">Admin Dashboard</h1>

        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
          <Link to="/admin/submissions" className="card hover:shadow-lg transition-shadow cursor-pointer">
            <h3 className="text-lg font-semibold text-gray-900 mb-2">Submissions</h3>
            <p className="text-gray-600">View and filter all submissions</p>
          </Link>

          <Link to="/admin/analytics" className="card hover:shadow-lg transition-shadow cursor-pointer">
            <h3 className="text-lg font-semibold text-gray-900 mb-2">Analytics</h3>
            <p className="text-gray-600">View statistics and charts</p>
          </Link>

          <div className="card">
            <h3 className="text-lg font-semibold text-gray-900 mb-2">Audit Logs</h3>
            <p className="text-gray-600">View system activity</p>
          </div>
        </div>
      </div>
    </Layout>
  );
}
