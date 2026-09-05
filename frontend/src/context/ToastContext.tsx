import React, { createContext, useContext, useState, useCallback } from 'react';
import { CheckCircle2, AlertCircle, AlertTriangle, Info, X } from 'lucide-react';

type ToastType = 'success' | 'error' | 'warning' | 'info';

interface Toast {
  id: string;
  type: ToastType;
  message: string;
}

interface ToastContextType {
  success: (msg: string) => void;
  error: (msg: string) => void;
  warning: (msg: string) => void;
  info: (msg: string) => void;
}

const ToastContext = createContext<ToastContextType | undefined>(undefined);

export const ToastProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const [toasts, setToasts] = useState<Toast[]>([]);

  const remove = useCallback((id: string) => {
    setToasts(prev => prev.filter(t => t.id !== id));
  }, []);

  const add = useCallback((type: ToastType, message: string) => {
    const id = `${Date.now()}_${Math.random().toString(36).slice(2, 7)}`;
    setToasts(prev => [...prev, { id, type, message }]);
    setTimeout(() => remove(id), 4000);
  }, [remove]);

  const value: ToastContextType = {
    success: (msg) => add('success', msg),
    error: (msg) => add('error', msg),
    warning: (msg) => add('warning', msg),
    info: (msg) => add('info', msg),
  };

  const icons: Record<ToastType, React.ReactNode> = {
    success: <CheckCircle2 className="w-5 h-5 text-[var(--success)] shrink-0" />,
    error:   <AlertCircle  className="w-5 h-5 text-[var(--error)]   shrink-0" />,
    warning: <AlertTriangle className="w-5 h-5 text-[var(--warning)] shrink-0" />,
    info:    <Info          className="w-5 h-5 text-[var(--info)]    shrink-0" />,
  };

  return (
    <ToastContext.Provider value={value}>
      {children}
      <div className="fixed bottom-5 right-5 z-50 flex flex-col gap-2 w-full max-w-sm pointer-events-none px-4">
        {toasts.map(t => (
          <div
            key={t.id}
            className="pointer-events-auto flex items-start justify-between gap-3 rounded-xl border border-[var(--border)] bg-white px-4 py-3 shadow-lg"
          >
            <div className="flex items-start gap-3">
              {icons[t.type]}
              <p className="text-sm font-medium text-[var(--text-primary)]">{t.message}</p>
            </div>
            <button
              onClick={() => remove(t.id)}
              className="text-[var(--text-muted)] hover:text-[var(--text-primary)] transition-colors"
            >
              <X className="w-4 h-4" />
            </button>
          </div>
        ))}
      </div>
    </ToastContext.Provider>
  );
};

export function useToast() {
  const ctx = useContext(ToastContext);
  if (!ctx) throw new Error('useToast must be used inside ToastProvider');
  return ctx;
}
