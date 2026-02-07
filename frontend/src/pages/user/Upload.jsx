import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import Layout from '../../components/Layout';
import { appAPI } from '../../lib/api';

export default function Upload() {
  const [formData, setFormData] = useState({
    name: '',
    age: '',
    gender: '',
    location: '',
    country: '',
    description: '',
  });
  const [photo, setPhoto] = useState(null);
  const [preview, setPreview] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [success, setSuccess] = useState(false);
  const [uploadedId, setUploadedId] = useState(null);
  const navigate = useNavigate();

  const handleChange = (e) => {
    setFormData({
      ...formData,
      [e.target.name]: e.target.value,
    });
  };

  const handlePhotoChange = (e) => {
    const file = e.target.files[0];
    if (file) {
      setPhoto(file);
      const reader = new FileReader();
      reader.onloadend = () => {
        setPreview(reader.result);
      };
      reader.readAsDataURL(file);
    }
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');
    setLoading(true);

    const data = new FormData();
    data.append('photo', photo);
    data.append('name', formData.name);
    data.append('age', formData.age);
    data.append('gender', formData.gender);
    data.append('location', formData.location);
    data.append('country', formData.country);
    if (formData.description) {
      data.append('description', formData.description);
    }

    try {
      const response = await appAPI.uploadPhoto(data);
      setUploadedId(response.data.id);
      setSuccess(true);
      setError('');
      
      // Don't block - let user navigate immediately
      // Classification happens in background
      setTimeout(() => {
        navigate('/dashboard');
      }, 3000);
    } catch (err) {
      const errorMsg = err.response?.data?.detail || err.response?.data?.message;
      if (err.response?.status === 413) {
        setError('File too large. Maximum size is 10MB.');
      } else if (err.response?.status === 415) {
        setError('Invalid file type. Please upload an image (JPG, PNG, GIF).');
      } else {
        setError(errorMsg || 'Upload failed. Please try again.');
      }
    } finally {
      setLoading(false);
    }
  };

  return (
    <Layout>
      <div className="max-w-2xl mx-auto">
        <h1 className="text-3xl font-bold text-gray-900 mb-6">Upload Photo</h1>

        {success && (
          <div className="bg-green-50 border border-green-200 text-green-700 px-4 py-3 rounded mb-6">
            <p className="font-semibold">Photo uploaded successfully!</p>
            <p className="text-sm mt-1">Classification is processing in the background. You can view results in your dashboard.</p>
          </div>
        )}

        {error && (
          <div className="bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded mb-6">
            {error}
          </div>
        )}

        <form onSubmit={handleSubmit} className="card space-y-6">
          {/* Photo Upload */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Photo *
            </label>
            <div className="mt-1 flex justify-center px-6 pt-5 pb-6 border-2 border-gray-300 border-dashed rounded-lg hover:border-primary-400 transition-colors">
              <div className="space-y-1 text-center">
                {preview ? (
                  <div className="mb-4">
                    <img src={preview} alt="Preview" className="mx-auto h-48 w-auto rounded" />
                  </div>
                ) : (
                  <svg className="mx-auto h-12 w-12 text-gray-400" stroke="currentColor" fill="none" viewBox="0 0 48 48">
                    <path d="M28 8H12a4 4 0 00-4 4v20m32-12v8m0 0v8a4 4 0 01-4 4H12a4 4 0 01-4-4v-4m32-4l-3.172-3.172a4 4 0 00-5.656 0L28 28M8 32l9.172-9.172a4 4 0 015.656 0L28 28m0 0l4 4m4-24h8m-4-4v8m-12 4h.02" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" />
                  </svg>
                )}
                <div className="flex text-sm text-gray-600">
                  <label htmlFor="photo" className="relative cursor-pointer bg-white rounded-md font-medium text-primary-600 hover:text-primary-500">
                    <span>Upload a file</span>
                    <input
                      id="photo"
                      name="photo"
                      type="file"
                      className="sr-only"
                      accept="image/*"
                      required
                      onChange={handlePhotoChange}
                    />
                  </label>
                  <p className="pl-1">or drag and drop</p>
                </div>
                <p className="text-xs text-gray-500">PNG, JPG, GIF up to 10MB</p>
              </div>
            </div>
          </div>

          {/* Personal Information */}
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div>
              <label htmlFor="name" className="block text-sm font-medium text-gray-700">
                Name *
              </label>
              <input
                type="text"
                name="name"
                id="name"
                required
                className="input-field mt-1"
                value={formData.name}
                onChange={handleChange}
              />
            </div>

            <div>
              <label htmlFor="age" className="block text-sm font-medium text-gray-700">
                Age *
              </label>
              <input
                type="number"
                name="age"
                id="age"
                required
                min="1"
                max="150"
                className="input-field mt-1"
                value={formData.age}
                onChange={handleChange}
              />
            </div>

            <div>
              <label htmlFor="gender" className="block text-sm font-medium text-gray-700">
                Gender *
              </label>
              <select
                name="gender"
                id="gender"
                required
                className="input-field mt-1"
                value={formData.gender}
                onChange={handleChange}
              >
                <option value="">Select gender</option>
                <option value="Male">Male</option>
                <option value="Female">Female</option>
                <option value="Other">Other</option>
              </select>
            </div>

            <div>
              <label htmlFor="location" className="block text-sm font-medium text-gray-700">
                Location *
              </label>
              <input
                type="text"
                name="location"
                id="location"
                required
                className="input-field mt-1"
                placeholder="City"
                value={formData.location}
                onChange={handleChange}
              />
            </div>

            <div className="md:col-span-2">
              <label htmlFor="country" className="block text-sm font-medium text-gray-700">
                Country *
              </label>
              <input
                type="text"
                name="country"
                id="country"
                required
                className="input-field mt-1"
                value={formData.country}
                onChange={handleChange}
              />
            </div>

            <div className="md:col-span-2">
              <label htmlFor="description" className="block text-sm font-medium text-gray-700">
                Description (Optional)
              </label>
              <textarea
                name="description"
                id="description"
                rows="3"
                maxLength="500"
                className="input-field mt-1"
                placeholder="Add any additional information (max 500 characters)"
                value={formData.description}
                onChange={handleChange}
              />
              <p className="mt-1 text-xs text-gray-500">
                {formData.description.length}/500 characters
              </p>
            </div>
          </div>

          {/* Submit Button */}
          <div className="flex justify-end space-x-3">
            <button
              type="button"
              onClick={() => navigate('/dashboard')}
              className="btn-secondary"
            >
              Cancel
            </button>
            <button
              type="submit"
              disabled={loading || !photo}
              className="btn-primary disabled:opacity-50 disabled:cursor-not-allowed"
            >
              {loading ? 'Uploading...' : 'Upload Photo'}
            </button>
          </div>
        </form>
      </div>
    </Layout>
  );
}
