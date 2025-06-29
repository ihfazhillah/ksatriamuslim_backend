import axios from 'axios';
import { Task } from '../data/mockData';
import AsyncStorage from '@react-native-async-storage/async-storage';

// Determine the base URL based on the environment
const baseURL = __DEV__
  ? 'http://10.0.2.2:8000/api/kanban/' // For Android emulator
  : 'https://cms.ihfazh.com/api/kanban/';

const apiClient = axios.create({
  baseURL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Add a request interceptor to include the token in all requests
apiClient.interceptors.request.use(
  async (config) => {
    const token = await AsyncStorage.getItem('user_token');
    if (token) {
      config.headers.Authorization = `Token ${token}`;
    }
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

export interface ChildWithTasks {
  id: string;
  name: string;
  tasks: Task[];
}

export interface BoardState {
  children: ChildWithTasks[];
}

export const getBoardState = async (): Promise<BoardState> => {
  const response = await apiClient.get('board/');
  return response.data;
};

export const updateTask = async (task: Partial<Task>): Promise<Task> => {
  const response = await apiClient.patch(`tasks/${task.id}/`, task);
  return response.data;
};

export const login = async (username: string, password: string): Promise<{ key: string }> => {
  const response = await axios.post(
    (__DEV__ ? 'http://10.0.2.2:8000/api/auth/login/' : 'https://cms.ihfazh.com/api/auth/login/'),
    { username, password },
    {
      headers: {
        'Content-Type': 'application/json',
      },
    }
  );
  return response.data;
};

export const logout = async () => {
  // You might have a logout endpoint on your backend if needed
  // await apiClient.post('logout/');
  await AsyncStorage.removeItem('user_token');
};
