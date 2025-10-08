<template>
  <q-item
    v-if="!children && !disabled"
    clickable
    tag="a"
    target="_blank"
    @click="actionMenu(path, action, category_id)"
    :class="name === route.name ? 'active-menu-item' : ''"
  >
    <q-item-section v-if="icon" avatar>
      <q-icon :name="icon" />
    </q-item-section>

    <q-item-section>
      <div class="row justify-between">
        <div class="content-center">
          {{ title }}
        </div>
        <q-btn
          v-if="deleted && (admin || maneger)"
          flat
          round
          color="red"
          icon="delete"
          @click="deleteCategory(category_id)"
        />
      </div>
    </q-item-section>
  </q-item>
  <template v-if="children">
    <q-list>
      <q-expansion-item :icon="icon" :label="title">
        <div class="q-pl-md">
          <MenuItems v-for="child in children" :key="child.title" :deleted="true" v-bind="child" />
        </div>
      </q-expansion-item>
    </q-list>
  </template>
  <q-dialog v-model="categoryModal">
    <q-card>
      <q-card-section>
        <div class="text-h6">Добавить категорию</div>
      </q-card-section>

      <q-card-section class="q-pt-none">
        <q-input v-model="categoryName" label="Наиминование категории" />
      </q-card-section>

      <q-card-actions align="right">
        <q-btn flat label="Отмена" color="negative" v-close-popup />
        <q-btn flat label="Добавить" color="primary" v-close-popup @click="addCategory()" />
      </q-card-actions>
    </q-card>
  </q-dialog>
</template>

<script setup lang="ts">
import { useQuasar } from 'quasar';
import { useCategoriesStore } from 'src/stores/categoriesStore';
import { ref } from 'vue';
import { useRoute, useRouter } from 'vue-router';
import { admin, maneger } from 'src/use/useUtils';
import { useProductsStore } from 'src/stores/productsStore';

export interface IMenuItems {
  title: string;
  path?: string;
  icon?: string;
  children?: IMenuItems[];
  action?: string;
  disabled?: boolean;
  deleted?: boolean;
  category_id?: number;
  name?: string;
}

withDefaults(defineProps<IMenuItems>(), {
  deleted: false,
  path: '#',
  icon: '',
});
const $q = useQuasar();
const router = useRouter();
const route = useRoute();
const categoriesStore = useCategoriesStore();
const productsStore = useProductsStore();
const categoryModal = ref(false);
const categoryName = ref('');

function actionMenu(path?: string, action?: string, category_id?: number) {
  if (action) categoryModal.value = !categoryModal.value;
  if (category_id) fetchProducts(category_id);
  if (path) router.push(path);
}

async function fetchProducts(id: number) {
  try {
    $q.loading.show();
    console.log(id);
    await productsStore.fetchProducts();
  } catch (e: any) {
    console.error(e);
  } finally {
    $q.loading.hide();
  }
}

async function addCategory() {
  try {
    $q.loading.show();
    const res = await categoriesStore.createCategories(categoryName.value);
    if (res) {
      $q.notify({
        message: `Категория успешно добавлена`,
        color: 'primary',
      });
    }
  } catch (e: any) {
    console.error(e);
  } finally {
    $q.loading.hide();
  }
}

function deleteCategory(id?: number) {
  console.log(id);
}
</script>

<style scoped lang="scss">
.active-menu-item {
  background-color: #8080802b;
}
</style>
