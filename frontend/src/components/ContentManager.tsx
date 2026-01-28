import React, { useState, useEffect, useCallback } from 'react';
import { useLanguage } from '../contexts/LanguageContext';
import { useTheme } from './ThemeToggle';

interface Article {
  id: string;
  topic: string;
  title: string;
  content_type: string;
  language: string;
  word_count: number;
  generated_at: string;
  content?: string;
}

const API_URL = 'http://144.31.238.16:8000';

const ContentManager: React.FC = () => {
  const { language } = useLanguage();
  const { theme } = useTheme();

  // Состояния
  const [articles, setArticles] = useState<Article[]>([]);
  const [loading, setLoading] = useState(true);
  const [generating, setGenerating] = useState(false);
  const [showGenerateModal, setShowGenerateModal] = useState(false);
  const [showPreviewModal, setShowPreviewModal] = useState(false);
  const [selectedArticle, setSelectedArticle] = useState<Article | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [success, setSuccess] = useState<string | null>(null);

  // Форма генерации
  const [generateForm, setGenerateForm] = useState({
    topic: '',
    language: 'en',
    content_type: 'article',
    word_count: 1000,
    tone: 'professional'
  });

  // Переводы
  const t = {
    title: language === 'ru' ? 'Контент' : 'Content',
    generate: language === 'ru' ? 'Создать контент' : 'Generate Content',
    noContent: language === 'ru' ? 'Нет созданного контента' : 'No content created yet',
    noContentDesc: language === 'ru' ? 'Создайте контент с помощью ИИ' : 'Generate content using AI',
    topic: language === 'ru' ? 'Тема' : 'Topic',
    lang: language === 'ru' ? 'Язык' : 'Language',
    type: language === 'ru' ? 'Тип контента' : 'Content Type',
    wordCount: language === 'ru' ? 'Количество слов' : 'Word Count',
    tone: language === 'ru' ? 'Тон' : 'Tone',
    cancel: language === 'ru' ? 'Отмена' : 'Cancel',
    generating: language === 'ru' ? 'Генерация...' : 'Generating...',
    preview: language === 'ru' ? 'Просмотр' : 'Preview',
    delete: language === 'ru' ? 'Удалить' : 'Delete',
    copy: language === 'ru' ? 'Копировать' : 'Copy',
    download: language === 'ru' ? 'Скачать' : 'Download',
    createdAt: language === 'ru' ? 'Создано' : 'Created',
    words: language === 'ru' ? 'слов' : 'words',
    loading: language === 'ru' ? 'Загрузка...' : 'Loading...',
    article: language === 'ru' ? 'Статья' : 'Article',
    guide: language === 'ru' ? 'Руководство' : 'Guide',
    review: language === 'ru' ? 'Обзор' : 'Review',
    comparison: language === 'ru' ? 'Сравнение' : 'Comparison',
    howTo: language === 'ru' ? 'Как сделать' : 'How-to',
    professional: language === 'ru' ? 'Профессиональный' : 'Professional',
    casual: language === 'ru' ? 'Разговорный' : 'Casual',
    formal: language === 'ru' ? 'Формальный' : 'Formal',
    friendly: language === 'ru' ? 'Дружелюбный' : 'Friendly',
  };

  const contentTypes = [
    { id: 'article', name: t.article },
    { id: 'guide', name: t.guide },
    { id: 'review', name: t.review },
    { id: 'comparison', name: t.comparison },
    { id: 'how-to', name: t.howTo },
  ];

  const tones = [
    { id: 'professional', name: t.professional },
    { id: 'casual', name: t.casual },
    { id: 'formal', name: t.formal },
    { id: 'friendly', name: t.friendly },
  ];

  const languages_list = [
    { code: 'en', name: 'English' },
    { code: 'ru', name: 'Русский' },
    { code: 'de', name: 'Deutsch' },
    { code: 'fr', name: 'Français' },
    { code: 'es', name: 'Español' },
    { code: 'it', name: 'Italiano' },
    { code: 'pt', name: 'Português' },
    { code: 'zh', name: '中文' },
    { code: 'ja', name: '日本語' },
    { code: 'ko', name: '한국어' },
  ];

  // Загрузка данных
  const loadData = useCallback(async () => {
    setLoading(true);
    try {
      const res = await fetch(`${API_URL}/api/autonomous/articles`);
      if (res.ok) {
        const data = await res.json();
        setArticles(data.articles || []);
      }
    } catch (err) {
      console.error('Error loading articles:', err);
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    loadData();
  }, [loadData]);

  // Генерация контента
  const handleGenerate = async () => {
    if (!generateForm.topic) {
      setError(language === 'ru' ? 'Тема обязательна' : 'Topic is required');
      return;
    }

    setGenerating(true);
    setError(null);

    try {
      const res = await fetch(`${API_URL}/api/autonomous/generate`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(generateForm)
      });

      if (res.ok) {
        const data = await res.json();
        setSuccess(language === 'ru' ? 'Контент создан!' : 'Content generated!');
        setShowGenerateModal(false);
        setGenerateForm({
          topic: '',
          language: 'en',
          content_type: 'article',
          word_count: 1000,
          tone: 'professional'
        });
        loadData();
        setTimeout(() => setSuccess(null), 3000);
      } else {
        const data = await res.json();
        setError(data.detail || (language === 'ru' ? 'Ошибка генерации' : 'Generation error'));
      }
    } catch (err) {
      setError(language === 'ru' ? 'Ошибка сети' : 'Network error');
    } finally {
      setGenerating(false);
    }
  };

  // Удаление статьи
  const handleDelete = async (articleId: string) => {
    if (!confirm(language === 'ru' ? 'Удалить эту статью?' : 'Delete this article?')) return;

    try {
      const res = await fetch(`${API_URL}/api/autonomous/articles/${articleId}`, {
        method: 'DELETE'
      });

      if (res.ok) {
        setSuccess(language === 'ru' ? 'Статья удалена' : 'Article deleted');
        loadData();
        setTimeout(() => setSuccess(null), 3000);
      }
    } catch (err) {
      setError(language === 'ru' ? 'Ошибка удаления' : 'Delete error');
    }
  };

  // Копирование в буфер
  const handleCopy = async (article: Article) => {
    try {
      await navigator.clipboard.writeText(article.content || article.title);
      setSuccess(language === 'ru' ? 'Скопировано!' : 'Copied!');
      setTimeout(() => setSuccess(null), 2000);
    } catch (err) {
      setError(language === 'ru' ? 'Ошибка копирования' : 'Copy error');
    }
  };

  // Скачивание
  const handleDownload = (article: Article) => {
    const content = article.content || article.title;
    const blob = new Blob([content], { type: 'text/plain' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `${article.title.slice(0, 50)}.txt`;
    a.click();
    URL.revokeObjectURL(url);
  };

  // Стили
  const cardBg = theme === 'dark' ? 'bg-gray-800' : 'bg-white shadow';
  const textPrimary = theme === 'dark' ? 'text-white' : 'text-gray-900';
  const textSecondary = theme === 'dark' ? 'text-gray-400' : 'text-gray-500';
  const borderColor = theme === 'dark' ? 'border-gray-700' : 'border-gray-200';
  const inputBg = theme === 'dark' ? 'bg-gray-700 text-white border-gray-600' : 'bg-white text-gray-900 border-gray-300';

  if (loading) {
    return (
      <div className={`p-6 rounded-lg ${cardBg}`}>
        <div className="flex items-center justify-center py-12">
          <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-purple-500"></div>
          <span className={`ml-3 ${textSecondary}`}>{t.loading}</span>
        </div>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Уведомления */}
      {error && (
        <div className="p-4 bg-red-500/20 border border-red-500 rounded-lg text-red-400">
          {error}
          <button onClick={() => setError(null)} className="float-right">×</button>
        </div>
      )}
      {success && (
        <div className="p-4 bg-green-500/20 border border-green-500 rounded-lg text-green-400">
          {success}
        </div>
      )}

      {/* Заголовок и кнопка генерации */}
      <div className={`p-6 rounded-lg ${cardBg}`}>
        <div className="flex justify-between items-center mb-6">
          <h3 className={`text-xl font-bold ${textPrimary}`}>{t.title}</h3>
          <button
            onClick={() => setShowGenerateModal(true)}
            className="px-4 py-2 bg-purple-600 text-white rounded-lg hover:bg-purple-700 transition-colors flex items-center gap-2"
          >
            <span>✨</span> {t.generate}
          </button>
        </div>

        {/* Список статей */}
        {articles.length === 0 ? (
          <div className={`text-center py-12 ${textSecondary}`}>
            <span className="text-6xl">📝</span>
            <p className="mt-4 text-lg">{t.noContent}</p>
            <p className="mt-2">{t.noContentDesc}</p>
            <button
              onClick={() => setShowGenerateModal(true)}
              className="mt-4 px-6 py-3 bg-purple-600 text-white rounded-lg hover:bg-purple-700 transition-colors"
            >
              ✨ {t.generate}
            </button>
          </div>
        ) : (
          <div className="grid gap-4">
            {articles.map((article) => (
              <div key={article.id} className={`p-4 rounded-lg border ${borderColor} ${theme === 'dark' ? 'bg-gray-700' : 'bg-gray-50'}`}>
                <div className="flex justify-between items-start">
                  <div className="flex-1">
                    <h4 className={`font-medium ${textPrimary}`}>{article.title}</h4>
                    <div className="flex gap-4 mt-2">
                      <span className={`text-sm ${textSecondary}`}>
                        📝 {article.content_type}
                      </span>
                      <span className={`text-sm ${textSecondary}`}>
                        🌐 {article.language.toUpperCase()}
                      </span>
                      <span className={`text-sm ${textSecondary}`}>
                        📊 {article.word_count} {t.words}
                      </span>
                      <span className={`text-sm ${textSecondary}`}>
                        📅 {new Date(article.generated_at).toLocaleDateString()}
                      </span>
                    </div>
                  </div>
                  <div className="flex gap-2">
                    <button
                      onClick={() => {
                        setSelectedArticle(article);
                        setShowPreviewModal(true);
                      }}
                      className="px-3 py-1 bg-blue-600 text-white text-sm rounded hover:bg-blue-700"
                    >
                      👁️ {t.preview}
                    </button>
                    <button
                      onClick={() => handleCopy(article)}
                      className="px-3 py-1 bg-gray-600 text-white text-sm rounded hover:bg-gray-700"
                    >
                      📋
                    </button>
                    <button
                      onClick={() => handleDownload(article)}
                      className="px-3 py-1 bg-green-600 text-white text-sm rounded hover:bg-green-700"
                    >
                      ⬇️
                    </button>
                    <button
                      onClick={() => handleDelete(article.id)}
                      className="px-3 py-1 bg-red-600 text-white text-sm rounded hover:bg-red-700"
                    >
                      🗑️
                    </button>
                  </div>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>

      {/* Модальное окно генерации */}
      {showGenerateModal && (
        <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50">
          <div className={`p-6 rounded-lg w-full max-w-lg ${cardBg}`}>
            <h3 className={`text-xl font-bold mb-4 ${textPrimary}`}>{t.generate}</h3>
            
            <div className="space-y-4">
              <div>
                <label className={`block text-sm mb-1 ${textSecondary}`}>{t.topic} *</label>
                <input
                  type="text"
                  value={generateForm.topic}
                  onChange={(e) => setGenerateForm({ ...generateForm, topic: e.target.value })}
                  placeholder={language === 'ru' ? 'О чём написать статью...' : 'What to write about...'}
                  className={`w-full px-4 py-2 rounded-lg border ${inputBg} focus:outline-none focus:ring-2 focus:ring-purple-500`}
                />
              </div>
              
              <div className="grid grid-cols-2 gap-4">
                <div>
                  <label className={`block text-sm mb-1 ${textSecondary}`}>{t.lang}</label>
                  <select
                    value={generateForm.language}
                    onChange={(e) => setGenerateForm({ ...generateForm, language: e.target.value })}
                    className={`w-full px-4 py-2 rounded-lg border ${inputBg} focus:outline-none focus:ring-2 focus:ring-purple-500`}
                  >
                    {languages_list.map((lang) => (
                      <option key={lang.code} value={lang.code}>{lang.name}</option>
                    ))}
                  </select>
                </div>
                
                <div>
                  <label className={`block text-sm mb-1 ${textSecondary}`}>{t.type}</label>
                  <select
                    value={generateForm.content_type}
                    onChange={(e) => setGenerateForm({ ...generateForm, content_type: e.target.value })}
                    className={`w-full px-4 py-2 rounded-lg border ${inputBg} focus:outline-none focus:ring-2 focus:ring-purple-500`}
                  >
                    {contentTypes.map((type) => (
                      <option key={type.id} value={type.id}>{type.name}</option>
                    ))}
                  </select>
                </div>
              </div>
              
              <div className="grid grid-cols-2 gap-4">
                <div>
                  <label className={`block text-sm mb-1 ${textSecondary}`}>{t.wordCount}</label>
                  <select
                    value={generateForm.word_count}
                    onChange={(e) => setGenerateForm({ ...generateForm, word_count: parseInt(e.target.value) })}
                    className={`w-full px-4 py-2 rounded-lg border ${inputBg} focus:outline-none focus:ring-2 focus:ring-purple-500`}
                  >
                    <option value={500}>500</option>
                    <option value={800}>800</option>
                    <option value={1000}>1000</option>
                    <option value={1500}>1500</option>
                    <option value={2000}>2000</option>
                    <option value={3000}>3000</option>
                  </select>
                </div>
                
                <div>
                  <label className={`block text-sm mb-1 ${textSecondary}`}>{t.tone}</label>
                  <select
                    value={generateForm.tone}
                    onChange={(e) => setGenerateForm({ ...generateForm, tone: e.target.value })}
                    className={`w-full px-4 py-2 rounded-lg border ${inputBg} focus:outline-none focus:ring-2 focus:ring-purple-500`}
                  >
                    {tones.map((tone) => (
                      <option key={tone.id} value={tone.id}>{tone.name}</option>
                    ))}
                  </select>
                </div>
              </div>
            </div>
            
            <div className="flex gap-3 mt-6">
              <button
                onClick={() => setShowGenerateModal(false)}
                disabled={generating}
                className={`flex-1 px-4 py-2 rounded-lg border ${borderColor} ${textPrimary} hover:bg-gray-700 disabled:opacity-50`}
              >
                {t.cancel}
              </button>
              <button
                onClick={handleGenerate}
                disabled={generating}
                className="flex-1 px-4 py-2 bg-purple-600 text-white rounded-lg hover:bg-purple-700 disabled:opacity-50 flex items-center justify-center gap-2"
              >
                {generating ? (
                  <>
                    <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white"></div>
                    {t.generating}
                  </>
                ) : (
                  <>✨ {t.generate}</>
                )}
              </button>
            </div>
          </div>
        </div>
      )}

      {/* Модальное окно предпросмотра */}
      {showPreviewModal && selectedArticle && (
        <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50">
          <div className={`p-6 rounded-lg w-full max-w-3xl max-h-[80vh] overflow-auto ${cardBg}`}>
            <div className="flex justify-between items-start mb-4">
              <h3 className={`text-xl font-bold ${textPrimary}`}>{selectedArticle.title}</h3>
              <button
                onClick={() => setShowPreviewModal(false)}
                className={`text-2xl ${textSecondary} hover:${textPrimary}`}
              >
                ×
              </button>
            </div>
            
            <div className="flex gap-4 mb-4">
              <span className={`text-sm ${textSecondary}`}>📝 {selectedArticle.content_type}</span>
              <span className={`text-sm ${textSecondary}`}>🌐 {selectedArticle.language.toUpperCase()}</span>
              <span className={`text-sm ${textSecondary}`}>📊 {selectedArticle.word_count} {t.words}</span>
            </div>
            
            <div className={`p-4 rounded-lg ${theme === 'dark' ? 'bg-gray-700' : 'bg-gray-100'} ${textPrimary} whitespace-pre-wrap`}>
              {selectedArticle.content || selectedArticle.title}
            </div>
            
            <div className="flex gap-3 mt-4">
              <button
                onClick={() => handleCopy(selectedArticle)}
                className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700"
              >
                📋 {t.copy}
              </button>
              <button
                onClick={() => handleDownload(selectedArticle)}
                className="px-4 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700"
              >
                ⬇️ {t.download}
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default ContentManager;
