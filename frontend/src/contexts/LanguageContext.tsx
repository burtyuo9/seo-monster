/**
 * SEO Monster - Language Context
 * Контекст для управления языком приложения
 */

import React, { createContext, useContext, useState, useEffect, ReactNode } from 'react';
import { Language, SUPPORTED_LANGUAGES, DEFAULT_LANGUAGE, t as translate, translations } from '../locales';

interface LanguageContextType {
  language: Language;
  setLanguage: (lang: Language) => void;
  t: (key: string, params?: Record<string, string | number>) => string;
  supportedLanguages: Language[];
}

const LanguageContext = createContext<LanguageContextType | undefined>(undefined);

const STORAGE_KEY = 'seo_monster_language';

export function LanguageProvider({ children }: { children: ReactNode }) {
  const [language, setLanguageState] = useState<Language>(() => {
    // Попытка загрузить язык из localStorage
    if (typeof window !== 'undefined') {
      const saved = localStorage.getItem(STORAGE_KEY);
      if (saved && SUPPORTED_LANGUAGES.includes(saved as Language)) {
        return saved as Language;
      }
      
      // Определение языка браузера
      const browserLang = navigator.language.split('-')[0];
      if (SUPPORTED_LANGUAGES.includes(browserLang as Language)) {
        return browserLang as Language;
      }
    }
    return DEFAULT_LANGUAGE;
  });

  const setLanguage = (lang: Language) => {
    if (SUPPORTED_LANGUAGES.includes(lang)) {
      setLanguageState(lang);
      localStorage.setItem(STORAGE_KEY, lang);
      
      // Обновление языка на сервере
      fetch('/api/localization/set', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ language: lang }),
      }).catch(console.error);
    }
  };

  const t = (key: string, params?: Record<string, string | number>): string => {
    return translate(key, language, params);
  };

  useEffect(() => {
    // Установка атрибута lang на html элемент
    document.documentElement.lang = language;
  }, [language]);

  return (
    <LanguageContext.Provider
      value={{
        language,
        setLanguage,
        t,
        supportedLanguages: SUPPORTED_LANGUAGES,
      }}
    >
      {children}
    </LanguageContext.Provider>
  );
}

export function useLanguage() {
  const context = useContext(LanguageContext);
  if (context === undefined) {
    throw new Error('useLanguage must be used within a LanguageProvider');
  }
  return context;
}

// Компонент переключателя языка
export function LanguageSwitcher({ className = '' }: { className?: string }) {
  const { language, setLanguage, supportedLanguages } = useLanguage();

  const languageNames: Record<Language, string> = {
    en: 'English',
    ru: 'Русский',
  };

  const languageFlags: Record<Language, string> = {
    en: '🇺🇸',
    ru: '🇷🇺',
  };

  return (
    <div className={`flex items-center gap-2 ${className}`}>
      {supportedLanguages.map((lang) => (
        <button
          key={lang}
          onClick={() => setLanguage(lang)}
          className={`
            flex items-center gap-1 px-3 py-1.5 rounded-lg text-sm font-medium
            transition-all duration-200
            ${language === lang
              ? 'bg-blue-600 text-white shadow-md'
              : 'bg-gray-100 text-gray-700 hover:bg-gray-200 dark:bg-gray-700 dark:text-gray-300 dark:hover:bg-gray-600'
            }
          `}
          title={languageNames[lang]}
        >
          <span>{languageFlags[lang]}</span>
          <span className="hidden sm:inline">{lang.toUpperCase()}</span>
        </button>
      ))}
    </div>
  );
}

// Компонент выпадающего списка языков
export function LanguageDropdown({ className = '' }: { className?: string }) {
  const { language, setLanguage, supportedLanguages } = useLanguage();
  const [isOpen, setIsOpen] = useState(false);

  const languageNames: Record<Language, string> = {
    en: 'English',
    ru: 'Русский',
  };

  const languageFlags: Record<Language, string> = {
    en: '🇺🇸',
    ru: '🇷🇺',
  };

  return (
    <div className={`relative ${className}`}>
      <button
        onClick={() => setIsOpen(!isOpen)}
        className="flex items-center gap-2 px-3 py-2 rounded-lg bg-gray-100 hover:bg-gray-200 dark:bg-gray-700 dark:hover:bg-gray-600 transition-colors"
      >
        <span>{languageFlags[language]}</span>
        <span>{languageNames[language]}</span>
        <svg
          className={`w-4 h-4 transition-transform ${isOpen ? 'rotate-180' : ''}`}
          fill="none"
          stroke="currentColor"
          viewBox="0 0 24 24"
        >
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 9l-7 7-7-7" />
        </svg>
      </button>

      {isOpen && (
        <div className="absolute top-full left-0 mt-1 w-full min-w-[150px] bg-white dark:bg-gray-800 rounded-lg shadow-lg border border-gray-200 dark:border-gray-700 overflow-hidden z-50">
          {supportedLanguages.map((lang) => (
            <button
              key={lang}
              onClick={() => {
                setLanguage(lang);
                setIsOpen(false);
              }}
              className={`
                w-full flex items-center gap-2 px-3 py-2 text-left
                ${language === lang
                  ? 'bg-blue-50 text-blue-600 dark:bg-blue-900/30 dark:text-blue-400'
                  : 'hover:bg-gray-50 dark:hover:bg-gray-700'
                }
              `}
            >
              <span>{languageFlags[lang]}</span>
              <span>{languageNames[lang]}</span>
              {language === lang && (
                <svg className="w-4 h-4 ml-auto" fill="currentColor" viewBox="0 0 20 20">
                  <path
                    fillRule="evenodd"
                    d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z"
                    clipRule="evenodd"
                  />
                </svg>
              )}
            </button>
          ))}
        </div>
      )}
    </div>
  );
}
