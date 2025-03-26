import axios from "axios"
import camelcaseKeys from "camelcase-keys"
import snakecaseKeys from "snakecase-keys"

const instance = axios.create({
    baseURL: '/',
    timeout: 600000,
    adapter: 'fetch',
    // other configurations...
});

// Add request interceptor
instance.interceptors.request.use(function (config) {
    const accessToken = localStorage.getItem('accessToken');
    if (accessToken) {
        config.headers['Authorization'] = `Bearer ${accessToken}`;
    }
    if (config.data) {
        config.data = snakecaseKeys(config.data, { deep: true })
    }
    if (config.params) {
        config.params = snakecaseKeys(config.params, { deep: true })
    }
    return config;
}, function (error) {
    // Do something with request error
    return Promise.reject(error);
});

// Response interceptor for instance
instance.interceptors.response.use(function (response) {
    // Any status code that lie within the range of 2xx cause this function to trigger
    // Do something with response data
    if (response.data) {
        response.data = camelcaseKeys(response.data, { deep: true })
    }
    return response;
}, function (error) {
    if (error.response.status === 401) {
        localStorage.removeItem('accessToken');
        window.location.href = '/';
    }
    return Promise.reject(error);
});

export default instance;