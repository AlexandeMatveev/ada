import React, { useState, useEffect, useCallback } from 'react';
import api from './api';
import './App.css';

function App() {
  // Состояния
  const [user, setUser] = useState(null);
  const [items, setItems] = useState([]);
  const [cart, setCart] = useState([]);
  const [orders, setOrders] = useState([]);
  const [loading, setLoading] = useState(false);
  const [userLoading, setUserLoading] = useState(true);
  const [activeTab, setActiveTab] = useState('items'); // items, cart, orders

  // Формы
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [username, setUsername] = useState('');
  const [title, setTitle] = useState('');
  const [description, setDescription] = useState('');
  const [price, setPrice] = useState('');
  const [stock, setStock] = useState('');

  // Форма заказа
  const [shippingAddress, setShippingAddress] = useState('');
  const [phone, setPhone] = useState('');
  const [notes, setNotes] = useState('');

  const [page, setPage] = useState('login');

  // Загружаем список товаров
  const loadItems = useCallback(async () => {
    setLoading(true);
    try {
      const res = await api.get('/items/');
      setItems(res.data);
    } catch (err) {
      console.error('Ошибка загрузки товаров:', err);
    }
    setLoading(false);
  }, []);

  // Загружаем заказы
  const loadOrders = useCallback(async () => {
    try {
      const res = await api.get('/orders/');
      setOrders(res.data);
    } catch (err) {
      console.error('Ошибка загрузки заказов:', err);
    }
  }, []);

  // Загружаем данные пользователя
  const loadUser = useCallback(async () => {
    setUserLoading(true);
    try {
      const res = await api.get('/auth/me');
      setUser(res.data);
      setPage('main');
      await loadItems();
      await loadOrders();
    } catch (err) {
      console.error('Error loading user:', err);
      localStorage.removeItem('accessToken');
      localStorage.removeItem('refreshToken');
      setPage('login');
    } finally {
      setUserLoading(false);
    }
  }, [loadItems, loadOrders]);

  // Проверяем токен при загрузке
  useEffect(() => {
    const accessToken = localStorage.getItem('accessToken');
    if (accessToken) {
      loadUser();
    } else {
      setUserLoading(false);
    }
  }, [loadUser]);

  // Корзина в localStorage
  useEffect(() => {
    const savedCart = localStorage.getItem('cart');
    if (savedCart) {
      setCart(JSON.parse(savedCart));
    }
  }, []);

  useEffect(() => {
    localStorage.setItem('cart', JSON.stringify(cart));
  }, [cart]);

  // Регистрация
  const handleRegister = async (e) => {
    e.preventDefault();
    setLoading(true);
    try {
      const res = await api.post('/auth/register', {
        email,
        username: username || email.split('@')[0],
        password,
      });

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
      const res = await api.post('/auth/login', { email, password });

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
        await api.post('/auth/logout', { refresh_token: refreshToken });
      }
    } catch (err) {
      console.error('Logout error:', err);
    } finally {
      localStorage.removeItem('accessToken');
      localStorage.removeItem('refreshToken');
      localStorage.removeItem('cart');
      setUser(null);
      setCart([]);
      setPage('login');
      setEmail('');
      setPassword('');
    }
  };

  // Добавление в корзину
  const addToCart = (item) => {
    const existingItem = cart.find(i => i.id === item.id);
    if (existingItem) {
      setCart(cart.map(i =>
        i.id === item.id ? { ...i, quantity: i.quantity + 1 } : i
      ));
    } else {
      setCart([...cart, { ...item, quantity: 1 }]);
    }
  };

  // Удаление из корзины
  const removeFromCart = (itemId) => {
    setCart(cart.filter(i => i.id !== itemId));
  };

  // Обновление количества
  const updateQuantity = (itemId, quantity) => {
    if (quantity <= 0) {
      removeFromCart(itemId);
    } else {
      setCart(cart.map(i =>
        i.id === itemId ? { ...i, quantity } : i
      ));
    }
  };

  // Создание заказа
  const handleCreateOrder = async (e) => {
    e.preventDefault();
    if (cart.length === 0) {
      alert('Корзина пуста');
      return;
    }

    setLoading(true);
    try {
      const orderData = {
        shipping_address: shippingAddress,
        phone: phone,
        notes: notes,
        items: cart.map(item => ({
          item_id: item.id,
          quantity: item.quantity
        }))
      };

      await api.post('/orders/', orderData);
      alert('Заказ успешно создан!');
      setCart([]);
      setShippingAddress('');
      setPhone('');
      setNotes('');
      await loadOrders();
      setActiveTab('orders');
    } catch (err) {
      alert(err.response?.data?.detail || 'Ошибка создания заказа');
    } finally {
      setLoading(false);
    }
  };

  // Создание товара (админ)
  const handleCreateItem = async (e) => {
    e.preventDefault();
    setLoading(true);
    try {
      await api.post('/items/', {
        title,
        description,
        price: parseFloat(price),
        stock: parseInt(stock)
      });
      setTitle('');
      setDescription('');
      setPrice('');
      setStock('');
      await loadItems();
      alert('Товар добавлен');
    } catch (err) {
      alert(err.response?.data?.detail || 'Ошибка создания товара');
    } finally {
      setLoading(false);
    }
  };

  // Удаление товара (админ)
  const handleDeleteItem = async (id) => {
    if (window.confirm('Удалить товар?')) {
      try {
        await api.delete(`/items/${id}`);
        await loadItems();
      } catch (err) {
        alert('Ошибка удаления');
      }
    }
  };

  // Отмена заказа
  const handleCancelOrder = async (orderId) => {
    if (window.confirm('Отменить заказ?')) {
      try {
        await api.post(`/orders/${orderId}/cancel`);
        await loadOrders();
      } catch (err) {
        alert(err.response?.data?.detail || 'Ошибка отмены заказа');
      }
    }
  };

  const getStatusColor = (status) => {
    const colors = {
      pending: '#f59e0b',
      confirmed: '#3b82f6',
      processing: '#8b5cf6',
      shipped: '#10b981',
      delivered: '#059669',
      cancelled: '#ef4444'
    };
    return colors[status] || '#6b7280';
  };

  const getStatusText = (status) => {
    const texts = {
      pending: 'Ожидает',
      confirmed: 'Подтвержден',
      processing: 'В обработке',
      shipped: 'Отправлен',
      delivered: 'Доставлен',
      cancelled: 'Отменен'
    };
    return texts[status] || status;
  };

  const cartTotal = cart.reduce((sum, item) => sum + (item.price * item.quantity), 0);

  // Страница загрузки
  if (userLoading) {
    return (
      <div className="container">
        <div className="loading-spinner">
          <div className="spinner"></div>
          <p>Загрузка...</p>
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
            <button className="link" onClick={() => setPage('register')} disabled={loading}>
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
              placeholder="Имя пользователя"
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
            <button className="link" onClick={() => setPage('login')} disabled={loading}>
              Войти
            </button>
          </p>
        </div>
      </div>
    );
  }

  // Главная страница
  return (
    <div className="container">
      <div className="header">
        <h1>Магазин</h1>
        <div className="user-info">
          <div className="user-profile">
            <div className="user-avatar">
              {user?.username?.[0] || user?.email?.[0] || 'U'}
            </div>
            <div className="user-details">
              <span className="user-name">{user?.username || user?.email}</span>
              <span className="user-email">{user?.email}</span>
              {user?.is_superuser && <span className="user-badge">Admin</span>}
            </div>
          </div>
          <button onClick={handleLogout} className="logout-btn">Выйти</button>
        </div>
      </div>

      <div className="tabs">
        <button className={activeTab === 'items' ? 'tab active' : 'tab'} onClick={() => setActiveTab('items')}>
          Товары
        </button>
        <button className={activeTab === 'cart' ? 'tab active' : 'tab'} onClick={() => setActiveTab('cart')}>
          Корзина ({cart.length})
        </button>
        <button className={activeTab === 'orders' ? 'tab active' : 'tab'} onClick={() => setActiveTab('orders')}>
          Заказы
        </button>
      </div>

      {/* Товары */}
      {activeTab === 'items' && (
        <>
          {user?.is_superuser && (
            <div className="card">
              <h3>Добавить товар</h3>
              <form onSubmit={handleCreateItem} className="create-form">
                <input
                  type="text"
                  placeholder="Название"
                  value={title}
                  onChange={(e) => setTitle(e.target.value)}
                  required
                />
                <textarea
                  placeholder="Описание"
                  value={description}
                  onChange={(e) => setDescription(e.target.value)}
                  rows="2"
                />
                <input
                  type="number"
                  placeholder="Цена"
                  value={price}
                  onChange={(e) => setPrice(e.target.value)}
                  required
                />
                <input
                  type="number"
                  placeholder="Количество"
                  value={stock}
                  onChange={(e) => setStock(e.target.value)}
                  required
                />
                <button type="submit" disabled={loading}>Добавить</button>
              </form>
            </div>
          )}

          <div className="items-grid">
            {loading && <p>Загрузка...</p>}
            {!loading && items.length === 0 && <p className="empty">Нет товаров</p>}
            {items.map(item => (
              <div key={item.id} className="item-card">
                <div className="item-image">📦</div>
                <div className="item-info">
                  <h4>{item.title}</h4>
                  {item.description && <p>{item.description}</p>}
                  <div className="item-price">{item.price} ₽</div>
                  <div className="item-stock">В наличии: {item.stock}</div>
                </div>
                <div className="item-actions">
                  <button onClick={() => addToCart(item)} className="add-to-cart-btn">
                    В корзину
                  </button>
                  {user?.is_superuser && (
                    <button onClick={() => handleDeleteItem(item.id)} className="delete-btn">
                      Удалить
                    </button>
                  )}
                </div>
              </div>
            ))}
          </div>
        </>
      )}

      {/* Корзина */}
      {activeTab === 'cart' && (
        <div className="cart-container">
          {cart.length === 0 ? (
            <div className="empty-cart">
              <p>Корзина пуста</p>
              <button onClick={() => setActiveTab('items')} className="link">
                Перейти к товарам
              </button>
            </div>
          ) : (
            <>
              <div className="cart-items">
                <h3>Товары в корзине</h3>
                {cart.map(item => (
                  <div key={item.id} className="cart-item">
                    <div className="cart-item-info">
                      <h4>{item.title}</h4>
                      <div className="cart-item-price">{item.price} ₽</div>
                    </div>
                    <div className="cart-item-quantity">
                      <button onClick={() => updateQuantity(item.id, item.quantity - 1)}>-</button>
                      <span>{item.quantity}</span>
                      <button onClick={() => updateQuantity(item.id, item.quantity + 1)}>+</button>
                    </div>
                    <div className="cart-item-total">{item.price * item.quantity} ₽</div>
                    <button onClick={() => removeFromCart(item.id)} className="remove-btn">×</button>
                  </div>
                ))}
                <div className="cart-total">
                  <strong>Итого: {cartTotal} ₽</strong>
                </div>
              </div>

              <div className="card">
                <h3>Оформление заказа</h3>
                <form onSubmit={handleCreateOrder}>
                  <textarea
                    placeholder="Адрес доставки *"
                    value={shippingAddress}
                    onChange={(e) => setShippingAddress(e.target.value)}
                    required
                    rows="3"
                  />
                  <input
                    type="tel"
                    placeholder="Телефон *"
                    value={phone}
                    onChange={(e) => setPhone(e.target.value)}
                    required
                  />
                  <textarea
                    placeholder="Комментарий"
                    value={notes}
                    onChange={(e) => setNotes(e.target.value)}
                    rows="2"
                  />
                  <button type="submit" disabled={loading}>
                    {loading ? 'Оформление...' : 'Оформить заказ'}
                  </button>
                </form>
              </div>
            </>
          )}
        </div>
      )}

      {/* Заказы */}
      {activeTab === 'orders' && (
        <div className="orders-list">
          <h3>Мои заказы</h3>
          {orders.length === 0 ? (
            <p className="empty">У вас пока нет заказов</p>
          ) : (
            orders.map(order => (
              <div key={order.id} className="order-card">
                <div className="order-header">
                  <div>
                    <span className="order-id">Заказ #{order.id}</span>
                    <span className="order-date">
                      {new Date(order.created_at).toLocaleDateString()}
                    </span>
                  </div>
                  <div>
                    <span className="order-status" style={{ backgroundColor: getStatusColor(order.status) }}>
                      {getStatusText(order.status)}
                    </span>
                    {order.status === 'pending' && (
                      <button onClick={() => handleCancelOrder(order.id)} className="cancel-order-btn">
                        Отменить
                      </button>
                    )}
                  </div>
                </div>
                <div className="order-body">
                  <div><strong>Адрес:</strong> {order.shipping_address}</div>
                  <div><strong>Телефон:</strong> {order.phone}</div>
                  {order.notes && <div><strong>Комментарий:</strong> {order.notes}</div>}
                  <div className="order-items">
                    <strong>Товары:</strong>
                    <ul>
                      {order.items?.map(item => (
                        <li key={item.id}>
                          {item.item_title} x {item.quantity} = {item.price_at_time * item.quantity} ₽
                        </li>
                      ))}
                    </ul>
                  </div>
                </div>
                <div className="order-footer">
                  <div className="order-total">Итого: <strong>{order.total_amount} ₽</strong></div>
                </div>
              </div>
            ))
          )}
        </div>
      )}
    </div>
  );
}

export default App;