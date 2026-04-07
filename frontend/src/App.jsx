import React, { useState, useEffect, useCallback } from 'react';
import api from './api';
import './App.css';

function App() {
  // Состояния
  const [user, setUser] = useState(null);
  const [items, setItems] = useState([]);
  const [loading, setLoading] = useState(false);
  const [userLoading, setUserLoading] = useState(true);

  // Формы
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [username, setUsername] = useState('');
  const [title, setTitle] = useState('');
  const [description, setDescription] = useState('');

  // Какую страницу показывать
  const [page, setPage] = useState('login');

  // Загружаем список товаров
  const loadItems = useCallback(async () => {
    setLoading(true);
    try {
      const res = await api.get('/api/v1/items/');
      setItems(res.data);
    } catch (err) {
      console.error('Ошибка загрузки товаров:', err);
      if (err.response?.status === 401) {
        // Токен истек - пробуем обновить
        const refreshToken = localStorage.getItem('refreshToken');
        if (refreshToken) {
          try {
            const refreshRes = await api.post('/api/v1/auth/refresh', {
              refresh_token: refreshToken
            });
            localStorage.setItem('accessToken', refreshRes.data.access_token);
            // Повторяем запрос
            const retryRes = await api.get('/api/v1/items/');
            setItems(retryRes.data);
          } catch (refreshErr) {
            console.error('Refresh token error:', refreshErr);
            localStorage.removeItem('accessToken');
            localStorage.removeItem('refreshToken');
            setPage('login');
          }
        } else {
          setPage('login');
        }
      }
    }
    setLoading(false);
  }, []);

  // Загружаем данные пользователя
  const loadUser = useCallback(async () => {
    setUserLoading(true);
    try {
      const res = await api.get('/api/v1/auth/me');
      console.log('User data from /me:', res.data);
      setUser(res.data);
      setPage('items');
      await loadItems();
    } catch (err) {
      console.error('Error loading user:', err);
      localStorage.removeItem('accessToken');
      localStorage.removeItem('refreshToken');
      setPage('login');
    } finally {
      setUserLoading(false);
    }
  }, [loadItems]);

  // Проверяем токен при загрузке
  useEffect(() => {
    const accessToken = localStorage.getItem('accessToken');
    if (accessToken) {
      loadUser();
    } else {
      setUserLoading(false);
    }
  }, [loadUser]);

  // Регистрация
  const handleRegister = async (e) => {
    e.preventDefault();
    setLoading(true);
    try {
      const res = await api.post('/api/v1/auth/register', {
        email,
        username: username || email.split('@')[0],
        password,
      });

      // Сохраняем оба токена
      localStorage.setItem('accessToken', res.data.access_token);
      localStorage.setItem('refreshToken', res.data.refresh_token);

      await loadUser();
    } catch (err) {
      alert(err.response?.data?.detail || 'Ошибка регистрации');
    } finally {
      setLoading(false);
    }
  };

  // Вход
  const handleLogin = async (e) => {
    e.preventDefault();
    setLoading(true);
    try {
      const res = await api.post('/api/v1/auth/login', { email, password });

      // Сохраняем оба токена
      localStorage.setItem('accessToken', res.data.access_token);
      localStorage.setItem('refreshToken', res.data.refresh_token);

      await loadUser();
    } catch (err) {
      alert('Неверный email или пароль');
    } finally {
      setLoading(false);
    }
  };

  // Выход
  const handleLogout = async () => {
    try {
      const refreshToken = localStorage.getItem('refreshToken');
      if (refreshToken) {
        await api.post('/api/v1/auth/logout', { refresh_token: refreshToken });
      }
    } catch (err) {
      console.error('Logout error:', err);
    } finally {
      localStorage.removeItem('accessToken');
      localStorage.removeItem('refreshToken');
      setUser(null);
      setPage('login');
      setEmail('');
      setPassword('');
      setUsername('');
    }
  };

  // Создание товара
  const handleCreateItem = async (e) => {
    e.preventDefault();
    if (!title.trim()) return;

    setLoading(true);
    try {
      await api.post('/api/v1/items/', { title, description });
      setTitle('');
      setDescription('');
      await loadItems();
    } catch (err) {
      alert('Ошибка создания товара');
    } finally {
      setLoading(false);
    }
  };

  // Удаление товара
  const handleDeleteItem = async (id) => {
    if (window.confirm('Удалить товар?')) {
      try {
        await api.delete(`/api/v1/items/${id}`);
        await loadItems();
      } catch (err) {
        alert('Ошибка удаления');
      }
    }
  };

  // Страница загрузки
  if (userLoading) {
    return (
      <div className="container">
        <div className="loading-spinner">
          <div className="spinner"></div>
          <p>Загрузка профиля...</p>
        </div>
      </div>
    );
  }

  // Страница входа
  if (page === 'login') {
    return (
      <div className="container">
        <div className="card">
          <h2>Вход</h2>
          <form onSubmit={handleLogin}>
            <input
              type="email"
              placeholder="Email"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              required
              disabled={loading}
            />
            <input
              type="password"
              placeholder="Пароль"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              required
              disabled={loading}
            />
            <button type="submit" disabled={loading}>
              {loading ? 'Вход...' : 'Войти'}
            </button>
          </form>
          <p>
            Нет аккаунта?{' '}
            <button
              className="link"
              onClick={() => setPage('register')}
              disabled={loading}
            >
              Зарегистрироваться
            </button>
          </p>
        </div>
      </div>
    );
  }

  // Страница регистрации
  if (page === 'register') {
    return (
      <div className="container">
        <div className="card">
          <h2>Регистрация</h2>
          <form onSubmit={handleRegister}>
            <input
              type="email"
              placeholder="Email"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              required
              disabled={loading}
            />
            <input
              type="text"
              placeholder="Имя пользователя (опционально)"
              value={username}
              onChange={(e) => setUsername(e.target.value)}
              disabled={loading}
            />
            <input
              type="password"
              placeholder="Пароль"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              required
              disabled={loading}
            />
            <button type="submit" disabled={loading}>
              {loading ? 'Регистрация...' : 'Зарегистрироваться'}
            </button>
          </form>
          <p>
            Уже есть аккаунт?{' '}
            <button
              className="link"
              onClick={() => setPage('login')}
              disabled={loading}
            >
              Войти
            </button>
          </p>
        </div>
      </div>
    );
  }

  // Главная страница со списком товаров
  return (
    <div className="container">
      {/* Шапка */}
      <div className="header">
        <h1>Мои товары</h1>
        <div className="user-info">
          <div className="user-profile">
            <div className="user-avatar">
              {user?.username?.[0] || user?.email?.[0] || 'U'}
            </div>
            <div className="user-details">
              <span className="user-name">{user?.username || user?.email}</span>
              <span className="user-email">{user?.email}</span>
              {user?.full_name && (
                <span className="user-fullname">{user.full_name}</span>
              )}
              {user?.is_superuser && (
                <span className="user-badge">Admin</span>
              )}
            </div>
          </div>
          <button onClick={handleLogout} className="logout-btn" disabled={loading}>
            Выйти
          </button>
        </div>
      </div>

      {/* Форма создания товара */}
      <div className="card">
        <h3>Добавить товар</h3>
        <form onSubmit={handleCreateItem} className="create-form">
          <input
            type="text"
            placeholder="Название товара"
            value={title}
            onChange={(e) => setTitle(e.target.value)}
            required
            disabled={loading}
          />
          <textarea
            placeholder="Описание"
            value={description}
            onChange={(e) => setDescription(e.target.value)}
            rows="3"
            disabled={loading}
          />
          <button type="submit" disabled={loading}>
            {loading ? 'Добавление...' : 'Добавить'}
          </button>
        </form>
      </div>

      {/* Список товаров */}
      <div className="items-list">
        <h3>Список товаров</h3>
        {loading && <p>Загрузка...</p>}

        {!loading && items.length === 0 && (
          <p className="empty">Нет товаров. Добавьте первый!</p>
        )}

        {items.map((item) => (
          <div key={item.id} className="item-card">
            <div className="item-content">
              <h4>{item.title}</h4>
              {item.description && <p>{item.description}</p>}
              <small>ID: {item.id}</small>
            </div>
            <button
              onClick={() => handleDeleteItem(item.id)}
              className="delete-btn"
              disabled={loading}
            >
              Удалить
            </button>
          </div>
        ))}
      </div>
    </div>
  );
}

export default App;