import React from 'react';
import { Search, Bell, Sun, Moon } from 'lucide-react';

export default function Header() {
  const [isDark, setIsDark] = React.useState(true);

  const toggleTheme = () => {
    setIsDark(!isDark);
    document.documentElement.classList.toggle('dark');
  };

  return (
    <header className="h-16 glass border-b flex items-center justify-between px-6 z-10">
      <div className="flex-1 max-w-md flex items-center">
        <div className="relative w-full">
          <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-gray-400" />
          <input
            type="text"
            placeholder="Search candidates, jobs..."
            className="w-full pl-10 pr-4 py-2 bg-gray-100/50 dark:bg-navy-900/50 border-none rounded-full focus:ring-2 focus:ring-primary/50 outline-none text-sm"
          />
        </div>
      </div>
      <div className="flex items-center space-x-4">
        <button onClick={toggleTheme} className="p-2 rounded-full hover:bg-gray-100 dark:hover:bg-navy-800 transition-colors">
          {isDark ? <Sun className="w-5 h-5 text-gray-300" /> : <Moon className="w-5 h-5 text-gray-600" />}
        </button>
        <button className="p-2 rounded-full hover:bg-gray-100 dark:hover:bg-navy-800 transition-colors relative">
          <Bell className="w-5 h-5 text-gray-600 dark:text-gray-300" />
          <span className="absolute top-1.5 right-1.5 w-2 h-2 bg-red-500 rounded-full"></span>
        </button>
        <div className="w-8 h-8 rounded-full bg-gradient-to-tr from-primary to-secondary p-[2px] cursor-pointer">
          <div className="w-full h-full rounded-full bg-white dark:bg-navy-900 flex items-center justify-center overflow-hidden">
            <img src="https://ui-avatars.com/api/?name=Recruiter&background=random" alt="User" className="w-full h-full object-cover" />
          </div>
        </div>
      </div>
    </header>
  );
}
