import { useState, useEffect } from 'react';

type Theme = 'dark' | 'light';

export function useTheme() {
  const [theme, setTheme] = useState<Theme>(() => {
    const saved = localStorage.getItem('seo-monster-theme');
    return (saved as Theme) || 'dark';
  });

  useEffect(() => {
    localStorage.setItem('seo-monster-theme', theme);
    document.documentElement.setAttribute('data-theme', theme);
    
    if (theme === 'light') {
      document.documentElement.classList.remove('dark');
      document.documentElement.classList.add('light');
    } else {
      document.documentElement.classList.remove('light');
      document.documentElement.classList.add('dark');
    }
  }, [theme]);

  const toggleTheme = () => {
    setTheme(prev => prev === 'dark' ? 'light' : 'dark');
  };

  return { theme, setTheme, toggleTheme };
}

interface ThemeToggleProps {
  theme: Theme;
  toggleTheme: () => void;
}

export default function ThemeToggle({ theme, toggleTheme }: ThemeToggleProps) {
  return (
    <button
      onClick={toggleTheme}
      className={`
        relative w-14 h-7 rounded-full transition-colors duration-300
        ${theme === 'dark' ? 'bg-gray-700' : 'bg-blue-200'}
      `}
      title={`Switch to ${theme === 'dark' ? 'light' : 'dark'} mode`}
    >
      <span
        className={`
          absolute top-0.5 w-6 h-6 rounded-full transition-all duration-300
          flex items-center justify-center text-sm
          ${theme === 'dark' 
            ? 'left-0.5 bg-gray-900' 
            : 'left-7 bg-yellow-400'
          }
        `}
      >
        {theme === 'dark' ? '🌙' : '☀️'}
      </span>
    </button>
  );
}
