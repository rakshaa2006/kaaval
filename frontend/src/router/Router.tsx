import React, { createContext, useContext, useState, useEffect, useCallback, ReactNode } from 'react';

interface RouterContextType {
  path: string;
  navigate: (to: string) => void;
  params: Record<string, string>;
}

const RouterContext = createContext<RouterContextType>({
  path: '/',
  navigate: () => {},
  params: {},
});

export function useRouter(): RouterContextType {
  return useContext(RouterContext);
}

// Simple path matcher for :id patterns
export function matchPath(pattern: string, pathname: string): { matches: boolean; params: Record<string, string> } {
  const patternSegments = pattern.split('/').filter(Boolean);
  const pathSegments = pathname.split('/').filter(Boolean);

  if (patternSegments.length !== pathSegments.length) {
    return { matches: false, params: {} };
  }

  const params: Record<string, string> = {};

  for (let i = 0; i < patternSegments.length; i++) {
    const pSeg = patternSegments[i];
    const uSeg = pathSegments[i];

    if (pSeg.startsWith(':')) {
      const paramName = pSeg.slice(1);
      params[paramName] = decodeURIComponent(uSeg);
    } else if (pSeg !== uSeg) {
      return { matches: false, params: {} };
    }
  }

  return { matches: true, params };
}

interface RouterProviderProps {
  children: ReactNode;
}

export const RouterProvider: React.FC<RouterProviderProps> = ({ children }) => {
  const [currentPath, setCurrentPath] = useState<string>(() => {
    return window.location.pathname || '/';
  });

  const [currentParams, setCurrentParams] = useState<Record<string, string>>({});

  useEffect(() => {
    const handlePopState = () => {
      setCurrentPath(window.location.pathname || '/');
    };

    window.addEventListener('popstate', handlePopState);
    return () => window.removeEventListener('popstate', handlePopState);
  }, []);

  const navigate = useCallback((to: string) => {
    if (window.location.pathname !== to) {
      window.history.pushState(null, '', to);
      setCurrentPath(to);
      window.scrollTo({ top: 0, behavior: 'smooth' });
    }
  }, []);

  // Update params when path changes based on standard routes
  useEffect(() => {
    const routes = [
      '/app/tasks/:id',
      '/app/sessions/:id',
      '/app/incidents/:id',
    ];

    let foundParams: Record<string, string> = {};
    for (const route of routes) {
      const match = matchPath(route, currentPath);
      if (match.matches) {
        foundParams = match.params;
        break;
      }
    }
    setCurrentParams(foundParams);
  }, [currentPath]);

  return (
    <RouterContext.Provider value={{ path: currentPath, navigate, params: currentParams }}>
      {children}
    </RouterContext.Provider>
  );
};

interface LinkProps extends React.AnchorHTMLAttributes<HTMLAnchorElement> {
  href: string;
  children: ReactNode;
  className?: string;
}

export const Link: React.FC<LinkProps> = ({ href, children, className, onClick, ...rest }) => {
  const { navigate } = useRouter();

  const handleClick = (e: React.MouseEvent<HTMLAnchorElement>) => {
    if (onClick) onClick(e);
    if (!e.defaultPrevented && !e.metaKey && !e.ctrlKey && !e.shiftKey) {
      e.preventDefault();
      navigate(href);
    }
  };

  return (
    <a href={href} onClick={handleClick} className={className} {...rest}>
      {children}
    </a>
  );
};
