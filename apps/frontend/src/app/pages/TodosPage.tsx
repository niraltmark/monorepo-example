import { useCallback, useEffect, useState } from 'react';
import { todosApi, type CreateTodoPayload, type TodoRead, type TodoStatus } from '../api/todosApi';
import { useAuth } from '../contexts/AuthContext';

const STATUS_LABELS: Record<TodoStatus, string> = {
  pending: 'Pending',
  in_progress: 'In Progress',
  done: 'Done',
};

const STATUS_COLORS: Record<TodoStatus, string> = {
  pending: '#f59e0b',
  in_progress: '#3b82f6',
  done: '#10b981',
};

export function TodosPage() {
  const { user, logout } = useAuth();
  const [todos, setTodos] = useState<TodoRead[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [showForm, setShowForm] = useState(false);
  const [newTodo, setNewTodo] = useState<Omit<CreateTodoPayload, 'user_id'>>({
    title: '',
    description: '',
    status: 'pending',
  });

  const fetchTodos = useCallback(async () => {
    if (!user) return;
    try {
      setLoading(true);
      const { items } = await todosApi.listByUser(user.id);
      setTodos(items);
    } catch (err: unknown) {
      setError(err instanceof Error ? err.message : 'Failed to load todos');
    } finally {
      setLoading(false);
    }
  }, [user]);

  useEffect(() => {
    fetchTodos();
  }, [fetchTodos]);

  const handleCreate = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!user) return;
    try {
      const created = await todosApi.create({ ...newTodo, user_id: user.id });
      setTodos((prev) => [created, ...prev]);
      setNewTodo({ title: '', description: '', status: 'pending' });
      setShowForm(false);
    } catch (err: unknown) {
      setError(err instanceof Error ? err.message : 'Failed to create todo');
    }
  };

  const handleToggleComplete = async (todo: TodoRead) => {
    try {
      const updated = await todosApi.update(todo.id, {
        is_completed: !todo.is_completed,
        status: !todo.is_completed ? 'done' : 'pending',
      });
      setTodos((prev) => prev.map((t) => (t.id === todo.id ? updated : t)));
    } catch (err: unknown) {
      setError(err instanceof Error ? err.message : 'Failed to update todo');
    }
  };

  const handleStatusChange = async (todo: TodoRead, status: TodoStatus) => {
    try {
      const updated = await todosApi.update(todo.id, {
        status,
        is_completed: status === 'done',
      });
      setTodos((prev) => prev.map((t) => (t.id === todo.id ? updated : t)));
    } catch (err: unknown) {
      setError(err instanceof Error ? err.message : 'Failed to update status');
    }
  };

  const handleDelete = async (todoId: string) => {
    if (!window.confirm('Delete this todo?')) return;
    try {
      await todosApi.delete(todoId);
      setTodos((prev) => prev.filter((t) => t.id !== todoId));
    } catch (err: unknown) {
      setError(err instanceof Error ? err.message : 'Failed to delete todo');
    }
  };

  const pending = todos.filter((t) => t.status === 'pending');
  const inProgress = todos.filter((t) => t.status === 'in_progress');
  const done = todos.filter((t) => t.status === 'done');

  return (
    <div className="todos-layout">
      <header className="todos-header">
        <div>
          <h1>My Todos</h1>
          <p className="user-info">
            Signed in as <strong>{user?.username}</strong> ({user?.email})
          </p>
        </div>
        <div className="header-actions">
          <button onClick={() => setShowForm((v) => !v)} className="btn-primary">
            {showForm ? 'Cancel' : '+ New Todo'}
          </button>
          <button onClick={logout} className="btn-secondary">
            Sign Out
          </button>
        </div>
      </header>

      {error && (
        <div className="error-banner" onClick={() => setError(null)}>
          {error} (click to dismiss)
        </div>
      )}

      {showForm && (
        <form onSubmit={handleCreate} className="todo-form">
          <h2>New Todo</h2>
          <label>
            Title *
            <input
              type="text"
              value={newTodo.title}
              onChange={(e) => setNewTodo((p) => ({ ...p, title: e.target.value }))}
              required
              maxLength={255}
            />
          </label>
          <label>
            Description
            <textarea
              value={newTodo.description}
              onChange={(e) => setNewTodo((p) => ({ ...p, description: e.target.value }))}
              rows={3}
              maxLength={2000}
            />
          </label>
          <label>
            Status
            <select
              value={newTodo.status}
              onChange={(e) =>
                setNewTodo((p) => ({ ...p, status: e.target.value as TodoStatus }))
              }
            >
              {(Object.keys(STATUS_LABELS) as TodoStatus[]).map((s) => (
                <option key={s} value={s}>
                  {STATUS_LABELS[s]}
                </option>
              ))}
            </select>
          </label>
          <button type="submit" className="btn-primary">
            Create Todo
          </button>
        </form>
      )}

      {loading ? (
        <p className="loading-text">Loading todos…</p>
      ) : todos.length === 0 ? (
        <div className="empty-state">
          <p>No todos yet. Create your first one!</p>
        </div>
      ) : (
        <div className="kanban-board">
          {([
            ['Pending', pending],
            ['In Progress', inProgress],
            ['Done', done],
          ] as [string, TodoRead[]][]).map(([label, items]) => (
            <div key={label} className="kanban-column">
              <h2 className="column-title">
                {label}
                <span className="column-count">{items.length}</span>
              </h2>
              <div className="todo-list">
                {items.map((todo) => (
                  <div
                    key={todo.id}
                    className={`todo-card ${todo.is_completed ? 'completed' : ''}`}
                  >
                    <div className="todo-card-header">
                      <input
                        type="checkbox"
                        checked={todo.is_completed}
                        onChange={() => handleToggleComplete(todo)}
                        title="Mark complete"
                      />
                      <span
                        className="status-badge"
                        style={{ backgroundColor: STATUS_COLORS[todo.status] }}
                      >
                        {STATUS_LABELS[todo.status]}
                      </span>
                    </div>
                    <h3 className="todo-title">{todo.title}</h3>
                    {todo.description && (
                      <p className="todo-description">{todo.description}</p>
                    )}
                    <div className="todo-card-footer">
                      <select
                        value={todo.status}
                        onChange={(e) =>
                          handleStatusChange(todo, e.target.value as TodoStatus)
                        }
                        className="status-select"
                      >
                        {(Object.keys(STATUS_LABELS) as TodoStatus[]).map((s) => (
                          <option key={s} value={s}>
                            {STATUS_LABELS[s]}
                          </option>
                        ))}
                      </select>
                      <button
                        onClick={() => handleDelete(todo.id)}
                        className="btn-danger-sm"
                        title="Delete todo"
                      >
                        Delete
                      </button>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
