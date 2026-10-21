export interface ApiUser {
  id: string;
  organization_id: string;
  organization_name: string;
  email: string;
  role: string;
  status: string;
}

export interface ApiTask {
  id: string;
  organization_id: string;
  owner_id: string;
  purpose: string;
  status: string;
  created_at: string;
  updated_at: string;
}

export interface ApiPassport {
  id: string;
  task_id: string;
  organization_id: string;
  version: number;
  passport_type: string;
  generation_status: string;
  activation_status: string;
  purpose: string;
  allowed_tools: string[];
  approval_required_tools: string[];
  forbidden_tools: string[];
  data_policy: {
    synthetic_data_only: boolean;
    allowed_data_sources: string[];
    source_document_instructions: string;
    external_transmission: string;
    destructive_operations: string;
  };
  expires_at: string;
  activated_at: string | null;
  created_at: string;
}

export interface ApiSession {
  id: string;
  organization_id: string;
  task_id: string;
  passport_id: string;
  owner_id: string;
  status: string;
  created_at: string;
}

export interface ApiAuditEvent {
  id: string;
  event_type: string;
  actor_type: string;
  actor_id: string | null;
  task_id: string | null;
  session_id: string | null;
  action_id: string | null;
  incident_id: string | null;
  description: string;
  occurred_at: string;
  sequence: number | null;
  is_simulation: boolean;
}

export interface ApiIncident {
  id: string;
  organization_id: string;
  agent_session_id: string;
  task_id: string;
  triggering_action_id: string | null;
  severity: string;
  summary: string;
  containment_status: string;
  owner_review_status: string;
  recovery_status: string;
  created_at: string;
  updated_at: string;
  resolved_at: string | null;
}

export interface ApiAction {
  action_id: string;
  request_id: string;
  tool_name: string;
  decision: {
    outcome: 'ALLOW' | 'REQUIRES_APPROVAL' | 'BLOCK' | 'BLOCKED_FAIL_CLOSED';
    reason_code: string;
    reason: string;
    tool_executed: boolean;
  };
  result: Record<string, unknown> | null;
  findings: Array<{
    category: string;
    masked_value: string;
    location_hint: string | null;
    confidence: number | null;
  }>;
  created_at: string;
}

const apiBaseUrl = (import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000')
  .replace(/\/+$/, '');

export class ApiRequestError extends Error {
  constructor(message: string, readonly status: number) {
    super(message);
    this.name = 'ApiRequestError';
  }
}

async function request<T>(path: string, init: RequestInit = {}): Promise<T> {
  const headers = new Headers(init.headers);
  if (init.body !== undefined && !headers.has('Content-Type')) {
    headers.set('Content-Type', 'application/json');
  }

  let response: Response;
  try {
    response = await fetch(`${apiBaseUrl}${path}`, {
      ...init,
      headers,
      credentials: 'include',
    });
  } catch (error) {
    const detail = error instanceof Error ? `: ${error.message}` : '';
    throw new Error(`Unable to reach the Kaaval API at ${apiBaseUrl}${detail}`);
  }

  if (!response.ok) {
    let message = `API request failed (${response.status})`;
    try {
      const payload: unknown = await response.json();
      if (
        typeof payload === 'object' &&
        payload !== null &&
        'message' in payload &&
        typeof payload.message === 'string'
      ) {
        message = payload.message;
      }
    } catch {
      message = `API request failed (${response.status} ${response.statusText})`;
    }
    throw new ApiRequestError(message, response.status);
  }

  if (response.status === 204) {
    return undefined as T;
  }
  return response.json() as Promise<T>;
}

function post<T>(path: string, body?: unknown): Promise<T> {
  return request<T>(path, {
    method: 'POST',
    body: body === undefined ? undefined : JSON.stringify(body),
  });
}

export const api = {
  me: () => request<ApiUser>('/api/auth/me'),
  demoLogin: () => post<{ user: ApiUser }>('/api/auth/demo-login'),
  logout: () => post<{ status: string }>('/api/auth/logout'),
  listTasks: () => request<ApiTask[]>('/api/tasks'),
  createTask: (purpose: string) =>
    post<ApiTask>('/api/tasks', { purpose }),
  getTask: (taskId: string) =>
    request<ApiTask>(`/api/tasks/${encodeURIComponent(taskId)}`),
  generatePassport: (taskId: string) =>
    post<ApiPassport>(`/api/tasks/${encodeURIComponent(taskId)}/passport/generate`),
  getPassport: (taskId: string) =>
    request<ApiPassport>(`/api/tasks/${encodeURIComponent(taskId)}/passport`),
  activatePassport: (taskId: string) =>
    post<ApiPassport>(`/api/tasks/${encodeURIComponent(taskId)}/passport/activate`),
  createSession: (taskId: string) =>
    post<ApiSession>(`/api/tasks/${encodeURIComponent(taskId)}/sessions`),
  listSessions: () => request<ApiSession[]>('/api/sessions'),
  getSession: (sessionId: string) =>
    request<ApiSession>(`/api/sessions/${encodeURIComponent(sessionId)}`),
  getSessionTimeline: (sessionId: string) =>
    request<ApiAuditEvent[]>(`/api/sessions/${encodeURIComponent(sessionId)}/timeline`),
  submitAction: (sessionId: string, toolName: string, args: Record<string, unknown>) =>
    post<ApiAction>(`/api/sessions/${encodeURIComponent(sessionId)}/actions`, {
      tool_name: toolName,
      arguments: args,
    }),
  listIncidents: () => request<ApiIncident[]>('/api/incidents'),
  listAudit: () => request<ApiAuditEvent[]>('/api/audit'),
};
