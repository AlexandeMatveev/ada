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
    if (savedCart) setCart(JSON.parse(savedCart));
  }, []);
  useEffect(() => {
    localStorage.setItem('cart', JSON.stringify(cart));
  }, [cart]);

  // Регистрация
  const handleRegister = async (e) => {
    e.preventDefault();
    setLoading(true);
    try {
      const res = await api.post('/auth/register', { email, username: username || email.split('@')[0], password });
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
      if (refreshToken) await api.post('/auth/logout', { refresh_token: refreshToken });
    } catch (err) { console.error(err); }
    localStorage.removeItem('accessToken');
    localStorage.removeItem('refreshToken');
    localStorage.removeItem('cart');
    setUser(null);
    setCart([]);
    setPage('login');
  };

  // Корзина
  const addToCart = (item) => {
    const existing = cart.find(i => i.id === item.id);
    if (existing) {
      setCart(cart.map(i => i.id === item.id ? { ...i, quantity: i.quantity + 1 } : i));
    } else {
      setCart([...cart, { ...item, quantity: 1 }]);
    }
  };
  const removeFromCart = (id) => setCart(cart.filter(i => i.id !== id));
  const updateQuantity = (id, delta) => {
    const newCart = cart.map(i => {
      if (i.id !== id) return i;
      const newQty = i.quantity + delta;
      return newQty > 0 ? { ...i, quantity: newQty } : null;
    }).filter(Boolean);
    setCart(newCart);
  };

  // Создание заказа
  const handleCreateOrder = async (e) => {
    e.preventDefault();
    if (cart.length === 0) return alert('Корзина пуста');
    setLoading(true);
    try {
      await api.post('/orders/', {
        shipping_address: shippingAddress,
        phone,
        notes,
        items: cart.map(i => ({ item_id: i.id, quantity: i.quantity }))
      });
      alert('Заказ оформлен!');
      setCart([]);
      setShippingAddress('');
      setPhone('');
      setNotes('');
      await loadOrders();
      setActiveTab('orders');
    } catch (err) {
      alert(err.response?.data?.detail || 'Ошибка оформления заказа');
    } finally {
      setLoading(false);
    }
  };

  // Админ: создание товара
  const handleCreateItem = async (e) => {
    e.preventDefault();
    if (!user?.is_superuser) return alert('Нет прав');
    setLoading(true);
    try {
      await api.post('/items/', { title, description, price: parseFloat(price), stock: parseInt(stock) });
      setTitle(''); setDescription(''); setPrice(''); setStock('');
      await loadItems();
      alert('Товар добавлен');
    } catch (err) {
      alert('Ошибка добавления товара');
    } finally {
      setLoading(false);
    }
  };

  const handleDeleteItem = async (id) => {
    if (!user?.is_superuser) return;
    if (window.confirm('Удалить товар?')) {
      try {
        await api.delete(`/items/${id}`);
        await loadItems();
      } catch (err) { alert('Ошибка удаления'); }
    }
  };

  // Отмена заказа
  const handleCancelOrder = async (orderId) => {
    if (window.confirm('Отменить заказ?')) {
      try {
        await api.post(`/orders/${orderId}/cancel`);
        await loadOrders();
      } catch (err) { alert(err.response?.data?.detail || 'Ошибка отмены'); }
    }
  };

  const getStatusColor = (status) => {
    const colors = { pending: '#f59e0b', confirmed: '#3b82f6', processing: '#8b5cf6', shipped: '#10b981', delivered: '#059669', cancelled: '#ef4444' };
    return colors[status] || '#6b7280';
  };
  const getStatusText = (status) => {
    const texts = { pending: 'Ожидает', confirmed: 'Подтвержден', processing: 'В обработке', shipped: 'Отправлен', delivered: 'Доставлен', cancelled: 'Отменен' };
    return texts[status] || status;
  };

  const cartTotal = cart.reduce((sum, i) => sum + (i.price * i.quantity), 0);

  if (userLoading) return <div className="container"><div className="loading-spinner"><div className="spinner"></div><p>Загрузка...</p></div></div>;
  if (page === 'login') return
  if (page === 'register') return

  return (
    <div className="container">
      <div className="header">
        <h1>Магазин</h1>
        <div className="user-info">
          <div className="user-profile">
            <div className="user-avatar">{user?.username?.[0] || user?.email?.[0]}</div>
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
        <button className={activeTab === 'items' ? 'tab active' : 'tab'} onClick={() => setActiveTab('items')}>Товары</button>
        <button className={activeTab === 'cart' ? 'tab active' : 'tab'} onClick={() => setActiveTab('cart')}>Корзина ({cart.length})</button>
        <button className={activeTab === 'orders' ? 'tab active' : 'tab'} onClick={() => setActiveTab('orders')}>Заказы</button>
      </div>

      {activeTab === 'items' && (
        <>
          {user?.is_superuser && (
            <div className="card">
              <h3>Добавить товар</h3>
              <form onSubmit={handleCreateItem}>
                <input placeholder="Название" value={title} onChange={e => setTitle(e.target.value)} required />
                <textarea placeholder="Описание" value={description} onChange={e => setDescription(e.target.value)} />
                <input type="number" placeholder="Цена" value={price} onChange={e => setPrice(e.target.value)} required />
                <input type="number" placeholder="Количество" value={stock} onChange={e => setStock(e.target.value)} required />
                <button type="submit">Добавить</button>
              </form>
            </div>
          )}
          <div className="items-grid">
            {items.map(item => (
              <div key={item.id} className="item-card">
                <div className="item-info">
                  <h4>{item.title}</h4>
                  <p>{item.description}</p>
                  <div className="item-price">{item.price} ₽</div>
                  <div>В наличии: {item.stock}</div>
                </div>
                <button onClick={() => addToCart(item)} className="add-to-cart-btn">В корзину</button>
                {user?.is_superuser && <button onClick={() => handleDeleteItem(item.id)} className="delete-btn">Удалить</button>}
              </div>
            ))}
          </div>
        </>
      )}

      {activeTab === 'cart' && (
        <div className="cart-container">
          {cart.length === 0 ? <div className="empty-cart"><p>Корзина пуста</p><button onClick={() => setActiveTab('items')} className="link">Перейти к товарам</button></div> : (
            <>
              <div className="cart-items">
                {cart.map(item => (
                  <div key={item.id} className="cart-item">
                    <div><strong>{item.title}</strong><br/>{item.price} ₽</div>
                    <div>
                      <button onClick={() => updateQuantity(item.id, -1)}>-</button>
                      <span>{item.quantity}</span>
                      <button onClick={() => updateQuantity(item.id, 1)}>+</button>
                    </div>
                    <div>{item.price * item.quantity} ₽</div>
                    <button onClick={() => removeFromCart(item.id)} className="remove-btn">×</button>
                  </div>
                ))}
                <div className="cart-total">Итого: {cartTotal} ₽</div>
              </div>
              <div className="card">
                <h3>Оформление заказа</h3>
                <form onSubmit={handleCreateOrder}>
                  <textarea placeholder="Адрес доставки *" value={shippingAddress} onChange={e => setShippingAddress(e.target.value)} required rows="2" />
                  <input placeholder="Телефон *" value={phone} onChange={e => setPhone(e.target.value)} required />
                  <textarea placeholder="Комментарий" value={notes} onChange={e => setNotes(e.target.value)} rows="2" />
                  <button type="submit" disabled={loading}>{loading ? 'Оформление...' : 'Оформить заказ'}</button>
                </form>
              </div>
            </>
          )}
        </div>
      )}

      {activeTab === 'orders' && (
        <div className="orders-list">
          <h3>Мои заказы</h3>
          {orders.length === 0 && <p className="empty">У вас пока нет заказов</p>}
          {orders.map(order => (
            <div key={order.id} className="order-card">
              <div className="order-header">
                <span>Заказ #{order.id} от {new Date(order.created_at).toLocaleDateString()}</span>
                <span className="order-status" style={{backgroundColor: getStatusColor(order.status)}}>{getStatusText(order.status)}</span>
              </div>
              <div className="order-body">
                <div><strong>Адрес:</strong> {order.shipping_address}</div>
                <div><strong>Телефон:</strong> {order.phone}</div>
                {order.notes && <div><strong>Комментарий:</strong> {order.notes}</div>}
                <div><strong>Товары:</strong></div>
                <ul>
                  {order.items?.map(item => <li key={item.id}>{item.item_title} x {item.quantity} = {item.price_at_time * item.quantity} ₽</li>)}
                </ul>
              </div>
              <div className="order-footer">Итого: <strong>{order.total_amount} ₽</strong></div>
              {order.status === 'pending' && <button onClick={() => handleCancelOrder(order.id)} className="cancel-order-btn">Отменить</button>}
            </div>
          ))}
        </div>
      )}
    </div>
  );
}

export default App;