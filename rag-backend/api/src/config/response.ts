export type SuccessResponse<T> = {
	status: "success" | string;
	message: string;
	data: T;
};
export function success<T>(
	data: T,
	message: string,
	status: string,
): SuccessResponse<T> {
	return {
		status: status || "success",
		message,
		data,
	};
}
export type ErrorResponse = {
	success: false;
	error: {
		message: string;
		code?: string;
	};
};


export function error(message: string, code?: string): ErrorResponse {
	return {
		success: false,
		error: { message, code },
	};
}