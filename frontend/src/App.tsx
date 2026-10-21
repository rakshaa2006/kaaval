/**
 * @license
 * SPDX-License-Identifier: Apache-2.0
 */

import React from 'react';
import { RouterProvider, useRouter } from './router/Router';
import { GovernanceProvider } from './context/GovernanceContext';
import { LandingPage } from './pages/LandingPage';
import { LoginPage } from './pages/LoginPage';
import { DashboardPage } from './pages/DashboardPage';
import { CreateTaskPage } from './pages/CreateTaskPage';
import { PassportReviewPage } from './pages/PassportReviewPage';
import { SessionMonitorPage } from './pages/SessionMonitorPage';
import { IncidentDetailsPage } from './pages/IncidentDetailsPage';
import { AuditTimelinePage } from './pages/AuditTimelinePage';
import { IncidentsPage } from './pages/IncidentsPage';

function AppContent() {
  const { path } = useRouter();

  // Route dispatching
  if (path === '/') {
    return <LandingPage />;
  }

  if (path === '/login') {
    return <LoginPage />;
  }

  if (path === '/app') {
    return <DashboardPage />;
  }

  if (path === '/app/tasks/new') {
    return <CreateTaskPage />;
  }

  if (path.startsWith('/app/tasks/')) {
    return <PassportReviewPage />;
  }

  if (path.startsWith('/app/sessions/')) {
    return <SessionMonitorPage />;
  }

  if (path.startsWith('/app/incidents/')) {
    return <IncidentDetailsPage />;
  }

  if (path === '/app/audit') {
    return <AuditTimelinePage />;
  }

  if (path === '/app/incidents') {
    return <IncidentsPage />;
  }

  // Fallback default
  return <LandingPage />;
}

export default function App() {
  return (
    <RouterProvider>
      <GovernanceProvider>
        <AppContent />
      </GovernanceProvider>
    </RouterProvider>
  );
}
