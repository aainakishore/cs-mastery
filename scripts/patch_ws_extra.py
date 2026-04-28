import json
from pathlib import Path

p = Path('/Users/eptr6dj/IdeaProjects/master-cs/cs-mastery/src/content/topics/networking/websockets.json')
d = json.loads(p.read_text())

extra = [
    {"id":"ws-q16","type":"mcq","prompt":"What is WebSocket subprotocol negotiation?",
     "choices":["A security handshake","Sec-WebSocket-Protocol header lets client propose protocols (e.g., 'chat', 'mqtt'). Server selects one. Allows typed communication on same WS endpoint.",
                "Load balancing protocol","Compression negotiation"],
     "answerIndex":1,"explanation":"Client: Sec-WebSocket-Protocol: chat, superchat. Server: Sec-WebSocket-Protocol: chat (picks one). Both sides then speak that sub-protocol. MQTT over WebSocket uses this. socket.io namespaces are the application-level equivalent.","tags":["websockets","subprotocol"]},
    {"id":"ws-q17","type":"mcq","prompt":"What tool is used to test WebSocket connections from the command line?",
     "choices":["curl","wscat (npm install -g wscat) — wscat -c ws://localhost:8080 opens interactive WS session",
                "telnet only","netcat only"],
     "answerIndex":1,"explanation":"wscat: wscat -c ws://localhost:8080. Interactive: type messages, see server responses in real time. Browser DevTools: Network tab, WS filter, click connection, Messages tab. Postman also supports WebSocket testing.","tags":["websockets","testing"]},
    {"id":"ws-q18","type":"mcq","prompt":"What does the permessage-deflate WebSocket extension do?",
     "choices":["Encrypts WebSocket frames","Compresses each WebSocket frame using DEFLATE — reduces bandwidth 60-80% for JSON/text payloads. Negotiated in handshake headers.",
                "Limits message size","Splits large messages"],
     "answerIndex":1,"explanation":"permessage-deflate: Sec-WebSocket-Extensions: permessage-deflate in handshake. Both sides compress each message frame. JSON (highly repetitive text) compresses well. Trade-off: CPU overhead. Enable for high-volume chat/analytics. Not needed for binary audio/video streams (already compressed).","tags":["websockets","compression","performance"]},
    {"id":"ws-q19","type":"mcq","prompt":"What happens to open WebSocket connections when a server node is restarted during a rolling deployment?",
     "choices":["Connections migrate automatically","Connections are terminated. Clients receive onclose event and must reconnect. Best practice: graceful shutdown sends WS close frame before process exit.",
                "Load balancer re-routes transparently","Connections buffered and replayed"],
     "answerIndex":1,"explanation":"Rolling deploy: drain HTTP connections + WebSocket connections. Graceful: send WS close frame (code 1001 Going Away) -> client gets clean close, reconnects to healthy node. Without graceful close: abrupt TCP RST. Client reconnect logic must handle both cases with exponential backoff.","tags":["websockets","deployment","reconnect"]},
    {"id":"ws-q20","type":"mcq","prompt":"Does WebSocket guarantee message ordering?",
     "choices":["No, messages may arrive out of order","Yes — WebSocket runs on TCP which guarantees in-order delivery on a single connection. Messages arrive in the order sent.",
                "Only with sequence numbers","Only in binary mode"],
     "answerIndex":1,"explanation":"TCP: ordered, reliable delivery. WebSocket on TCP inherits ordering. Messages sent 1,2,3 arrive 1,2,3 on same connection. Cross-connection ordering (reconnects): not guaranteed. After reconnect add application-level sequence numbers to detect any gaps caused by disconnect.","tags":["websockets","ordering","tcp"]},
]

existing_ids = {q['id'] for q in d['questions']}
for q in extra:
    if q['id'] not in existing_ids:
        d['questions'].append(q)

with open(p, 'w') as f:
    json.dump(d, f, indent=2, ensure_ascii=False)
print(f"websockets.json: q={len(d['questions'])} fc={len(d['flashcards'])}")

