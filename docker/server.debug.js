
export function createServer({ port=4000, handler }, callback) {

  async function fetch(req) {
    const { pathname, searchParams } = new URL(req.url)

    // custom handler (proxy or worker)
    const result = handler && await handler(req)
    if (result) return result

    // WebSocket connection for HMR
    if (req.headers.get('upgrade') == 'websocket') {
      const ua = req.headers.get('user-agent') || ''
      return server.upgrade(req, { data: req.url + ' | ' + ua }) ? undefined : new Response('Upgrade failed', { status: 500 })
    }

    // regular file serving
    try {
      const res = await callback(pathname, Object.fromEntries(searchParams))

      // res = Bun.file
      if (res?.stream) return new Response(res, { status: 200 })

      // res = { content, type, status } || HTML <string>
      if (res) {
        return new Response(res.content || res, {
          headers: { 'Content-Type': res.type || 'text/html; charset=utf-8' },
          status: res.status || 200
        })

      } else {
        console.error('Not found', pathname)
        return new Response('404 Not Found', { status: 404 })
      }

    } catch (e) {
      console.error(e)
      return new Response('500 Server Error', { status: 500 })
    }
  }

  const server = Bun.serve({ idleTimeout: 0, port, fetch, websocket })
  return server
}


const sessions = []

const websocket = {
  open(ws) {
    sessions.push(ws)
    console.log(`HMRDBG open total=${sessions.length} ua=${ws.data} rs=${ws.readyState}`)
  },
  close(ws) {
    const i = sessions.indexOf(ws)
    if (i >= 0) sessions.splice(i, 1)
    console.log(`HMRDBG close total=${sessions.length} ua=${ws.data}`)
  }
}

export function broadcast(data) {
  const str = JSON.stringify(data)
  console.log(`HMRDBG broadcast sessions=${sessions.length} base=${data?.base} bytes=${str.length}`)
  sessions.forEach(ws => {
    try { const n = ws.send(str, false); console.log(`HMRDBG sent ua=${ws.data} n=${n}`) }
    catch(e) { console.log(`HMRDBG send err ua=${ws.data} ${e.message}`) }
  })
}

