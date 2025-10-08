<template>
  <q-item
    v-if="!children"
    clickable
    tag="a"
    target="_blank"
    @click="router.push(path)"
    :class="path === route.name ? 'active-menu-item' : ''"
  >
    <q-item-section v-if="icon" avatar>
      <q-icon :name="icon" />
    </q-item-section>

    <q-item-section>
      <q-item-label>{{ title }}</q-item-label>
    </q-item-section>
  </q-item>
  <template v-if="children">
    <q-list>
      <q-expansion-item :icon="icon" :label="title">
        <div class="q-pl-md">
          <MenuItems v-for="child in children" :key="child.title" v-bind="child" />
        </div>
      </q-expansion-item>
    </q-list>
  </template>
</template>

<script setup lang="ts">
import { useRoute, useRouter } from 'vue-router';

const route = useRoute();

export interface IMenuItems {
  title: string;
  path?: string;
  icon?: string;
  children?: IMenuItems[];
}

withDefaults(defineProps<IMenuItems>(), {
  path: '#',
  icon: '',
});
const router = useRouter();
</script>

<style scoped lang="scss">
.active-menu-item {
  background-color: #8080802b;
}
</style>
