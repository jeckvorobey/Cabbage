import { defineStore } from 'pinia';
import { client } from 'src/boot/axios';

export const useOrderStore = defineStore('Order', () => {
  async function createOrder(order: any) {
    return client
      .post<any>('order', order)
      .then((res) => res.data)
      .catch((err) => {
        console.error('[OrderStore] - An error occurred while createing via order', err.message);
        throw err;
      });
  }

  return { createOrder };
});
