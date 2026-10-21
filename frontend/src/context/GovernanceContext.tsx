import React, {
  createContext,
  useCallback,
  useContext,
  useEffect,
  useState,
  ReactNode,
} from 'react';
import {
  ApiAction,
  ApiAuditEvent,
  ApiIncident,
  ApiSession,
  ApiTask,
  ApiUser,
  api,
  ApiRequestError,
} from '../api/client';
import {
  Task,
  Session,
  Incident,
  AuditEvent,
  UserProfile,
  DemoScenarioId,
} from '../types/governance';
import {
  MOCK_TASKS,
  MOCK_SESSIONS,
  MOCK_INCIDENTS,
  MOCK_AUDIT_LOGS,
} from '../data/mockData';
import { useRouter } from '../router/Router';

interface GovernanceContextType {
  currentUser: UserProfile | null;
  login: () => Promise<void>;
  logout: () => Promise<void>;
  activeScenario: DemoScenarioId | 'custom';
  activateScenario: (scenarioId: DemoScenarioId) => void;
  tasks: Task[];
  sessions: Session[];
  incidents: Incident[];
  auditLogs: AuditEvent[];
  apiError: string | null;
  clearApiError: () => void;
  refreshDashboard: () => Promise<void>;
  createTask: (data: {
    title: string;
    description: string;
  }) => Promise<string>;
  createSession: (taskId: string) => Promise<ApiSession>;
  submitAction: (
    sessionId: string,
    toolName: string,
    args: Record<string, unknown>,
  ) => Promise<ApiAction>;
  resetDemoData: () => void;
}

const GovernanceContext = createContext<GovernanceContextType | null>(null);

export function useGovernance(): GovernanceContextType {
  const context = useContext(GovernanceContext);
  if (!context) {
    throw new Error('useGovernance must be used within a GovernanceProvider');
  }
  return context;
}

interface GovernanceProviderProps {
  children: ReactNode;
}

function userFromApi(user: ApiUser): UserProfile {
  const name = user.email.split('@')[0].replace(/[._-]+/g, ' ');
  const initials = name
    .split(/\s+/)
    .filter(Boolean)
    .slice(0, 2)
    .map((part) => part[0].toUpperCase())
    .join('');
  return {
    id: user.id,
    name: name.replace(/\b\w/g, (letter) => letter.toUpperCase()),
    role: user.role,
    email: user.email,
    initials,
  };
}

function verdictFromTaskStatus(status: string): Task['status'] {
  if (status === 'ACTIVE' || status === 'RUNNING' || status === 'COMPLETED') {
    return 'allowed';
  }
  if (status === 'EXPIRED' || status === 'CANCELLED') {
    return 'blocked';
  }
  return 'pending';
}

function taskFromApi(task: ApiTask): Task {
  return {
    id: task.id,
    title: task.purpose,
    agentId: task.owner_id,
    agentName: 'Kaaval Demo Agent',
    category: 'finance',
    status: verdictFromTaskStatus(task.status),
    createdAt: task.created_at,
    description: task.purpose,
    source: 'api',
    backendStatus: task.status,
  };
}

function sessionFromApi(session: ApiSession): Session {
  const isQuarantined = session.status === 'QUARANTINED';
  const isActive = session.status === 'ACTIVE' || session.status === 'STARTING';
  return {
    id: session.id,
    taskId: session.task_id,
    agentId: session.owner_id,
    agentName: 'Kaaval Demo Agent',
    status: isQuarantined ? 'quarantined' : isActive ? 'active' : 'completed',
    startTime: session.created_at,
    verdict: isQuarantined ? 'quarantined' : isActive ? 'pending' : 'allowed',
    steps: [],
    source: 'api',
    backendStatus: session.status,
  };
}

function incidentFromApi(incident: ApiIncident): Incident {
  const severity = incident.severity.toLowerCase();
  return {
    id: incident.id,
    title: 'Backend enforcement incident',
    sessionId: incident.agent_session_id,
    taskId: incident.task_id,
    agentId: 'Kaaval Demo Agent',
    severity: severity === 'critical' || severity === 'medium' ? severity : 'high',
    timestamp: incident.created_at,
    threatType: 'UNAUTHORIZED_TOOL_INVOCATION',
    mitigationStatus:
      incident.owner_review_status === 'RESOLVED'
        ? 'resolved'
        : incident.containment_status === 'CONTAINED'
          ? 'contained'
          : 'investigating',
    blockedTarget: 'Not provided by the backend incident summary.',
    ruleBreached: 'See the enforcement decision in the session timeline.',
    summary: incident.summary,
    rawPayloadSample: 'The backend does not expose raw action payloads.',
    remediationSteps: [
      `Containment: ${incident.containment_status}`,
      `Owner review: ${incident.owner_review_status}`,
      `Recovery: ${incident.recovery_status}`,
    ],
    source: 'api',
    backendStatus: incident.containment_status,
  };
}

function auditEventFromApi(event: ApiAuditEvent): AuditEvent {
  const normalizedType = event.event_type.toLowerCase();
  const verdict: AuditEvent['verdict'] =
    normalizedType.includes('quarantin')
      ? 'quarantined'
      : normalizedType.includes('block')
        ? 'blocked'
        : 'allowed';
  return {
    id: event.id,
    timestamp: event.occurred_at,
    actor: event.actor_type,
    action: event.event_type,
    resource:
      event.action_id ??
      event.session_id ??
      event.task_id ??
      event.incident_id ??
      'Kaaval',
    verdict,
    policyId: 'Not exposed by the backend',
    hash: 'Not exposed by the backend',
    previousHash: 'Not exposed by the backend',
    details: event.description,
    source: 'api',
  };
}

