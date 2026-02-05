import apiClient from "../../services/apiClient";

export default async function getMyProfile() {
  const res = await apiClient.get("/profile");
  return res.data;
}
