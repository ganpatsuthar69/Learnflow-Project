import apiClient from "../../../services/apiClient";

export interface LoginPayload {
  email: string;
  password: string;
}

export const loginRequest = async (payload: LoginPayload) => {
  const response = await apiClient.post("/login", payload);
  return response.data;
};

export interface SignupPayload {
  full_name: string;
  email: string;
  username: string
  mobile_no: string;
  password: string;
}

export const signupRequest = async (payload: SignupPayload) => {
  const response = await apiClient.post("/sign_up", payload);
  return response.data;
};

export interface VerifyOtpPayload {
  email?: string;
  otp: string;
}

export const verifyOtpRequest = async (payload: VerifyOtpPayload) => {
  const response = await apiClient.post("/sign_up/verify", payload);
  return response.data;
};

export interface forgotPasswordRequest {
  email: string
}

export const ForgotPassword = async (payload: forgotPasswordRequest)=>{
  const response = await apiClient.post("/forgotpassword", payload);
  return response.data;
};

export const resetPasswordRequest = async (payload: {
  email: string;
  otp: string;
  new_password: string;
}) => {
  const response = await apiClient.post("/reset-password",
    payload
  );
  return response.data;
};