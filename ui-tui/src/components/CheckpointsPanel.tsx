import React, { useState, useEffect } from 'react';
import { Box, Text, Newline, Spacer } from 'ink';
import type { Checkpoint, CheckpointListResponse } from '../gatewayTypes';
import type { Gateway } from '../gateway';

interface CheckpointsPanelProps {
  gw: Gateway;
  sessionId: string;
  t: any;
}

export function CheckpointsPanel({ gw, sessionId, t }: CheckpointsPanelProps) {
  const [checkpoints, setCheckpoints] = useState<Checkpoint[]>([]);
  const [loading, setLoading] = useState(false);

  const loadCheckpoints = async () => {
    setLoading(true);
    try {
      const resp = await gw.request<CheckpointListResponse>('checkpoint.list', {
        session_id: sessionId,
      });
      if (resp && resp.checkpoints) {
        setCheckpoints(resp.checkpoints);
      }
    } catch (error) {
      console.error('Failed to load checkpoints:', error);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    if (sessionId) {
      loadCheckpoints();
    }
  }, [sessionId]);

  const handleRestore = async (checkpointFile: string) => {
    try {
      await gw.request('checkpoint.restore', {
        session_id: sessionId,
        checkpoint_file: checkpointFile,
      });
      // Можно добавить уведомление об успехе
    } catch (error) {
      console.error('Failed to restore checkpoint:', error);
    }
  };

  const handleDelete = async (checkpointFile: string) => {
    try {
      await gw.request('checkpoint.delete', {
        checkpoint_file: checkpointFile,
      });
      // Обновляем список
      loadCheckpoints();
    } catch (error) {
      console.error('Failed to delete checkpoint:', error);
    }
  };

  if (loading) {
    return (
      <Box>
        <Text>Loading checkpoints...</Text>
      </Box>
    );
  }

  if (checkpoints.length === 0) {
    return (
      <Box flexDirection="column">
        <Text bold>Checkpoints</Text>
        <Newline />
        <Text color="gray">No checkpoints found.</Text>
        <Text color="gray">Checkpoints are created automatically before dangerous operations (write_file, patch, terminal).</Text>
      </Box>
    );
  }

  return (
    <Box flexDirection="column">
      <Text bold>Checkpoints ({checkpoints.length})</Text>
      <Newline />
      
      {checkpoints.map((cp, index) => (
        <Box key={cp.filepath} flexDirection="column" marginBottom={1}>
          <Box>
            <Text bold>📸 {cp.formatted_time}</Text>
          </Box>
          <Box paddingLeft={2}>
            <Text color="gray">File: {cp.filename}</Text>
          </Box>
          <Box paddingLeft={2}>
            <Text color="gray">Agent: {cp.agent_id}</Text>
          </Box>
          <Box paddingLeft={2} gap={2}>
            <Text 
              color="green" 
              onClick={() => handleRestore(cp.filepath)}
              style={{ cursor: 'pointer' }}
            >
              [Restore]
            </Text>
            <Text 
              color="red" 
              onClick={() => handleDelete(cp.filepath)}
              style={{ cursor: 'pointer' }}
            >
              [Delete]
            </Text>
          </Box>
          {index < checkpoints.length - 1 && (
            <Box marginTop={1}>
              <Text>───────────────────────────</Text>
            </Box>
          )}
        </Box>
      ))}
    </Box>
  );
}
