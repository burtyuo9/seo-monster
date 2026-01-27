import React from 'react';
import { useTranslation } from 'react-i18next';
import { Globe } from 'lucide-react';

interface LanguageSwitcherProps {
  variant?: 'dropdown' | 'toggle' | 'flags';
  className?: string;
}

const LanguageSwitcher: React.FC<LanguageSwitcherProps> = ({ 
  variant = 'toggle',
  className = '' 
}) => {
  const { i18n, t } = useTranslation('common');
  const currentLang = i18n.language;

  const changeLanguage = (lng: string) => {
    i18n.changeLanguage(lng);
    localStorage.setItem('i18nextLng', lng);
  };

  // Toggle variant - simple RU/EN switch
  if (variant === 'toggle') {
    return (
      <div className={`flex items-center gap-2 ${className}`}>
        <Globe className="w-4 h-4 text-slate-400" />
        <div className="flex bg-slate-800 rounded-lg p-1">
          <button
            onClick={() => changeLanguage('en')}
            className={`px-3 py-1.5 text-sm font-medium rounded-md transition-all duration-200 ${
              currentLang === 'en' || currentLang.startsWith('en')
                ? 'bg-purple-600 text-white shadow-lg'
                : 'text-slate-400 hover:text-white'
            }`}
          >
            EN
          </button>
          <button
            onClick={() => changeLanguage('ru')}
            className={`px-3 py-1.5 text-sm font-medium rounded-md transition-all duration-200 ${
              currentLang === 'ru' || currentLang.startsWith('ru')
                ? 'bg-purple-600 text-white shadow-lg'
                : 'text-slate-400 hover:text-white'
            }`}
          >
            RU
          </button>
        </div>
      </div>
    );
  }

  // Flags variant - with country flags
  if (variant === 'flags') {
    return (
      <div className={`flex items-center gap-3 ${className}`}>
        <button
          onClick={() => changeLanguage('en')}
          className={`flex items-center gap-2 px-3 py-2 rounded-lg transition-all duration-200 ${
            currentLang === 'en' || currentLang.startsWith('en')
              ? 'bg-purple-600/20 border border-purple-500'
              : 'bg-slate-800 border border-transparent hover:border-slate-600'
          }`}
        >
          <span className="text-xl">🇺🇸</span>
          <span className="text-sm font-medium text-slate-300">English</span>
        </button>
        <button
          onClick={() => changeLanguage('ru')}
          className={`flex items-center gap-2 px-3 py-2 rounded-lg transition-all duration-200 ${
            currentLang === 'ru' || currentLang.startsWith('ru')
              ? 'bg-purple-600/20 border border-purple-500'
              : 'bg-slate-800 border border-transparent hover:border-slate-600'
          }`}
        >
          <span className="text-xl">🇷🇺</span>
          <span className="text-sm font-medium text-slate-300">Русский</span>
        </button>
      </div>
    );
  }

  // Dropdown variant
  return (
    <div className={`relative group ${className}`}>
      <button className="flex items-center gap-2 px-3 py-2 bg-slate-800 rounded-lg hover:bg-slate-700 transition-colors">
        <Globe className="w-4 h-4 text-purple-400" />
        <span className="text-sm font-medium text-slate-300">
          {currentLang === 'ru' || currentLang.startsWith('ru') ? '🇷🇺 RU' : '🇺🇸 EN'}
        </span>
        <svg className="w-4 h-4 text-slate-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 9l-7 7-7-7" />
        </svg>
      </button>
      <div className="absolute right-0 mt-2 w-40 bg-slate-800 rounded-lg shadow-xl border border-slate-700 opacity-0 invisible group-hover:opacity-100 group-hover:visible transition-all duration-200 z-50">
        <button
          onClick={() => changeLanguage('en')}
          className={`w-full flex items-center gap-3 px-4 py-3 text-left hover:bg-slate-700 rounded-t-lg transition-colors ${
            currentLang === 'en' || currentLang.startsWith('en') ? 'bg-purple-600/20' : ''
          }`}
        >
          <span className="text-lg">🇺🇸</span>
          <span className="text-sm text-slate-300">English</span>
          {(currentLang === 'en' || currentLang.startsWith('en')) && (
            <svg className="w-4 h-4 text-purple-400 ml-auto" fill="currentColor" viewBox="0 0 20 20">
              <path fillRule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clipRule="evenodd" />
            </svg>
          )}
        </button>
        <button
          onClick={() => changeLanguage('ru')}
          className={`w-full flex items-center gap-3 px-4 py-3 text-left hover:bg-slate-700 rounded-b-lg transition-colors ${
            currentLang === 'ru' || currentLang.startsWith('ru') ? 'bg-purple-600/20' : ''
          }`}
        >
          <span className="text-lg">🇷🇺</span>
          <span className="text-sm text-slate-300">Русский</span>
          {(currentLang === 'ru' || currentLang.startsWith('ru')) && (
            <svg className="w-4 h-4 text-purple-400 ml-auto" fill="currentColor" viewBox="0 0 20 20">
              <path fillRule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clipRule="evenodd" />
            </svg>
          )}
        </button>
      </div>
    </div>
  );
};

export default LanguageSwitcher;
