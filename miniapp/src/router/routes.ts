import type { RouteRecordRaw } from 'vue-router';

const routes: RouteRecordRaw[] = [
  {
    path: '/',
    component: () => import('layouts/MainLayout.vue'),
    children: [
      { path: '', name: '/', component: () => import('pages/DashboardPage.vue') },
      { path: '/user', name: 'user', component: () => import('pages/UserPage.vue') },
      { path: '/users', name: 'users', component: () => import('pages/UsersPage.vue') },
      { path: '/history', name: 'history', component: () => import('pages/OrderHistoryPage.vue') },
    ],
  },

  // Always leave this as last one,
  // but you can also remove it
  {
    path: '/:catchAll(.*)*',
    component: () => import('pages/ErrorNotFound.vue'),
  },
];

export default routes;
