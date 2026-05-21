import { useState, useEffect, useCallback } from 'react'

import type { GatewayClient } from '../gatewayClient.js'
import type { Achievement, AchievementCheckResponse, TelemetryData } from '../gatewayTypes.js'

/**
 * Hook for collecting telemetry and integrating with the achievement system.
 * Tracks token usage, task duration, tools used, and other metrics.
 */
export function useTelemetry(sessionId: string, gw: GatewayClient) {
  const [telemetry, setTelemetry] = useState<TelemetryData>({
    tokens_used: 0,
    tokens_saved: 0,
    task_duration: 0,
    tools_used: [],
    tasks_completed: 0,
    autonomous_fixes: 0,
    checkpoints_created: 0,
    swarm_messages: 0,
  })

  const [newAchievements, setNewAchievements] = useState<Achievement[]>([])

  // Function to update telemetry
  const updateTelemetry = useCallback((data: Partial<TelemetryData>) => {
    setTelemetry(prev => ({ ...prev, ...data }))
  }, [])

  // Function to check achievements via TUI gateway
  const checkAchievements = useCallback(async (): Promise<Achievement[]> => {
    try {
      const raw = await gw.request<AchievementCheckResponse>('achievement.check', {
        agent_id: sessionId,
        telemetry: telemetry,
      })

      const result = raw as AchievementCheckResponse

      if (result?.new_unlocked?.length > 0) {
        setNewAchievements(result.new_unlocked)
      }

      return result?.unlocked || []
    } catch (error) {
      console.error('Failed to check achievements:', error)
      return []
    }
  }, [sessionId, telemetry, gw])

  // Auto-check achievements when significant events occur
  useEffect(() => {
    if (telemetry.tasks_completed > 0 || telemetry.tokens_saved > 0) {
      void checkAchievements()
    }
  }, [telemetry.tasks_completed, telemetry.tokens_saved, checkAchievements])

  return {
    telemetry,
    updateTelemetry,
    checkAchievements,
    newAchievements,
    clearNewAchievements: () => setNewAchievements([]),
  }
}
