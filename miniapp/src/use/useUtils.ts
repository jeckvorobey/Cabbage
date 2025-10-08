import { ref } from 'vue';
export enum EPermissionTypes {
  ADMIN = '1',
  MANAGER = '2',
}

const admin = ref<boolean>(false);
const maneger = ref<boolean>(false);

function accessLevel(data: any) {
  switch (data.role) {
    case EPermissionTypes.ADMIN:
      admin.value = true;
      break;
    case EPermissionTypes.MANAGER:
      maneger.value = true;
      break;
    default:
      break;
  }
}

export { admin, maneger, accessLevel };
