<template>
  <div class="product-card row q-col-gutter-xs">
    <div class="col-6" v-for="(item, index) in productsStore.products" :key="index">
      <q-card class="my-card radius-12 full-height" style="border-radius: 20px" flat bordered>
        <q-card-section class="q-pa-sm full-height">
          <div>
            <q-img
              class="cursor-pointer"
              src="https://media.istockphoto.com/id/1141529240/ru/%D0%B2%D0%B5%D0%BA%D1%82%D0%BE%D1%80%D0%BD%D0%B0%D1%8F/%D0%BF%D1%80%D0%BE%D1%81%D1%82%D0%BE%D0%B5-%D1%8F%D0%B1%D0%BB%D0%BE%D0%BA%D0%BE-%D0%B2-%D0%BF%D0%BB%D0%BE%D1%81%D0%BA%D0%BE%D0%BC-%D1%81%D1%82%D0%B8%D0%BB%D0%B5-%D0%B8%D0%BB%D0%BB%D1%8E%D1%81%D1%82%D1%80%D0%B0%D1%86%D0%B8%D1%8F-%D0%B2%D0%B5%D0%BA%D1%82%D0%BE%D1%80%D0%B0.jpg?s=612x612&w=0&k=20&c=B-KXrA7VTm8E6t4jk9qcuFz8bDFzTJwiIGaYGYUcsZI="
            />
          </div>
          <q-card-section class="q-pa-sm">
            <div class="text-center card-title">{{ item.name }}</div>
            <div class="text-center">
              <span class="text-bold">{{ item.price }}</span> ₽
              <span v-if="item?.oldPrice" class="text-grey old-price">{{ item.oldPrice }} ₽</span>
              / {{ item.weight }}
            </div>
            <!-- <div class="q-mt-sm q-mb-xs text-center">
              Итого:
              <span class="text-bold">{{ item.price * item.quantity }}</span> ₽
            </div> -->
          </q-card-section>
          <q-card-actions class="justify-center">
            <!-- <q-btn padding="xs" color="secondary" icon="add" @click="item.quantity += 1" />
            <div class="q-px-md">
              {{ item.quantity }}
            </div>
            <q-btn
              :disabled="item.quantity === 1"
              padding="xs"
              color="secondary"
              icon="remove"
              @click="item.quantity -= 1"
            />
            <q-space /> -->
            <q-btn
              dense
              no-caps
              class="full-width"
              color="secondary"
              icon="add_shopping_cart"
              label="В корзину"
              @click="addOrder(item)"
            />
          </q-card-actions>
        </q-card-section>
      </q-card>
    </div>
  </div>
</template>

<script setup lang="ts">
import { useProductsStore } from 'stores/productsStore.js';
import { useOrderStore } from 'src/stores/orderStore';
import { toRaw } from 'vue';
import { useQuasar } from 'quasar';

const $q = useQuasar();
const productsStore = useProductsStore();
const prderStore = useOrderStore();

function addOrder(it: any) {
  try {
    $q.loading.show();
    if (prderStore.basketData?.length) {
      const coincidences = prderStore.basketData.find((item: any) => item.id === it.id);
      if (coincidences) {
        recalculationGoods(coincidences, it);
      } else {
        prderStore.basketData.push(structuredClone(toRaw(it)));
      }
    } else {
      prderStore.basketData.push(structuredClone(toRaw(it)));
    }
  } catch (e) {
    console.error(e);
  } finally {
    $q.notify({
      message: `Товар ${it.name} добавлен в корзину`,
      color: 'primary',
    });
    $q.loading.hide();
  }
}

function recalculationGoods(newGoods: any, oldGoods: any) {
  if (newGoods.price) newGoods.price += oldGoods.price;
  if (newGoods.weight) newGoods.weight += oldGoods.weight;
  if (newGoods.oldPrice) newGoods.oldPrice += oldGoods.oldPrice;
}
</script>

<style scoped lang="scss">
.product-card {
  .card-title {
    font-size: 18px;
    white-space: nowrap;
    overflow: hidden;
    text-overflow: ellipsis;
  }
  .old-price {
    text-decoration: line-through;
  }
}
</style>
