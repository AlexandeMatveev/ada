import React, { useState, useEffect } from 'react';
import api from './api';
import './App.css';

function App() {
  // Состояния
  const [user, setUser] = useState(null);
  const [items, setItems] = useState([]);
  const [loading, setLoading] = useState(false);
  
  // Формы
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [username, setUsername] = useState('');
  const [title, setTitle] = useState('');
  const [description, setDescription] = useState('');
  
  // Какую страницу показывать
  const [page, setPage] = useState('login'); // login, register, items

  // Проверяем токен при загрузке
  useEffect(() => {
    const token = localStorage.getItem('token');
    if (token) {
      loadUser();
    }
  }, []);

  // Загружаем данные пользователя
  const loadUser = async () => {
    try {
      const res = await api.get('/api/v1/auth/me');
      setUser(res.data);
      setPage('items');
      loadItems();
    } catch (err) {
      localStorage.removeItem('token');
    }
  };

  // Загружаем список товаров
  const loadItems = async () => {
    setLoading(true);
    try {
      const res = await api.get('/api/v1/items/');
      setItems(res.data);
    } catch (err) {
      console.error('Ошибка загрузки товаров:', err);
    }
    setLoading(false);
  };

  // Регистрация
  const handleRegister = async (e) => {
    e.preventDefault();
    try {
      const res = await api.post('/api/v1/auth/register', {
        email,
        username: username || email.split('@')[0],
        password,
      });
      localStorage.setItem('token', res.data.access_token);
      loadUser();
    } catch (err) {
      alert(err.response?.data?.detail || 'Ошибка регистрации');
    }
  };

  // Вход
  const handleLogin = async (e) => {
    e.preventDefault();
    try {
      const res = await api.post('/api/v1/auth/login', { email, password });
      localStorage.setItem('token', res.data.access_token);
      loadUser();
    } catch (err) {
      alert('Неверный email или пароль');
    }
  };

  // Выход
  const handleLogout = () => {
    localStorage.removeItem('token');
    setUser(null);
    setPage('login');
    setEmail('');
    setPassword('');
  };

  // Создание товара
  const handleCreateItem = async (e) => {
    e.preventDefault();
    if (!title.trim()) return;
    
    try {
      await api.post('/api/v1/items/', { title, description });
      setTitle('');
      setDescription('');
      loadItems();
    } catch (err) {
      alert('Ошибка создания товара');
    }
  };

  // Удаление товара
  const handleDeleteItem = async (id) => {
    if (window.confirm('Удалить товар?')) {
      try {
        await api.delete(`/api/v1/items/${id}`);
        loadItems();
      } catch (err) {
        alert('Ошибка удаления');
      }
    }
  };

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
            />
            <input
              type="password"
              placeholder="Пароль"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              required
            />
            <button type="submit">Войти</button>
          </form>
          <p>
            Нет аккаунта?{' '}
            <button className="link" onClick={() => setPage('register')}>
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
            />
            <input
              type="text"
              placeholder="Имя пользователя (опционально)"
              value={username}
              onChange={(e) => setUsername(e.target.value)}
            />
            <input
              type="password"
              placeholder="Пароль"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              required
            />
            <button type="submit">Зарегистрироваться</button>
          </form>
          <p>
            Уже есть аккаунт?{' '}
            <button className="link" onClick={() => setPage('login')}>
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
          <span>Привет, {user?.username || user?.email}!</span>
          <button onClick={handleLogout} className="logout-btn">
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
          />
          <textarea
            placeholder="Описание"
            value={description}
            onChange={(e) => setDescription(e.target.value)}
            rows="3"
          />
          <button type="submit">Добавить</button>
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