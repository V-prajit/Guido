/**
 * WebSocket Hook for Game Mode
 *
 * Fixed implementation using refs for callbacks to prevent circular dependency.
 * Connects once on mount, maintains stable connection without reconnect loops.
 */

import { useEffect, useRef, useState, useCallback } from 'react';

interface UseWebSocketOptions {
  url: string;
  onMessage: (data: any) => void;
  onOpen?: () => void;
  onClose?: () => void;
  onError?: (error: Event) => void;
  reconnectAttempts?: number;
  reconnectInterval?: number;
}

export const useWebSocket = ({
  url,
  onMessage,
  onOpen,
  onClose,
  onError,
  reconnectAttempts = 5,
  reconnectInterval = 3000,
}: UseWebSocketOptions) => {
  const [isConnected, setIsConnected] = useState(false);

  // Use refs to store callbacks - prevents circular dependency
  const onMessageRef = useRef(onMessage);
  const onOpenRef = useRef(onOpen);
  const onCloseRef = useRef(onClose);
  const onErrorRef = useRef(onError);

  // Use refs for connection state - doesn't trigger re-renders or effect re-runs
  const wsRef = useRef<WebSocket | null>(null);
  const reconnectTimeoutRef = useRef<NodeJS.Timeout>();
  const reconnectCountRef = useRef(0);
  const isMountedRef = useRef(true);

  // Update refs when callbacks change (but don't trigger reconnect)
  useEffect(() => {
    onMessageRef.current = onMessage;
    onOpenRef.current = onOpen;
    onCloseRef.current = onClose;
    onErrorRef.current = onError;
  }, [onMessage, onOpen, onClose, onError]);

  // Connection effect - runs ONCE on mount only
  useEffect(() => {
    const connect = () => {
      try {
        console.log(`[WebSocket] Attempting connection to ${url}`);
        const ws = new WebSocket(url);

        ws.onopen = () => {
          console.log('[WebSocket] ✓ Connected');
          if (isMountedRef.current) {
            setIsConnected(true);
            reconnectCountRef.current = 0;
            if (onOpenRef.current) onOpenRef.current();
          }
        };

        ws.onmessage = (event) => {
          try {
            const data = JSON.parse(event.data);
            if (onMessageRef.current) onMessageRef.current(data);
          } catch (error) {
            console.error('[WebSocket] Failed to parse message:', error);
          }
        };

        ws.onclose = () => {
          console.log('[WebSocket] ✗ Disconnected');
          if (isMountedRef.current) {
            setIsConnected(false);
            if (onCloseRef.current) onCloseRef.current();
          }

          // Attempt reconnection only if still mounted
          if (isMountedRef.current && reconnectCountRef.current < reconnectAttempts) {
            console.log(
              `[WebSocket] Reconnecting... (${reconnectCountRef.current + 1}/${reconnectAttempts})`
            );
            reconnectCountRef.current += 1;
            reconnectTimeoutRef.current = setTimeout(() => {
              connect();
            }, reconnectInterval);
          }
        };

        ws.onerror = (error) => {
          console.error('[WebSocket] Error:', error);
          if (onErrorRef.current) onErrorRef.current(error);
        };

        wsRef.current = ws;
      } catch (error) {
        console.error('[WebSocket] Failed to create connection:', error);
      }
    };

    // Connect once on mount
    connect();

    // Cleanup on unmount
    return () => {
      isMountedRef.current = false;

      if (reconnectTimeoutRef.current) {
        clearTimeout(reconnectTimeoutRef.current);
      }

      if (wsRef.current && wsRef.current.readyState === WebSocket.OPEN) {
        wsRef.current.close();
      }
    };
  }, [url, reconnectAttempts, reconnectInterval]);

  const sendMessage = useCallback((data: any) => {
    if (wsRef.current && wsRef.current.readyState === WebSocket.OPEN) {
      wsRef.current.send(JSON.stringify(data));
    } else {
      console.warn('[WebSocket] Cannot send - not connected');
    }
  }, []);

  const disconnect = useCallback(() => {
    isMountedRef.current = false;
    if (reconnectTimeoutRef.current) {
      clearTimeout(reconnectTimeoutRef.current);
    }
    if (wsRef.current && wsRef.current.readyState === WebSocket.OPEN) {
      wsRef.current.close();
    }
  }, []);

  return {
    isConnected,
    sendMessage,
    disconnect,
  };
};