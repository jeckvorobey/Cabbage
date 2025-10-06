import { defineBoot } from '@quasar/app-vite/wrappers';
import axios from 'axios';
import type { AxiosInstance } from 'axios';

declare module 'vue' {
  interface ComponentCustomProperties {
    $axios: AxiosInstance;
    $api: AxiosInstance;
  }
}

const client = axios.create({
  baseURL: `/tg/webapp/`,
  timeout: 10000,
});

client.interceptors.request.use((request) => {
  // Из запроса удаляются заголовки xsrf для запроса к сервису https://dadata.ru
  if (request.headers.Authorization) {
    delete request.xsrfHeaderName;
    delete request.xsrfCookieName;
    delete request.withCredentials;
    delete request.withXSRFToken;
  }

  if (!request.headers.SkipAuth) {
    request.headers.Authorization = 'Bearer ' + localStorage.getItem('token');
  }

  return request;
});

export default defineBoot(({ app }) => {
  app.config.globalProperties.$axios = axios;
  app.config.globalProperties.$api = client;
});

export { client };
