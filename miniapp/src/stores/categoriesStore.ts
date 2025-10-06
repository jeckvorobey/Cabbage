import { defineStore } from 'pinia';
import { client } from 'src/boot/axios';

export const useCategoriesStore = defineStore('Categories', () => {
  async function createCategories(Categori: any) {
    return client
      .post<any>('categories', Categori)
      .then((res) => res.data)
      .catch((err) => {
        console.error(
          '[CategoriesStore] - An error occurred while createing via Categori',
          err.message,
        );
        throw err;
      });
  }

  async function deleteCategories(id: number) {
    return client
      .delete(`categories/${id}`)
      .then((res) => res.data)
      .catch((err) => {
        console.error(
          '[CategoriesStore] - An error occurred while deleting via Categori',
          err.message,
        );
        throw err;
      });
  }

  return { createCategories, deleteCategories };
});