export const GovernanceProvider: React.FC<GovernanceProviderProps> = ({ children }) => {
  const { navigate } = useRouter();
  const [currentUser, setCurrentUser] = useState<UserProfile | null>(null);
  const [activeScenario, setActiveScenario] = useState<DemoScenarioId | 'custom'>('clean-invoice');
  const [tasks, setTasks] = useState<Task[]>(MOCK_TASKS);
  const [sessions, setSessions] = useState<Session[]>(MOCK_SESSIONS);
  const [incidents, setIncidents] = useState<Incident[]>(MOCK_INCIDENTS);
  const [auditLogs, setAuditLogs] = useState<AuditEvent[]>(MOCK_AUDIT_LOGS);
  const [apiError, setApiError] = useState<string | null>(null);

  const refreshDashboard = useCallback(async () => {
    try {
      const [apiTasks, apiSessions, apiIncidents, apiAuditEvents] = await Promise.all([
        api.listTasks(),
        api.listSessions(),
        api.listIncidents(),
        api.listAudit(),
      ]);
      setTasks([...apiTasks.map(taskFromApi), ...MOCK_TASKS]);
      setSessions([...apiSessions.map(sessionFromApi), ...MOCK_SESSIONS]);
      setIncidents([...apiIncidents.map(incidentFromApi), ...MOCK_INCIDENTS]);
      setAuditLogs([...apiAuditEvents.map(auditEventFromApi), ...MOCK_AUDIT_LOGS]);
      setApiError(null);
    } catch (error) {
      setApiError(error instanceof Error ? error.message : 'Unable to refresh backend records.');
    }
  }, []);

  useEffect(() => {
    let cancelled = false;
    const restoreSession = async () => {
      try {
        const user = await api.me();
        if (cancelled) return;
        setCurrentUser(userFromApi(user));
        await refreshDashboard();
      } catch (error) {
        if (cancelled) return;
        if (!(error instanceof ApiRequestError) || error.status !== 401) {
          setApiError(error instanceof Error ? error.message : 'Unable to restore the session.');
        }
      }
    };
    void restoreSession();
    return () => {
      cancelled = true;
    };
  }, [refreshDashboard]);

  const login = async () => {
    setApiError(null);
    try {
      const response = await api.demoLogin();
      setCurrentUser(userFromApi(response.user));
      await refreshDashboard();
      navigate('/app');
    } catch (error) {
      const message = error instanceof Error ? error.message : 'Demo login failed.';
      setApiError(message);
      throw error;
    }
  };

  const logout = async () => {
    setApiError(null);
    try {
      await api.logout();
      setCurrentUser(null);
      setTasks(MOCK_TASKS);
      setSessions(MOCK_SESSIONS);
      setIncidents(MOCK_INCIDENTS);
      setAuditLogs(MOCK_AUDIT_LOGS);
      navigate('/login');
    } catch (error) {
      const message = error instanceof Error ? error.message : 'Sign out failed.';
      setApiError(message);
    }
  };

  const activateScenario = (scenarioId: DemoScenarioId) => {
    setActiveScenario(scenarioId);
    if (scenarioId === 'clean-invoice') {
      navigate('/app/sessions/sess-inv-clean');
    } else if (scenarioId === 'blocked-action') {
      navigate('/app/incidents/inc-402');
    } else if (scenarioId === 'sentinel-quarantine') {
      navigate('/app/sessions/sess-sentinel-88');
    }
  };

  const createTask = async (data: {
    title: string;
    description: string;
  }): Promise<string> => {
    setApiError(null);
    try {
      const task = await api.createTask(
        `${data.title}. Process synthetic invoice: ${data.description || data.title}`,
      );
      await api.generatePassport(task.id);
      setTasks((previous) => [taskFromApi(task), ...previous.filter((item) => item.id !== task.id)]);
      return task.id;
    } catch (error) {
      const message = error instanceof Error ? error.message : 'Unable to create the task.';
      setApiError(message);
      throw error;
    }
  };

  const createSession = async (taskId: string): Promise<ApiSession> => {
    setApiError(null);
    try {
      const session = await api.createSession(taskId);
      setSessions((previous) => [
        sessionFromApi(session),
        ...previous.filter((item) => item.id !== session.id),
      ]);
      await refreshDashboard();
      return session;
    } catch (error) {
      const message = error instanceof Error ? error.message : 'Unable to start the session.';
      setApiError(message);
      throw error;
    }
  };

  const submitAction = async (
    sessionId: string,
    toolName: string,
    args: Record<string, unknown>,
  ): Promise<ApiAction> => {
    setApiError(null);
    try {
      const action = await api.submitAction(sessionId, toolName, args);
      await refreshDashboard();
      return action;
    } catch (error) {
      const message = error instanceof Error ? error.message : 'Unable to submit the action.';
      setApiError(message);
      throw error;
    }
  };

  const resetDemoData = () => {
    setTasks(MOCK_TASKS);
    setSessions(MOCK_SESSIONS);
    setIncidents(MOCK_INCIDENTS);
    setAuditLogs(MOCK_AUDIT_LOGS);
    setActiveScenario('clean-invoice');
  };

  return (
    <GovernanceContext.Provider
      value={{
        currentUser,
        login,
        logout,
        activeScenario,
        activateScenario,
        tasks,
        sessions,
        incidents,
        auditLogs,
        apiError,
        clearApiError: () => setApiError(null),
        refreshDashboard,
        createTask,
        createSession,
        submitAction,
        resetDemoData,
      }}
    >
      {children}
    </GovernanceContext.Provider>
  );
};
