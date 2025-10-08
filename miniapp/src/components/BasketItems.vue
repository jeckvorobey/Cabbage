<template>
  <div class="basket">
    <div v-if="prderStore.basketData?.length">
      <div class="containet">
        <q-card class="my-card q-ma-sm" flat bordered>
          <q-list v-for="(item, index) in prderStore.basketData" :key="index">
            <q-item class="q-px-xs">
              <q-item-section avatar>
                <q-img
                  class="cursor-pointer"
                  src="https://media.istockphoto.com/id/1141529240/ru/%D0%B2%D0%B5%D0%BA%D1%82%D0%BE%D1%80%D0%BD%D0%B0%D1%8F/%D0%BF%D1%80%D0%BE%D1%81%D1%82%D0%BE%D0%B5-%D1%8F%D0%B1%D0%BB%D0%BE%D0%BA%D0%BE-%D0%B2-%D0%BF%D0%BB%D0%BE%D1%81%D0%BA%D0%BE%D0%BC-%D1%81%D1%82%D0%B8%D0%BB%D0%B5-%D0%B8%D0%BB%D0%BB%D1%8E%D1%81%D1%82%D1%80%D0%B0%D1%86%D0%B8%D1%8F-%D0%B2%D0%B5%D0%BA%D1%82%D0%BE%D1%80%D0%B0.jpg?s=612x612&w=0&k=20&c=B-KXrA7VTm8E6t4jk9qcuFz8bDFzTJwiIGaYGYUcsZI="
                />
              </q-item-section>

              <q-item-section>
                <q-item-label>
                  <span class="q-mr-md">{{ item.name }}</span>
                  <span>{{ item.weight }}кг</span>
                </q-item-label>
                <q-item-label>
                  <span class="text-bold">{{ item.price }}</span> ₽
                  <span v-if="item?.oldPrice" class="text-grey old-price"
                    >{{ item.oldPrice }} ₽</span
                  >
                </q-item-label>
              </q-item-section>
              <q-item-action>
                <q-btn flat round color="red" icon="close" @click="removeItem(item)" />
              </q-item-action>
            </q-item>
            <q-separator />
          </q-list>
        </q-card>
      </div>
      <div class="q-px-sm">
        <q-btn color="secondary" class="full-width" label="Оформить заказ" />
      </div>
    </div>

    <div v-else class="text-h6 text-center text-grey">Корзина пуста</div>
  </div>
</template>

<script setup lang="ts">
import { useOrderStore } from 'src/stores/orderStore';

// const $q = useQuasar();
const prderStore = useOrderStore();
// const basketData = ref<any>([]);

// onMounted(() => {
//   basketData.value = $q.localStorage.getItem('basket');
// });

function removeItem(it: any) {
  const order = prderStore.basketData.filter((item: { id: number }) => item.id !== it.id);
  // const order = basketData.value.filter((item: { id: number }) => item.id !== it.id);
  prderStore.basketData = order;
  // $q.localStorage.set('basket', basketData.value);
}
</script>

<style scoped lang="scss">
.basket {
  .containet {
    height: 86svh;
    .old-price {
      text-decoration: line-through;
    }
  }
}
</style>
