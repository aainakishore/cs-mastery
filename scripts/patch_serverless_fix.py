import json
from pathlib import Path

p = list(Path('/Users/eptr6dj/IdeaProjects/master-cs/cs-mastery/src/content/topics').glob('**/serverless-patterns.json'))[0]
d = json.loads(p.read_text())

extra_q = [
    {"id":"sls-q18","type":"mcq","prompt":"What is AWS SAM (Serverless Application Model)?",
     "choices":["A CloudFormation replacement","An AWS framework that extends CloudFormation with serverless-specific resource types (Lambda, API GW, DynamoDB) and provides local testing tools (sam local)",
                "A Lambda monitoring service","An IAM permission model"],
     "answerIndex":1,"explanation":"SAM simplifies serverless IaC. AWS::Serverless::Function replaces the verbose Lambda + Role + LogGroup resources. sam local invoke and sam local start-api let you test Lambda functions locally before deploying.","tags":["sam","serverless","iac"]},
    {"id":"sls-q19","type":"mcq","prompt":"Why is EventBridge preferred over CloudWatch Events for scheduling Lambda?",
     "choices":["EventBridge is free, CloudWatch Events is paid","EventBridge IS the updated name/service for CloudWatch Events, with added features: schema registry, event buses, archive and replay, richer filtering",
                "CloudWatch can't schedule Lambda","EventBridge supports more cron formats"],
     "answerIndex":1,"explanation":"Amazon EventBridge was formerly CloudWatch Events — it is the same underlying service, rebranded and extended. EventBridge adds: custom event buses, schema registry, partner event sources, archive and replay. For new projects always use EventBridge naming.","tags":["eventbridge","lambda","scheduling"]},
    {"id":"sls-q20","type":"mcq","prompt":"What is the 'pay per execution' cost model in Lambda?",
     "choices":["Pay $0.20/month per function","Pay for compute time: number of requests x duration in ms x memory GB. First 1 million requests and first 400,000 GB-seconds are FREE every month.",
                "Pay per deployment","Pay per cold start"],
     "answerIndex":1,"explanation":"Lambda pricing: $0.20 per 1M requests + $0.0000166667 per GB-second. At 512MB and 100ms average: $0.20/M requests + tiny compute. For sporadic workloads this is dramatically cheaper than an EC2 running 24/7. Free tier = 1M req + 400K GB-sec/month forever.","tags":["lambda","pricing","serverless"]},
]

extra_fc = [
    {"id":"sls-fc1-real","front":"Lambda trigger types summary","back":"API Gateway (HTTP request) -> sync response. S3 (file upload) -> async processing. SQS (queue message) -> poll-based batch. EventBridge (schedule/event) -> async. DynamoDB Streams (DB change) -> stream. SNS (notification) -> async fan-out.","tags":["lambda","triggers"]},
    {"id":"sls-fc2-real","front":"Step Functions error handling","back":"Retry: {MaxAttempts:3, IntervalSeconds:2, BackoffRate:2} — exponential backoff. Catch: catch specific error types, transition to error handling state. Much cleaner than try/catch chains inside Lambda code.","tags":["step-functions","error-handling"]},
    {"id":"sls-fc3-real","front":"Serverless cost optimisation tips","back":"1. Right-size memory (profile, don't always use max)  2. Use ARM64 (Graviton) = 20% cheaper + faster  3. Reduce package size (faster cold start = shorter billed duration)  4. Use Lambda SnapStart for Java (cache initialised snapshot)","tags":["lambda","cost"]},
]

existing_qids = {q['id'] for q in d['questions']}
for q in extra_q:
    if q['id'] not in existing_qids:
        d['questions'].append(q)

existing_fcids = {fc['id'] for fc in d['flashcards']}
for fc in extra_fc:
    if fc['id'] not in existing_fcids:
        d['flashcards'].append(fc)

with open(p, 'w') as f:
    json.dump(d, f, indent=2, ensure_ascii=False)
print(f"serverless-patterns.json fixed: q={len(d['questions'])} fc={len(d['flashcards'])}")

