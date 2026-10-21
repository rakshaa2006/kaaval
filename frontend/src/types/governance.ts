export type Verdict = 'allowed' | 'blocked' | 'quarantined' | 'pending';

export interface TaskPassport {
  passportId: string;
  issuer: string;
  issuedAt: string;
  expiresAt: string;
  allowedTools: string[];
  prohibitedTools: string[];
  maxCallsPerHour: number;
  dataBoundaries: {
    allowedDomains: string[];
    allowedDirectories: string[];
    egressRestricted: boolean;
    piiFilterEnabled: boolean;
  };
  policyHash: string;
  signature: string;
}

export interface Task {
  id: string;
  title: string;
  agentId: string;
  agentName: string;
  category: 'finance' | 'customer_ops' | 'infra' | 'data_reconcile';
  status: Verdict;
  createdAt: string;
  passport?: TaskPassport;
  activeSessionId?: string;
  description: string;
  source?: 'mock' | 'api';
  backendStatus?: string;
}

export interface InspectionResult {
  piiDetected: boolean;
  piiEntitiesFound: string[];
  secretDetected: boolean;
  injectionDetected: boolean;
  injectionScore: number; // 0 to 1
  egressTarget?: string;
  riskVerdict: 'clean' | 'suspicious' | 'hostile';
}

export interface SessionStep {
  stepIndex: number;
  timestamp: string;
  tool: string;
  inputPayload: Record<string, unknown>;
  inspection: InspectionResult;
  verdict: 'allowed' | 'blocked' | 'quarantined';
  policyRuleApplied: string;
  outputPayload?: Record<string, unknown> | string;
  latencyMs: number;
}

export interface Session {
  id: string;
  taskId: string;
  agentId: string;
  agentName: string;
  status: 'active' | 'completed' | 'quarantined' | 'halted';
  startTime: string;
  endTime?: string;
  verdict: Verdict;
  steps: SessionStep[];
  quarantineMetadata?: {
    triggeredAt: string;
    engine: 'Sentinel Core v3.1';
    threatCategory: 'INDIRECT_PROMPT_INJECTION' | 'UNAUTHORIZED_EXFILTRATION' | 'CAPABILITY_BREACH';
    isolatedSandboxId: string;
    forensicDumpRef: string;
    explanation: string;
  };
  source?: 'mock' | 'api';
  backendStatus?: string;
}

export interface Incident {
  id: string;
  title: string;
  sessionId: string;
  taskId: string;
  agentId: string;
  severity: 'critical' | 'high' | 'medium';
  timestamp: string;
  threatType: 'UNAUTHORIZED_TOOL_INVOCATION' | 'INDIRECT_PROMPT_INJECTION' | 'CREDENTIAL_EXFILTRATION' | 'RATE_LIMIT_EXCEEDED';
  mitigationStatus: 'contained' | 'investigating' | 'resolved';
  blockedTarget: string;
  ruleBreached: string;
  summary: string;
  rawPayloadSample: string;
  remediationSteps: string[];
  source?: 'mock' | 'api';
  backendStatus?: string;
}

export interface AuditEvent {
  id: string;
  timestamp: string;
  actor: string;
  action: string;
  resource: string;
  verdict: Verdict;
  policyId: string;
  hash: string;
  previousHash: string;
  details: string;
  source?: 'mock' | 'api';
}

export interface UserProfile {
  id: string;
  name: string;
  role: string;
  email: string;
  initials: string;
}

export type DemoScenarioId = 'clean-invoice' | 'blocked-action' | 'sentinel-quarantine';
