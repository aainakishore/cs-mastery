import json
from pathlib import Path

p = list(Path('/Users/eptr6dj/IdeaProjects/master-cs/cs-mastery/src/content/topics').glob('**/serverless-patterns.json'))[0]
d = json.loads(p.read_text())

extra = [
    {"id":"sls-q1","type":"mcq","prompt":"What is the cold start problem in AWS Lambda?",
     "choices":["Lambda running out of memory","Lambda function crashing","The latency added when AWS must provision a new container and initialise the runtime for a Lambda function that has been idle","Lambda exceeding its timeout"],
     "answerIndex":2,"explanation":"Cold start = container provisioning overhead. New or idle Lambda containers need JVM/Node/Python startup + code load before handling the request. Java adds 1-3s. Python/Node ~100-300ms.","tags":["lambda","cold-start"]},
    {"id":"sls-q2","type":"mcq","prompt":"Why use Step Functions instead of chaining Lambda A -> Lambda B -> Lambda C in code?",
     "choices":["Step Functions is always faster","Step Functions provides built-in retry/catch/parallel states and visual execution history — direct Lambda chaining has no retry, no audit trail, and nested timeouts are fragile","Step Functions is cheaper","Lambda cannot call other Lambdas"],
     "answerIndex":1,"explanation":"Hand-coded Lambda chains: no built-in retry, cascading timeouts, no execution history. Step Functions manages state machine transitions, retries with exponential backoff, error catching by type, parallel branches, and shows every step in console.","tags":["step-functions","orchestration"]},
    {"id":"sls-q3","type":"mcq","prompt":"Should a Lambda function store temporary per-request user data in a global variable?",
     "choices":["Yes — global variables persist across invocations improving performance","No — Lambda containers are reused: global user data from request A persists into request B on the same warm container, causing data leakage","Yes — Lambda clears globals between invocations","Only for async invocations"],
     "answerIndex":1,"explanation":"Lambda containers are reused for warm invocations. Global variables persist between them. Safe globals: DB connection, SDK client (reusable, not user-specific). Unsafe globals: userId, request data (leaks between users). Keep per-request data inside the handler.","tags":["lambda","state","gotcha"]},
]

existing = {q['id'] for q in d['questions']}
for q in extra:
    if q['id'] not in existing:
        d['questions'].insert(0, q)

with open(p, 'w') as f:
    json.dump(d, f, indent=2, ensure_ascii=False)
print(f"serverless-patterns.json: q={len(d['questions'])} fc={len(d['flashcards'])}")

