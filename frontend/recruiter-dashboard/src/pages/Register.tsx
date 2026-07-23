import React from 'react';
import { Link } from 'react-router-dom';

export default function Register() {
  return (
    <div className="min-h-screen flex items-center justify-center relative bg-navy-900 overflow-hidden">
      <div className="glass-card w-full max-w-md p-8 relative z-10">
        <h2 className="text-2xl font-bold text-white mb-6 text-center">Create Account</h2>
        <form className="space-y-4">
          <input className="w-full bg-navy-900/50 border border-gray-700 rounded-lg p-2.5 text-white" placeholder="Name" />
          <input className="w-full bg-navy-900/50 border border-gray-700 rounded-lg p-2.5 text-white" type="email" placeholder="Email" />
          <input className="w-full bg-navy-900/50 border border-gray-700 rounded-lg p-2.5 text-white" type="password" placeholder="Password" />
          <button className="w-full bg-primary text-white py-2.5 rounded-lg">Register</button>
        </form>
        <p className="mt-4 text-center text-sm text-gray-400">
          Already have an account? <Link to="/login" className="text-primary">Login</Link>
        </p>
      </div>
    </div>
  );
}
