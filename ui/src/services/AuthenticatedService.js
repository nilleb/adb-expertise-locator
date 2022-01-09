import axios from "axios";
import { v4 as uuidv4 } from "uuid";

const API_BASE_URL = process.env.VUE_APP_API_BASE_URL; // 'http://localhost:8080/api/v1'

export default class AuthenticatedService {
  static service() {
    const token = "Bearer yolo";
    const svc = axios.create({
      baseURL: API_BASE_URL,
      timeout: 1000,
      headers: { Authorization: token },
    });
    svc.interceptors.request.use(
      (config) => {
        const updatedConfig = config;
        updatedConfig.headers["x-request-id"] = uuidv4();
        let sessionId = uuidv4();
        if (localStorage.sessionId) {
          sessionId = localStorage.sessionId;
        } else {
          localStorage.sessionId = sessionId;
        }
        updatedConfig.headers["x-session-id"] = sessionId;
        return updatedConfig;
      },
      (error) => Promise.reject(error)
    );
    svc.interceptors.response.use(
      (response) => {
        if (response.status === 200 || response.status === 201) {
          return Promise.resolve(response);
        }
        return Promise.reject(response);
      },
      (err) =>
        new Promise(() => {
          if (
            err !== undefined &&
            err.response !== undefined &&
            err.response.status === 401
          ) {
            // FIXME: complete the suer logout
          } else {
            console.log("unexpected interceptors error: ", err);
          }
        })
    );
    return svc;
  }
}
