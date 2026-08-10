const BASE_URL = import.meta.env.VITE_TODOS_SERVICE_URL ?? 'http://localhost:8002/api/v1';

export type TodoStatus = 'pending' | 'in_progress' | 'done';

export interface TodoRead {
  id: string;
  title: string;
  description: string | null;
  status: TodoStatus;
  is_completed: boolean;
  due_date: string | null;
  user_id: string;
  created_at: string;
  updated_at: string;
}

export interface TodoListResponse {
  items: TodoRead[];
  total: number;
  skip: number;
  limit: number;
}

export interface CreateTodoPayload {
  title: string;
  description?: string;
  status?: TodoStatus;
  due_date?: string;
  user_id: string;
}

export interface UpdateTodoPayload {
  title?: string;
  description?: string;
  status?: TodoStatus;
  is_completed?: boolean;
  due_date?: string;
}

async function request<T>(path: string, options: RequestInit = {}): Promise<T> {
  const res = await fetch(`${BASE_URL}${path}`, {
    headers: { 'Content-Type': 'application/json', ...options.headers },
    ...options,
  });
  if (!res.ok) {
    const error = await res.json().catch(() => ({ detail: 'Unknown error' }));
    throw new Error(error.detail ?? `HTTP ${res.status}`);
  }
  if (res.status === 204) return undefined as T;
  return res.json();
}

export const todosApi = {
  listByUser: (userId: string, skip = 0, limit = 100) =>
    request<TodoListResponse>(`/todos/user/${userId}?skip=${skip}&limit=${limit}`),

  create: (payload: CreateTodoPayload) =>
    request<TodoRead>('/todos', {
      method: 'POST',
      body: JSON.stringify(payload),
    }),

  update: (todoId: string, payload: UpdateTodoPayload) =>
    request<TodoRead>(`/todos/${todoId}`, {
      method: 'PATCH',
      body: JSON.stringify(payload),
    }),

  delete: (todoId: string) =>
    request<void>(`/todos/${todoId}`, { method: 'DELETE' }),
};
