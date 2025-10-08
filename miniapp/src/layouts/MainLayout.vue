<template>
  <q-layout view="lHh Lpr lFf">
    <q-header elevated>
      <q-toolbar class="bg-header">
        <q-btn flat dense round icon="menu" aria-label="Menu" @click="toggleLeftDrawer" />

        <q-toolbar-title>
          <div v-if="!showSearch">Shop</div>
          <div v-else>
            <q-input dense dark borderless rounded outlined v-model="textSearch">
              <template v-slot:append>
                <q-icon name="clear" @click="showSearch = !showSearch" />
              </template>
            </q-input>
          </div>
        </q-toolbar-title>

        <q-btn
          class="q-mr-md"
          flat
          dense
          round
          icon="search"
          aria-label="search"
          @click="showSearch = !showSearch"
        />
        <q-btn
          flat
          dense
          round
          icon="shopping_cart_checkout"
          aria-label="cart"
          @click="drawerRight = !drawerRight"
        />
        <div></div>
      </q-toolbar>
    </q-header>

    <q-drawer v-model="leftDrawerOpen" show-if-above bordered>
      <q-list>
        <q-item-label header>
          <div class="row justify-between">
            <div class="text-h6">Меню</div>
            <div>
              <q-btn-toggle
                v-model="themeData"
                size="sm"
                no-caps
                unelevated
                dense
                toggle-color="grey-9"
                color="white"
                text-color="grey-9"
                :options="[
                  { value: 'dark', slot: 'dark', title: 'Dark mode' },
                  { value: 'light', slot: 'light', title: 'Light mode' },
                ]"
                @click="themeToggle()"
              >
                <template v-slot:dark>
                  <div class="items-center">
                    <q-icon name="nightlight" />
                  </div>
                </template>

                <template v-slot:light>
                  <div class="items-center">
                    <q-icon name="light_mode" />
                  </div>
                </template>
              </q-btn-toggle>
            </div>
          </div>
        </q-item-label>

        <MenuItems v-for="link in menuList" :key="link.title" v-bind="link" />
      </q-list>
    </q-drawer>

    <q-drawer side="right" v-model="drawerRight" show-if-above bordered>
      <q-list>
        <q-item-label class="text-h6" header>Kорзина</q-item-label>
        <BasketItems />
      </q-list>
    </q-drawer>

    <q-page-container>
      <router-view />
    </q-page-container>
  </q-layout>
</template>

<script setup lang="ts">
import { computed, onMounted, ref, shallowReactive } from 'vue';
import MenuItems, { type IMenuItems } from 'components/MenuItems.vue';
import BasketItems from 'components/BasketItems.vue';
import { Dark, useQuasar } from 'quasar';
import { useAuthStore } from 'src/stores/authStore';
import { admin, maneger, accessLevel } from 'src/use/useUtils';

Dark.set(false);
const $q = useQuasar();
const authStore = useAuthStore();
type Theme = 'dark' | 'light';
const themeData = ref('dark');
const showSearch = ref(false);
const textSearch = ref();
const leftDrawerOpen = ref(false);
const drawerRight = ref(false);
const themeState = shallowReactive<Record<Theme, Theme>>({
  dark: 'dark',
  light: 'light',
});
const isDark = computed(() => Dark.isActive);
const themeStatus = computed(() => (isDark.value ? themeState.dark : themeState.light));
const themeToggle = () => {
  Dark.toggle();
  window.localStorage.setItem('theme', themeStatus.value);
};

const tgUser = ref();

const menuList: IMenuItems[] = [
  {
    title: 'Главная',
    icon: 'home',
    name: '/',
    path: '/',
  },
  {
    title: 'Добавить категорию',
    icon: 'home',
    name: '',
    action: 'add-category',
    disabled: !admin.value || !maneger.value,
  },
  {
    title: 'Каталог',
    icon: 'reorder',
    children: [
      {
        category_id: 1,
        title: 'Овощи',
        icon: 'play_arrow',
        name: '',
        path: '/',
      },
      {
        category_id: 2,
        title: 'Фрукты',
        icon: 'play_arrow',
        name: '',
        path: '/',
      },
      {
        category_id: 3,
        title: 'Хлеб',
        icon: 'play_arrow',
        name: '',
        path: '/',
      },
    ],
  },
  {
    title: 'Доставка и оплата',
    icon: 'local_shipping',
    name: '',
    path: '',
  },
  {
    title: 'История заказов',
    icon: 'history',
    name: 'history',
    path: 'history',
  },
  {
    title: 'Мой кабинет',
    icon: 'perm_identity',
    name: 'user',
    path: 'user',
  },
  {
    title: 'Пользователи',
    icon: 'people',
    name: 'users',
    path: 'users',
    disabled: !admin.value,
  },
];

onMounted(() => {
  tgUser.value = window?.Telegram?.WebApp?.initData;
  getUser();
});

async function getUser() {
  try {
    $q.loading.show();
    const data = await authStore.auth(tgUser.value);
    accessLevel(data);
  } catch (e: any) {
    console.error(e);
  } finally {
    $q.loading.hide();
  }
}

function toggleLeftDrawer() {
  leftDrawerOpen.value = !leftDrawerOpen.value;
}
</script>
