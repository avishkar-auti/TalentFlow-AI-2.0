import React from 'react';

export default function Settings() {
  return (
    <div className="animate-fade-in max-w-2xl mx-auto">
      <h1 className="text-2xl font-bold dark:text-white mb-6">Settings</h1>
      <div className="glass-card p-6 space-y-6">
        <div>
          <h3 className="text-lg font-semibold dark:text-white mb-4">Profile Information</h3>
          <div className="space-y-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">Full Name</label>
              <input type="text" className="w-full px-4 py-2 rounded-lg border border-gray-200 dark:border-gray-700 bg-gray-50 dark:bg-navy-900 text-gray-900 dark:text-white" defaultValue="Recruiter Name" />
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">Email</label>
              <input type="email" className="w-full px-4 py-2 rounded-lg border border-gray-200 dark:border-gray-700 bg-gray-50 dark:bg-navy-900 text-gray-900 dark:text-white" defaultValue="recruiter@company.com" disabled />
            </div>
          </div>
        </div>
        <hr className="border-gray-200 dark:border-gray-700" />
        <div>
          <h3 className="text-lg font-semibold dark:text-white mb-4">Preferences</h3>
          <div className="flex items-center justify-between">
            <span className="text-sm dark:text-gray-300">Email Notifications</span>
            <input type="checkbox" className="toggle" defaultChecked />
          </div>
        </div>
        <div className="pt-4 flex justify-end">
          <button className="px-6 py-2 bg-primary text-white rounded-lg font-medium shadow-lg shadow-primary/25 hover:bg-primary/90 transition-colors">
            Save Changes
          </button>
        </div>
      </div>
    </div>
  );
}
