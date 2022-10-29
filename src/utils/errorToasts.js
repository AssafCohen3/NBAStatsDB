

import { useToast } from 'vue-toastification';

export function toastError(axiosError){
	const toast = useToast();
	toast.error(axiosError.data);
}

export function toastSuccess(message){
	const toast = useToast();
	toast.success(message);
}