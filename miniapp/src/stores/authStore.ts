import { ref } from 'vue';
import { defineStore } from 'pinia';
import type { AxiosError } from 'axios';
import { client } from 'src/boot/axios';

export const useAuthStore = defineStore('auth', () => {
  const user = ref();
  const toWalletAddress = ref('');

  async function auth(initData: any) {
    return client
      .post(`auth`, initData)
      .then((res: { data: { token: string; toWalletAddress: string } }) => {
        localStorage.setItem('token', res.data.token);
        user.value = res.data;
        toWalletAddress.value = res.data.toWalletAddress;
        return res.data;
      })
      .catch((err: AxiosError<any>) => {
        console.error('[AuthStore] - An error occurred while fetching via auth', err.message);
        throw err;
      });
  }

  return {
    auth,
  };
});
