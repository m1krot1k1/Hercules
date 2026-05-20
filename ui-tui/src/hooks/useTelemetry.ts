import { useEffect, useMemo, useState } from 'react'

import type { GatewayClient } from '../gatewayClient.js'
import type { SubagentNode, SubagentProgress, TelemetryData } from '../types.js'
import { asRpcResult } from '../lib/rpc.js'
import {
  buildSubagentTree,
  treeTotals,
} from '../lib/subagentTree.js'

/**
 * Hook for subscribing to subagent tree updates via JSON-RPC.
 * Returns the current tree and a function to refresh it manually.
 */
export function useSubagentTree(gw: GatewayClient) {
  const [tree, setTree] = useState<SubagentNode[]>([])
  const [rawAgents, setRawAgents] = useState<SubagentProgress[]>([])

  useEffect(() => {
    let cancelled = false

    const fetchTree = async () => {
      try {
        const raw = await gw.request<{ active: SubagentProgress[] }>('delegation.status', {})
        const result = asRpcResult<{ active: SubagentProgress[] }>(raw)
        
        if (!cancelled && result?.active) {
          setRawAgents(result.active)
        }
      } catch {
        // Ignore network errors
      }
    }

    // Initial fetch
    void fetchTree()

    // Poll for updates (every 2 seconds)
    const interval = setInterval(() => void fetchTree(), 2000)

    return () => {
      cancelled = true
      clearInterval(interval)
    }
  }, [gw])

  const computedTree = useMemo(() => buildSubagentTree(rawAgents), [rawAgents])
  const totals = useMemo(() => treeTotals(computedTree), [computedTree])

  return { tree: computedTree, totals, rawAgents }
}

/**
 * Hook for getting telemetry data for a specific agent.
 * Returns telemetry including tokens, cost, time for the agent and its descendants.
 */
export function useTelemetry(agentId: string | null, gw: GatewayClient) {
  const [telemetry, setTelemetry] = useState<TelemetryData | null>(null)

  useEffect(() => {
    if (!agentId) {
      setTelemetry(null)
      return
    }

    let cancelled = false

    const fetchTelemetry = async () => {
      try {
        // Get delegation status which includes all agents with their metrics
        const raw = await gw.request<{ active: SubagentProgress[] }>('delegation.status', {})
        const result = asRpcResult<{ active: SubagentProgress[] }>(raw)
        
        if (!cancelled && result?.active) {
          const agent = result.active.find(a => a.id === agentId)
          
          if (agent) {
            const data: TelemetryData = {
              agentId: agent.id,
              inputTokens: agent.inputTokens ?? 0,
              outputTokens: agent.outputTokens ?? 0,
              reasoningTokens: agent.reasoningTokens ?? 0,
              costUsd: agent.costUsd ?? 0,
              durationSeconds: agent.durationSeconds ?? 0,
              toolCount: agent.toolCount ?? 0,
              status: agent.status,
              model: agent.model ?? '',
              // These would need to be computed from descendants
              descendantTokens: 0,
              descendantCost: 0,
              totalTokens: (agent.inputTokens ?? 0) + (agent.outputTokens ?? 0),
              totalCost: agent.costUsd ?? 0,
            }
            setTelemetry(data)
          }
        }
      } catch {
        // Ignore network errors
      }
    }

    void fetchTelemetry()

    // Poll for updates (every 1 second for active agents)
    const interval = setInterval(() => void fetchTelemetry(), 1000)

    return () => {
      cancelled = true
      clearInterval(interval)
    }
  }, [agentId, gw])

  return telemetry
}

/**
 * Toggle output visibility for a specific agent via JSON-RPC.
 */
export async function toggleAgentOutput(agentId: string, gw: GatewayClient): Promise<boolean> {
  try {
    const raw = await gw.request<{ success: boolean }>('subagent.toggle_output', {
      subagent_id: agentId,
    })
    const result = asRpcResult<{ success: boolean }>(raw)
    return result?.success ?? false
  } catch {
    return false
  }
}

export interface TelemetryData {
  agentId: string
  inputTokens: number
  outputTokens: number
  reasoningTokens: number
  costUsd: number
  durationSeconds: number
  toolCount: number
  status: string
  model: string
  descendantTokens: number
  descendantCost: number
  totalTokens: number
  totalCost: number
}
