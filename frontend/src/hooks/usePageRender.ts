import { useEffect, useState, useSyncExternalStore } from 'react'
import { scannerApi } from '../api/client'
import type { PageRead } from '../types/scanner'
import { createPageRender } from './pageRenderState'

/** Parent keys this editor by page/source and refresh, never by a just-saved revision. */
export function usePageRender(page: PageRead) {
  const [actions] = useState(() => createPageRender(page, scannerApi))
  const state = useSyncExternalStore(actions.subscribe, actions.getSnapshot)
  useEffect(() => {
    actions.connect()
    void actions.reload()
    return actions.disconnect
  }, [actions])
  return { ...state, actions }
}
