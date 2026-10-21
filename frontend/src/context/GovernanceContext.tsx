import React, { createContext, useContext, useState, ReactNode } from 'react';
import { Task, Session, Incident, AuditEvent, UserProfile, DemoScenarioId } from '../types/governance';
import { MOCK_TASKS, MOCK_SESSIONS, MOCK_INCIDENTS, MOCK_AUDIT_LOGS, MOCK_USERS } from '../data/mockData';
import { useRouter } from '../router/Router';

interface GovernanceContextType {
  currentUser: UserProfile | null;
  login: (user?: UserProfile) => void;
  logout: () => void;
  activeScenario: DemoScenarioId | 'custom';
  activateScenario: (scenarioId: DemoScenarioId) => void;
  tasks: Task[];
  sessions: Session[];
  incidents: Incident[];
  auditLogs: AuditEvent[];
  createTask: (data: {
    title: string;
    agentName: string;
    category: Task['category'];
    allowedTools: string[];
    prohibitedTools: string[];
    maxCallsPerHour: number;
    description: string;
  }) => string;
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

export const GovernanceProvider: React.FC<GovernanceProviderProps> = ({ children }) => {
  const { navigate } = useRouter();
  const [currentUser, setCurrentUser] = useState<UserProfile | null>(() => MOCK_USERS[0]);
  const [activeScenario, setActiveScenario] = useState<DemoScenarioId | 'custom'>('clean-invoice');
  const [tasks, setTasks] = useState<Task[]>(MOCK_TASKS);
  const [sessions, setSessions] = useState<Session[]>(MOCK_SESSIONS);
  const [incidents, setIncidents] = useState<Incident[]>(MOCK_INCIDENTS);
  const [auditLogs, setAuditLogs] = useState<AuditEvent[]>(MOCK_AUDIT_LOGS);

  const login = (user?: UserProfile) => {
    setCurrentUser(user || MOCK_USERS[0]);
    navigate('/app');
  };

  const logout = () => {
    setCurrentUser(null);
    navigate('/login');
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

  const createTask = (data: {
    title: string;
    agentName: string;
    category: Task['category'];
    allowedTools: string[];
    prohibitedTools: string[];
    maxCallsPerHour: number;
    description: string;
  }): string => {
    const id = `task-gov-${Date.now().toString().slice(-4)}`;
    const passportId = `pass-0x${Math.random().toString(16).slice(2, 10)}`;
    const policyHash = `0x${Array.from({ length: 64 }, () => Math.floor(Math.random() * 16).toString(16)).join('')}`;
    const signature = `ed25519:${Array.from({ length: 64 }, () => Math.floor(Math.random() * 16).toString(16)).join('')}`;

    const newTask: Task = {
      id,
      title: data.title,
      agentId: `agent-${data.agentName.toLowerCase().replace(/[^a-z0-9]/g, '-')}`,
      agentName: data.agentName,
      category: data.category,
      status: 'allowed',
      createdAt: new Date().toISOString(),
      description: data.description,
      passport: {
        passportId,
        issuer: 'Kaaval KMS Authority (eu-west-1)',
        issuedAt: new Date().toISOString(),
        expiresAt: new Date(Date.now() + 86400000).toISOString(),
        allowedTools: data.allowedTools,
        prohibitedTools: data.prohibitedTools,
        maxCallsPerHour: data.maxCallsPerHour,
        dataBoundaries: {
          allowedDomains: ['erp.internal.corp', 'vault.internal.corp'],
          allowedDirectories: ['/var/app/data'],
          egressRestricted: true,
          piiFilterEnabled: true,
        },
        policyHash,
        signature,
      },
    };

    setTasks(prev => [newTask, ...prev]);

    // Append audit event
    const newAuditEvent: AuditEvent = {
      id: `aud-${Date.now().toString().slice(-5)}`,
      timestamp: new Date().toISOString(),
      actor: currentUser?.name || 'SecOps Admin',
      action: 'ISSUE_PASSPORT',
      resource: passportId,
      verdict: 'allowed',
      policyId: 'POLICY-TASK-PASSPORT-ISSUER',
      hash: policyHash.slice(0, 18) + '...',
      previousHash: auditLogs[0]?.hash || '0x000...000',
      details: `New Task Passport issued for agent ${data.agentName} with ${data.allowedTools.length} allowed tools.`,
    };

    setAuditLogs(prev => [newAuditEvent, ...prev]);
    return id;
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
        createTask,
        resetDemoData,
      }}
    >
      {children}
    </GovernanceContext.Provider>
  );
};
