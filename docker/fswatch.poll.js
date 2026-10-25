import { promises as fs } from 'node:fs'
import { extname, join, relative } from 'node:path'

const DEFAULT_IGNORE = ['.*', '_*', 'node_modules']
const POLL_MS = 400

export function fswatch(root, opts = {}) {
  const { ignore = DEFAULT_IGNORE } = opts
  let closed = false
  let timer
  let snapshot = new Map()
  let initialized = false

  function skipped(rel) {
    const parts = rel.split(/[\\/]/)
    if (parts.some(part => part.startsWith('.') || part.startsWith('_'))) return true
    return ignore.some(pattern => rel.includes(pattern))
  }

  async function walk(dir, out) {
    let entries
    try {
      entries = await fs.readdir(dir, { withFileTypes: true })
    } catch {
      return
    }
    for (const entry of entries) {
      const full = join(dir, entry.name)
      const rel = relative(root, full)
      if (skipped(rel)) continue
      if (entry.isDirectory()) {
        await walk(full, out)
      } else if (entry.isFile()) {
        try {
          const stat = await fs.stat(full)
          out.set(rel, stat.mtimeMs)
        } catch {}
      }
    }
  }

  async function emit(path) {
    if (closed || isEditorBackup(path)) return
    const { onupdate, onremove } = watcher
    if (!onupdate && !onremove) return
    try {
      const stat = await fs.lstat(join(root, path))
      if (stat.isDirectory()) return
      if (onupdate && extname(path)) await onupdate(path)
    } catch (error) {
      if (error?.code === 'ENOENT') {
        if (onremove) await onremove(path)
      } else {
        console.error('fswatch error:', error)
      }
    }
  }

  async function scan() {
    if (closed) return
    const next = new Map()
    await walk(root, next)
    if (initialized) {
      for (const [path, mtime] of next) {
        if (!snapshot.has(path)) await emit(path)
        else if (snapshot.get(path) !== mtime) await emit(path)
      }
      for (const path of snapshot.keys()) {
        if (!next.has(path)) await emit(path)
      }
    }
    snapshot = next
    initialized = true
    if (!closed) timer = setTimeout(scan, POLL_MS)
  }

  const watcher = {
    close() {
      closed = true
      clearTimeout(timer)
    },
  }

  scan()
  return watcher
}

export function isEditorBackup(path) {
  return path.endsWith('~') || path.endsWith('.bck')
}

export function createDeduplicator() {
  let lastTime = 0
  return function shouldProcess() {
    const now = Date.now()
    if (now - lastTime < 50) return false
    lastTime = now
    return true
  }
}
