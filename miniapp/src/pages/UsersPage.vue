<template>
  <div>
    <h6 class="text-center q-mt-md q-mb-md">Пользователи</h6>
    <q-card class="my-card q-ma-sm" flat bordered>
      <q-list v-for="(user, index) in users" :key="index">
        <q-item>
          <q-item-section avatar>
            <q-icon color="primary" name="local_bar" />
          </q-item-section>

          <q-item-section>
            <q-item-label>{{ user.name }}</q-item-label>
            <q-item-label caption>{{ user.phone }}</q-item-label>
          </q-item-section>
          <q-item-action>
            <q-btn flat round color="red" icon="disabled_visible" />
            <q-btn flat round color="primary" icon="mode_edit" />
          </q-item-action>
        </q-item>
        <q-separator />
      </q-list>
    </q-card>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue';

const users = ref([
  {
    image: '',
    name: 'Игорь',
    phone: '+7078 000 00 00',
  },
  {
    image: '',
    name: 'Игорь',
    phone: '+7078 000 00 00',
  },
]);
</script>
