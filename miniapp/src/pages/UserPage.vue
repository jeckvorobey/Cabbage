<template>
  <div>
    <h6 class="text-center q-mt-md q-mb-md">Личный кабинет</h6>
    <div class="q-pa-sm">
      <q-card class="my-card full-height" flat bordered>
        <q-card-section>
          <div class="text-h6">Ваши данные:</div>
          <q-input class="q-mb-sm" rounded outlined v-model="userData.name" label="Имя" />
          <q-input class="q-mb-sm" rounded outlined v-model="userData.phone" label="Телефон" />
          <q-input class="q-mb-sm" rounded outlined v-model="userData.mail" label="Mail" />
          <q-input class="q-mb-sm" rounded outlined v-model="userData.addres" label="Адрес" />
        </q-card-section>
      </q-card>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue';

const userData = ref({
  name: '',
  mail: '',
  phone: '',
  addres: '',
});
</script>
