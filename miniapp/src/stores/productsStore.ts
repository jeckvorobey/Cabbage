import { defineStore } from 'pinia';
import { client } from 'src/boot/axios';
import { ref } from 'vue';

export const useProductsStore = defineStore('Products', () => {
  const products = ref([
    {
      id: 1,
      name: 'Груша спелая',
      img: 'https://media.istockphoto.com/id/1141529240/ru/%D0%B2%D0%B5%D0%BA%D1%82%D0%BE%D1%80%D0%BD%D0%B0%D1%8F/%D0%BF%D1%80%D0%BE%D1%81%D1%82%D0%BE%D0%B5-%D1%8F%D0%B1%D0%BB%D0%BE%D0%BA%D0%BE-%D0%B2-%D0%BF%D0%BB%D0%BE%D1%81%D0%BA%D0%BE%D0%BC-%D1%81%D1%82%D0%B8%D0%BB%D0%B5-%D0%B8%D0%BB%D0%BB%D1%8E%D1%81%D1%82%D1%80%D0%B0%D1%86%D0%B8%D1%8F-%D0%B2%D0%B5%D0%BA%D1%82%D0%BE%D1%80%D0%B0.jpg?s=612x612&w=0&k=20&c=B-KXrA7VTm8E6t4jk9qcuFz8bDFzTJwiIGaYGYUcsZI=',
      price: 12,
      discount: 0,
      weight: 1,
      quantity: 1,
    },
    {
      id: 2,
      name: 'Яблоко',
      img: 'https://media.istockphoto.com/id/1141529240/ru/%D0%B2%D0%B5%D0%BA%D1%82%D0%BE%D1%80%D0%BD%D0%B0%D1%8F/%D0%BF%D1%80%D0%BE%D1%81%D1%82%D0%BE%D0%B5-%D1%8F%D0%B1%D0%BB%D0%BE%D0%BA%D0%BE-%D0%B2-%D0%BF%D0%BB%D0%BE%D1%81%D0%BA%D0%BE%D0%BC-%D1%81%D1%82%D0%B8%D0%BB%D0%B5-%D0%B8%D0%BB%D0%BB%D1%8E%D1%81%D1%82%D1%80%D0%B0%D1%86%D0%B8%D1%8F-%D0%B2%D0%B5%D0%BA%D1%82%D0%BE%D1%80%D0%B0.jpg?s=612x612&w=0&k=20&c=B-KXrA7VTm8E6t4jk9qcuFz8bDFzTJwiIGaYGYUcsZI=',
      price: 12,
      oldPrice: 15,
      discount: 0,
      weight: 1,
      quantity: 1,
    },
    {
      id: 3,
      name: 'Cлива',
      img: 'https://media.istockphoto.com/id/1141529240/ru/%D0%B2%D0%B5%D0%BA%D1%82%D0%BE%D1%80%D0%BD%D0%B0%D1%8F/%D0%BF%D1%80%D0%BE%D1%81%D1%82%D0%BE%D0%B5-%D1%8F%D0%B1%D0%BB%D0%BE%D0%BA%D0%BE-%D0%B2-%D0%BF%D0%BB%D0%BE%D1%81%D0%BA%D0%BE%D0%BC-%D1%81%D1%82%D0%B8%D0%BB%D0%B5-%D0%B8%D0%BB%D0%BB%D1%8E%D1%81%D1%82%D1%80%D0%B0%D1%86%D0%B8%D1%8F-%D0%B2%D0%B5%D0%BA%D1%82%D0%BE%D1%80%D0%B0.jpg?s=612x612&w=0&k=20&c=B-KXrA7VTm8E6t4jk9qcuFz8bDFzTJwiIGaYGYUcsZI=',
      price: 12,
      discount: 0,
      weight: 1,
      quantity: 1,
    },
  ]);

  async function createProduct(product: any) {
    return client
      .post<any>('products', product)
      .then((res) => res.data)
      .catch((err) => {
        console.error(
          '[ProductsStore] - An error occurred while createing via product',
          err.message,
        );
        throw err;
      });
  }

  async function fetchProducts() {
    return client
      .post('products')
      .then((res) => res.data)
      .catch((err) => {
        console.error(
          '[ProductsStore] - An error occurred while fetching via products',
          err.message,
        );
        throw err;
      });
  }

  async function deleteProduct(id: number) {
    return client
      .delete(`products/${id}`)
      .then((res) => res.data)
      .catch((err) => {
        console.error(
          '[ProductsStore] - An error occurred while deleting via Product',
          err.message,
        );
        throw err;
      });
  }

  return { products, createProduct, fetchProducts, deleteProduct };
});
