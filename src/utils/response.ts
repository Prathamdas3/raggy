export type SuccessResponse<T> = {
  success: true;
  data: T;
};

export type ErrorResponse = {
  success: false;
  error: {
    message: string;
    code?: string; 
  };
};

export function success<T>(data: T): SuccessResponse<T> {
  return {
    success: true,
    data,
  };
}

export function error(message: string, code?: string): ErrorResponse {
  return {
    success: false,
    error: { message, code },
  };
}