import React from 'react';
import { useToast } from './ToastContext';
import { AnimatePresence, motion } from 'framer-motion';

const variantStyles: Record<string, string> = {
  success: 'border-green-500 bg-green-100',
  error: 'border-red-500 bg-red-100',
  info: 'border-blue-500 bg-blue-100',
};

const ToastContainer: React.FC = () => {
  const { toasts, removeToast } = useToast();
  return (
    <div className="fixed top-4 right-4 z-50 p-4 space-y-2 flex flex-col items-end">
      <AnimatePresence>
        {toasts.map((toast) => (
          <motion.div
            key={toast.id}
            initial={{ opacity: 0, y: -10 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: -10 }}
            transition={{ duration: 0.2 }}
            className={`w-80 border-l-4 rounded shadow-md px-4 py-3 ${variantStyles[toast.variant]}`}
            role="status"
            aria-live="polite"
          >
            <div className="flex justify-between items-start gap-2">
              <div>
                <div className="font-bold">{toast.title}</div>
                {toast.description && (
                  <div className="text-sm text-text-secondary mt-1">{toast.description}</div>
                )}
              </div>
              <button
                onClick={() => removeToast(toast.id)}
                className="ml-2 text-xl font-bold text-gray-500 hover:text-gray-800 focus:outline-none"
                aria-label="Close notification"
              >
                ×
              </button>
            </div>
          </motion.div>
        ))}
      </AnimatePresence>
    </div>
  );
};

export default ToastContainer; 