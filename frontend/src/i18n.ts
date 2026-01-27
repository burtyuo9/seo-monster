import i18n from 'i18next';
import { initReactI18next } from 'react-i18next';
import LanguageDetector from 'i18next-browser-languagedetector';

// English translations
import enCommon from './locales/en/common.json';
import enDashboard from './locales/en/dashboard.json';
import enAutopilot from './locales/en/autopilot.json';
import enContent from './locales/en/content.json';
import enKeywords from './locales/en/keywords.json';
import enCompetitors from './locales/en/competitors.json';
import enIndexing from './locales/en/indexing.json';
import enSettings from './locales/en/settings.json';

// Russian translations
import ruCommon from './locales/ru/common.json';
import ruDashboard from './locales/ru/dashboard.json';
import ruAutopilot from './locales/ru/autopilot.json';
import ruContent from './locales/ru/content.json';
import ruKeywords from './locales/ru/keywords.json';
import ruCompetitors from './locales/ru/competitors.json';
import ruIndexing from './locales/ru/indexing.json';
import ruSettings from './locales/ru/settings.json';

const resources = {
  en: {
    common: enCommon,
    dashboard: enDashboard,
    autopilot: enAutopilot,
    content: enContent,
    keywords: enKeywords,
    competitors: enCompetitors,
    indexing: enIndexing,
    settings: enSettings,
  },
  ru: {
    common: ruCommon,
    dashboard: ruDashboard,
    autopilot: ruAutopilot,
    content: ruContent,
    keywords: ruKeywords,
    competitors: ruCompetitors,
    indexing: ruIndexing,
    settings: ruSettings,
  },
};

i18n
  .use(LanguageDetector)
  .use(initReactI18next)
  .init({
    resources,
    fallbackLng: 'en',
    defaultNS: 'common',
    ns: ['common', 'dashboard', 'autopilot', 'content', 'keywords', 'competitors', 'indexing', 'settings'],
    interpolation: {
      escapeValue: false,
    },
    detection: {
      order: ['localStorage', 'navigator'],
      caches: ['localStorage'],
    },
  });

export default i18n;
