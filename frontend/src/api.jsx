// api.js
import axios from 'axios';

const api = axios.create({
  baseURL: 'http://localhost:8000',
});

// Флаг для предотвращения множественных обновлений токена
let isRefreshing = false;
let failedQueue = [];

// Обработка очереди запросов
const processQueue = (error, token = null) => {
  failedQueue.forEach(prom => {
    if (error) {
      prom.reject(error);
    } else {
      prom.resolve(token);
    }
  });
  failedQueue = [];
};

// Добавляем токен к каждому запросу
api.interceptors.request.use((config) => {
  const accessToken = localStorage.getItem('accessToken');
  if (accessToken) {
    config.headers.Authorization = `Bearer ${accessToken}`;
  }
  return config;
});

// Перехватываем ответы и обновляем токен при 401
api.interceptors.response.use(
  (response) => response,
  async (error) => {
    const originalRequest = error.config;

    // Если ошибка 401 и запрос не повторялся
    if (error.response?.status === 401 && !originalRequest._retry) {
      if (isRefreshing) {
        // Если уже обновляем токен, добавляем запрос в очередь
        return new Promise((resolve, reject) => {
          failedQueue.push({ resolve, reject });
        })
          .then((token) => {
            originalRequest.headers.Authorization = `Bearer ${token}`;
            return api(originalRequest);
          })
          .catch((err) => Promise.reject(err));
      }

      originalRequest._retry = true;
      isRefreshing = true;

      const refreshToken = localStorage.getItem('refreshToken');

      // Пробуем обновить токен
      try {
        const response = await axios.post('http://localhost:8000/api/v1/auth/refresh', {
          refresh_token: refreshToken
        });

        const { access_token } = response.data;
        localStorage.setItem('accessToken', access_token);

        // Обновляем заголовок и повторяем запрос
        originalRequest.headers.Authorization = `Bearer ${access_token}`;

        // Обрабатываем очередь запросов
        processQueue(null, access_token);

        return api(originalRequest);
      } catch (refreshError) {
        // Если refresh токен тоже истек - разлогиниваем
        processQueue(refreshError, null);
        localStorage.removeItem('accessToken');
        localStorage.removeItem('refreshToken');
        window.location.href = '/login';
        return Promise.reject(refreshError);
      } finally {
        isRefreshing = false;
      }
    }

    return Promise.reject(error);
  }
);

export default api;