import json
from pathlib import Path

BASE = Path("/Users/eptr6dj/IdeaProjects/master-cs/cs-mastery/src/content/topics")

def patch(filepath, guide, questions=None, flashcards=None):
    p = Path(filepath)
    t = json.loads(p.read_text())
    t["guide"] = guide
    if questions is not None:
        t["questions"] = questions
    if flashcards is not None:
        t["flashcards"] = flashcards
    p.write_text(json.dumps(t, indent=2))
    print(f"patched {p.name}: {len(t.get('questions',[]))}q {len(t.get('flashcards',[]))}fc")

patch(BASE / "ai/rag.json",
      guide="""# RAG — Retrieval-Augmented Generation

RAG combines an LLM's reasoning with a **retrieval step** that finds relevant documents before generating an answer. It grounds LLM responses in real, up-to-date information.

## The RAG Pipeline

```
User question
    ↓
1. Embed question → vector (e.g., "What is our refund policy?")
    ↓
2. Search vector database for similar document chunks
    k-nearest neighbors search returns top-5 chunks
    ↓
3. Inject retrieved chunks into LLM prompt:
   System: "Answer using only these documents: [chunk1] [chunk2]..."
   User:   "What is our refund policy?"
    ↓
4. LLM generates grounded answer
    ↓
5. (Optional) Return source citations
```

## Building the Knowledge Base

```python
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_openai import OpenAIEmbeddings
from langchain_community.vectorstores import FAISS

# 1. Load documents
documents = load_pdfs("knowledge_base/")

# 2. Chunk (overlap preserves context across boundaries)
splitter = RecursiveCharacterTextSplitter(
    chunk_size=500,       # characters per chunk
    chunk_overlap=50,     # overlap between chunks
)
chunks = splitter.split_documents(documents)

# 3. Embed and store in vector DB
embeddings = OpenAIEmbeddings(model="text-embedding-3-small")
vectorstore = FAISS.from_documents(chunks, embeddings)
vectorstore.save_local("faiss_index")
```

## Retrieval + Generation

```python
from langchain_openai import ChatOpenAI
from langchain.chains import RetrievalQA

vectorstore = FAISS.load_local("faiss_index", embeddings)
retriever = vectorstore.as_retriever(search_kwargs={"k": 5})

llm = ChatOpenAI(model="gpt-4o", temperature=0)

qa_chain = RetrievalQA.from_chain_type(
    llm=llm,
    retriever=retriever,
    return_source_documents=True
)

result = qa_chain.invoke({"query": "What is the refund policy?"})
print(result["result"])      # LLM answer
print(result["source_documents"])  # Which chunks were used
```

## Vector Search and Embeddings

```
Text embedding:
  "The quick brown fox" → [0.23, -0.15, 0.87, ...]  (1536-dim vector for text-embedding-3-small)

Semantic similarity:
  "dog" and "canine" → similar vectors (high cosine similarity)
  "dog" and "galaxy" → dissimilar vectors (low cosine similarity)

Vector databases: FAISS (local), Pinecone, Weaviate, pgvector (PostgreSQL)
```

## RAG vs Fine-Tuning

```
RAG:
  ✓ Knowledge updatable without retraining (add docs to vector DB)
  ✓ Transparent (can show source citations)
  ✓ Handles fresh/real-time data
  ✗ Requires retrieval infrastructure
  ✗ Answer quality limited by retrieval quality

Fine-tuning:
  ✓ Bakes domain knowledge into model weights
  ✓ No runtime retrieval step
  ✗ Expensive to update (retrain)
  ✗ Opaque (no citations)
  ✗ Knowledge becomes stale
```

## Common Pitfalls
- **Wrong chunk size** — too large = irrelevant info dilutes prompt. Too small = loses context. Test 200-1000 chars.
- **Missing overlap** — chunks with no overlap break sentences at boundaries. Use 10-20% overlap.
- **Top-K set too high** — too many retrieved chunks exceed context window or distract the LLM. Start with k=3-5.
- **Not filtering by metadata** — pre-filter by document type, date, or department before embedding search for relevance.
""",
      questions=[
          {"id":"rag-q1","type":"mcq","prompt":"Why does RAG improve LLM factual accuracy?","choices":["RAG uses a larger model","RAG provides the LLM with retrieved documents containing up-to-date facts in the prompt — LLM reasons over retrieved evidence rather than relying on potentially outdated training weights","RAG fine-tunes the model","RAG compresses the context window"],"answerIndex":1,"explanation":"LLMs hallucinate because they generate from training data statistics, not verified facts. RAG injects relevant verified documents into the prompt — LLM can only answer with provided evidence, dramatically reducing hallucination for factual queries.","tags":["RAG","LLM","retrieval"]},
          {"id":"rag-q2","type":"mcq","prompt":"Why is document chunking with overlap important in RAG?","choices":["Reduces storage","Chunks at fixed boundaries may split a sentence or argument mid-point. Overlap (50-100 chars between consecutive chunks) preserves context across boundaries — if the answer spans a chunk boundary, overlap ensures retrieval captures the full context","Required for vector databases","Overlap improves embedding speed"],"answerIndex":1,"explanation":"Example: chunk 1 ends 'The policy applies to...' and chunk 2 starts 'all products purchased...'. Without overlap, retrieval of either chunk gives incomplete information. Overlap ensures both chunks carry that critical context.","tags":["RAG","chunking"]},
          {"id":"rag-q3","type":"mcq","prompt":"RAG vs fine-tuning for a customer support chatbot with frequently updated FAQs?","choices":["Fine-tuning is always better","RAG — FAQs change frequently. RAG allows updating the knowledge base by adding/modifying documents without model retraining. Fine-tuning bakes knowledge into weights — every FAQ update requires an expensive retraining run","Same performance","RAG can't answer FAQ questions"],"answerIndex":1,"explanation":"Operational reality: fine-tuning cycles take days and cost money. A new FAQ answer in RAG: add the document to the vector store, available immediately. RAG is the right architecture for frequently updated domain knowledge.","tags":["RAG","fine-tuning","comparison"]},
      ],
      flashcards=[
          {"id":"rag-fc1","front":"RAG pipeline","back":"1. Embed question → vector. 2. Similarity search in vector DB → top-k chunks. 3. Inject chunks into LLM prompt. 4. LLM generates answer from provided evidence. 5. Return with citations.","tags":["RAG"]},
          {"id":"rag-fc2","front":"Chunking best practices","back":"Chunk size: 200-1000 chars (test empirically). Overlap: 10-20% to preserve boundary context. Use semantic splitters (split at paragraph/sentence, not fixed chars). Too large: noise. Too small: missing context.","tags":["RAG","chunking"]},
          {"id":"rag-fc3","front":"RAG vs fine-tuning","back":"RAG: updatable, transparent, fresh data. Fine-tuning: bakes knowledge in, no retrieval overhead, stale/opaque. Use RAG for frequently changing knowledge; fine-tuning for stable domain style/format.","tags":["RAG","fine-tuning"]},
      ])

patch(BASE / "ai/fine-tuning.json",
      guide="""# Fine-Tuning LLMs

Fine-tuning adapts a pre-trained LLM to a **specific domain, task, or style** by continuing training on domain-specific data.

## When to Fine-Tune vs Prompt Engineering

```
Try in this order (cheapest first):
  1. Prompt engineering (zero/few-shot) — free, immediate
  2. RAG — add knowledge without retraining
  3. Fine-tuning — when you need style/format/domain adaptation
  4. Train from scratch — almost never

Fine-tune when:
  ✓ Consistent output format (always produce JSON schema X)
  ✓ Domain vocabulary (medical abbreviations, legal lingo)
  ✓ Brand voice / style that's hard to describe in prompts
  ✓ Reducing inference cost (small fine-tuned model vs large base model)
  ✗ Don't fine-tune for knowledge — use RAG instead
```

## Parameter-Efficient Fine-Tuning (PEFT / LoRA)

Full fine-tuning updates all model weights — expensive (billions of params).
LoRA (Low-Rank Adaptation) freezes all weights and trains a tiny adapter:

```
Regular: update all W params (billions)    // too expensive

LoRA:    freeze W, add small ΔW = A × B   // A and B are small matrices
         W' = W + α(A × B)
         Only train A and B — often <1% of model params

Result: ~same performance as full fine-tuning, 1000× less compute.

PEFT library (Hugging Face):
from peft import get_peft_model, LoraConfig
config = LoraConfig(r=16, lora_alpha=32, target_modules=["q_proj","v_proj"])
model  = get_peft_model(base_model, config)
```

## Training Data Format (OpenAI Fine-Tune)

```jsonl
// JSONL format — one example per line
{"messages": [
  {"role": "system", "content": "You are a SQL assistant."},
  {"role": "user",   "content": "Get all users older than 30"},
  {"role": "assistant", "content": "SELECT * FROM users WHERE age > 30;"}
]}
{"messages": [
  {"role": "system", "content": "You are a SQL assistant."},
  {"role": "user",   "content": "Count orders per user"},
  {"role": "assistant", "content": "SELECT user_id, COUNT(*) FROM orders GROUP BY user_id;"}
]}
// Minimum 50 examples; 100-1000 for good results
```

## Evaluation

```
Before fine-tuning: baseline metrics on eval set
After fine-tuning: compare on same eval set

Metrics for different tasks:
  Classification: accuracy, F1
  SQL generation: execution accuracy (does it run? does it return correct row?)
  Summarization: ROUGE, human eval

Always: hold out 10-20% of data as eval (never train on eval).
```

## Common Pitfalls
- **Fine-tuning for knowledge** — the model won't reliably learn facts from small datasets. Use RAG for knowledge injection.
- **Too few examples** — < 50 examples often yields no improvement. Minimum 50-100; more is better.
- **Training on eval data** — data leakage. Never include eval samples in training.
- **Overfitting** — a fine-tuned model that performs great on training data but poorly on novel inputs. Use validation loss as the metric to stop training.
""",
      questions=[
          {"id":"ft-q1","type":"mcq","prompt":"What is LoRA (Low-Rank Adaptation) and why is it important?","choices":["A fine-tuning dataset format","Parameter-efficient fine-tuning: freezes all original weights, adds tiny low-rank adapter matrices (A × B). Updates only the adapters — <1% of parameters — achieving near full fine-tune performance at 1000× less compute","A regularization technique","Required for OpenAI fine-tuning"],"answerIndex":1,"explanation":"Full fine-tuning a 70B model requires terabytes of GPU memory. LoRA: original weights frozen, small adapters trained. Final model: original weights + adapters. Merge for inference. Enables fine-tuning on a single A100 instead of a 100-GPU cluster.","tags":["fine-tuning","LoRA","PEFT"]},
          {"id":"ft-q2","type":"mcq","prompt":"You want the model to always output valid JSON in a specific schema. Fine-tune or prompt?","choices":["RAG","Fine-tuning — consistent output format (structure) is exactly where fine-tuning excels. Prompt engineering alone often produces inconsistent JSON with hallucinated fields","Not possible","System prompt only"],"answerIndex":1,"explanation":"Use case: structured output (always JSON, always this schema). Training 100 examples of input → correct schema JSON fine-tunes the model to produce reliable format. Prompt engineering struggles to reliably enforce complex schemas.","tags":["fine-tuning","use-cases"]},
          {"id":"ft-q3","type":"mcq","prompt":"Minimum recommended number of fine-tuning examples for consistent improvement?","choices":["5","50-100 minimum; 500-1000 for robust results. Below 50 examples, fine-tuning often leaves the model virtually unchanged","10","1000 required always"],"answerIndex":1,"explanation":"Small datasets cause the model to overfit or not learn the pattern at all. 50-100 examples: model starts adapting. 500+: reliable, generalizable. Use data augmentation if you can't collect a large dataset.","tags":["fine-tuning","data"]},
      ],
      flashcards=[
          {"id":"ft-fc1","front":"When to fine-tune (hierarchy)","back":"1. Prompt engineering first. 2. RAG for knowledge. 3. Fine-tune for style/format/domain. 4. Scratch-train never. Fine-tune for: consistent output format, domain vocabulary, brand voice — NOT for factual knowledge.","tags":["fine-tuning"]},
          {"id":"ft-fc2","front":"LoRA / PEFT","back":"Freeze all original weights. Add small adapter matrices A × B per layer. Only A and B train (~1% params). Near full fine-tune quality at 1000× lower cost. Adapters can be merged for inference.","tags":["fine-tuning","LoRA"]},
          {"id":"ft-fc3","front":"Fine-tuning data format (OpenAI)","back":"JSONL: one JSON per line with 'messages' array (system, user, assistant roles). Min 50 examples. Hold out 10-20% for evaluation. No eval leakage.","tags":["fine-tuning","data"]},
      ])

patch(BASE / "ai/neural-nets.json",
      guide="""# Neural Networks & Deep Learning

Neural networks are universal function approximators built from layers of interconnected nodes (neurons) that learn by adjusting weights through backpropagation.

## The Perceptron to Deep Network

```
Single neuron (perceptron):
  inputs × weights + bias → activation function → output
  z = w₁x₁ + w₂x₂ + ... + wₙxₙ + b
  output = σ(z)   where σ = activation (sigmoid, ReLU, tanh)

Deep network (MLP):
  Input layer → Hidden layer 1 → Hidden layer 2 → ... → Output layer
  Each layer applies: activations = σ(weights × inputs + biases)
  Multiple layers enable learning hierarchical features:
    CNN image: layer 1 = edges, layer 2 = shapes, layer 3 = objects
```

## Activation Functions

```
ReLU (Rectified Linear Unit): f(x) = max(0, x)
  Most common for hidden layers: fast, no vanishing gradient for x > 0

Sigmoid: f(x) = 1 / (1 + e^-x) → output in [0,1]
  Binary classification output. Suffers vanishing gradient if used in hidden layers.

Softmax: normalizes outputs to sum to 1
  Multi-class classification output (gives probability distribution).

Tanh: f(x) = (e^x - e^-x) / (e^x + e^-x) → output in [-1,1]
  Better than sigmoid in hidden layers; still vanishing gradient issue.
```

## Training: Forward + Backward Pass

```
Forward pass:
  Input → layers → prediction (ŷ)

Loss function (measures error):
  MSE (regression):        L = (ŷ - y)²
  Cross-entropy (classify): L = -Σ y log(ŷ)

Backward pass (backpropagation):
  Compute ∂L/∂w for each weight using chain rule
  Update: w = w - α × ∂L/∂w   (gradient descent)

Optimizer:
  SGD:   w -= lr × gradient  (simple)
  Adam:  adaptive lr per weight + momentum (standard choice)
  Learning rate α: too large = diverge; too small = slow convergence
```

## Regularization (Fighting Overfitting)

```
Dropout:
  Randomly set fraction (20-50%) of neurons to 0 during training.
  Forces network to learn redundant representations.
  Disabled at inference time.

L2 Regularization (weight decay):
  Add λ||w||² to loss — penalizes large weights.
  Prevents single neurons from dominating.

Batch Normalization:
  Normalize activations within each mini-batch.
  Enables higher learning rates, reduces dependency on initialization.

Early stopping:
  Monitor validation loss; stop when it starts increasing (overfitting begins).
```

## Common Architectures

```
MLP:         Dense layers — tabular data
CNN:         Convolutional layers — images, spatial data
RNN/LSTM:    Sequential data — time series (largely replaced by Transformers)
Transformer: Self-attention — NLP, images (ViT), multimodal
GAN:         Generator + Discriminator — image generation
```

## Common Pitfalls
- **Vanishing gradients** — deep networks with sigmoid/tanh suffer small gradients that don't propagate. Use ReLU and BatchNorm.
- **Exploding gradients** — gradients grow exponentially. Use gradient clipping: `torch.nn.utils.clip_grad_norm_`.
- **Not normalizing inputs** — feature with range 0-10,000 dominates. Always normalize to [0,1] or zero-mean.
- **Overfitting without dropout/L2** — network memorizes training data. Monitor train vs val loss; add regularization.
""",
      questions=[
          {"id":"nn-q1","type":"mcq","prompt":"Why is ReLU preferred over sigmoid for hidden layer activations in deep networks?","choices":["ReLU is newer","ReLU: f(x) = max(0, x) — doesn't saturate for positive inputs, so gradients don't vanish during backprop. Sigmoid outputs [0,1] — saturates at extremes, gradients near 0. Deep networks with sigmoid → vanishing gradients → no training","ReLU requires less memory","Sigmoid is deprecated"],"answerIndex":1,"explanation":"Sigmoid and tanh saturate (output near 0 or 1) → gradient ≈ 0 → earlier layers don't update (vanishing gradient problem). ReLU passes gradient directly for x > 0. Dead ReLU (x always < 0): switch to Leaky ReLU or GELU.","tags":["neural-nets","activation","vanishing-gradient"]},
          {"id":"nn-q2","type":"mcq","prompt":"What does dropout do during training and why is it disabled at inference?","choices":["Dropout compresses the model","During training: randomly zeros out a fraction of neurons (e.g., 30%) per batch — forces the network to not rely on any single neuron. At inference: all neurons active, but outputs scaled by (1-dropout rate) to maintain expected value","Dropout reduces model size permanently","Dropout only works in CNNs"],"answerIndex":1,"explanation":"Dropout creates an ensemble effect — each training step uses a different subnetwork. The model learns redundant, robust features. At inference, all neurons contribute — scaling compensates for the expected activation value during training.","tags":["neural-nets","dropout","regularization"]},
          {"id":"nn-q3","type":"mcq","prompt":"What does the optimizer do in neural network training?","choices":["It loads data","Updates model weights based on computed gradients to minimize the loss function. SGD: w -= lr × gradient. Adam: adaptive per-weight learning rates + momentum — converges faster, less tuning needed","It trains the model architecture","It measures accuracy"],"answerIndex":1,"explanation":"After backprop computes ∂L/∂w for each weight, the optimizer determines HOW to update weights. Adam is the default choice: handles varying gradient magnitudes, works well on most problems out of the box.","tags":["neural-nets","optimizer","training"]},
      ],
      flashcards=[
          {"id":"nn-fc1","front":"Activation functions","back":"ReLU: max(0,x), hidden layers default. Sigmoid: [0,1], binary output. Softmax: multi-class output (sum=1). Tanh: [-1,1]. Avoid sigmoid/tanh in deep hidden layers → vanishing gradients.","tags":["neural-nets"]},
          {"id":"nn-fc2","front":"Backpropagation","back":"Forward: input → layers → loss. Backward: chain rule computes ∂L/∂w for each weight. Optimizer updates: w -= lr × ∂L/∂w. Repeat for each mini-batch until convergence.","tags":["neural-nets","training"]},
          {"id":"nn-fc3","front":"Regularization techniques","back":"Dropout: zero random neurons (20-50%) during training → ensemble effect. L2: penalize large weights → generalization. BatchNorm: normalize activations. Early stopping: stop when val loss increases.","tags":["neural-nets","regularization"]},
      ])

patch(BASE / "cloud-devops/serverless-patterns.json",
      guide="""# Serverless Patterns

Serverless computing abstracts away server management — you deploy functions that auto-scale, run on demand, and charge only for execution time.

## What Is Serverless

```
Traditional:                   Serverless:
  You provision servers          Provider provisions and scales
  Pay 24/7 regardless of load    Pay per invocation (milliseconds)
  Manual scaling                 Auto-scale to zero and to millions
  OS patches your problem        No OS, no runtime management

Examples:
  AWS Lambda: 15-min functions, 10GB RAM, pay per GB-second
  Cloudflare Workers: edge, <128MB, pay per million requests
  Vercel Functions: HTTP endpoints at the edge
  Azure Functions, GCP Cloud Functions
```

## Common Serverless Patterns

```
1. HTTP API Backend (most common):
   API Gateway → Lambda → DynamoDB
   REST CRUD with zero-server deployment.

2. Event-Driven Processing:
   S3 upload → Lambda → compress image → save
   SNS/EventBridge → Lambda → process event

3. Fan-Out:
   One event → multiple parallel Lambdas
   e.g., new order → notify Lambda + inventory Lambda + analytics Lambda

4. Step Functions (orchestration):
   Sequence of Lambdas with retries, parallelism, state
   Define workflow as state machine JSON
   Better than chaining Lambda → Lambda directly

5. Scheduled tasks (cron):
   EventBridge rule → Lambda (every hour, every day)
   Replace cron servers with Lambda + schedule rule

6. Stream processing:
   Kinesis/SQS → Lambda (event source mapping)
   auto-polls stream, batches records, invokes Lambda
```

## Cold Start Problem

```
Cold start: Lambda hasn't been invoked recently → container must start
  JS Lambda: 200-500ms cold start
  JVM Lambda: 1-5 seconds cold start (huge JVM startup)
  Python: 100-300ms

Mitigations:
  Provisioned concurrency: keep N Lambda instances warm (pay extra)
  Lambda Snapstart (Java): restore from snapshot (~100ms)
  Use lightweight runtimes: Node.js, Python > Java for latency-sensitive
  Smaller deployment packages: faster container initialization
```

## AWS Lambda Example

```javascript
// handler.js
exports.handler = async (event, context) => {
  console.log('Event:', JSON.stringify(event));

  // HTTP API: event.body contains request body
  const body = JSON.parse(event.body || '{}');

  try {
    const result = await processRequest(body);
    return {
      statusCode: 200,
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(result)
    };
  } catch (err) {
    return {
      statusCode: 500,
      body: JSON.stringify({ error: err.message })
    };
  }
};
```

## Common Pitfalls
- **Lambda cold starts in user-facing APIs** — use provisioned concurrency or lightweight runtimes to eliminate cold starts.
- **Timeouts for long operations** — Lambda max timeout is 15 min. For longer: use Step Functions or offload to ECS.
- **Shared state between invocations** — Lambda can reuse containers (execution context) but treat each invocation as stateless. Store state in DynamoDB, S3, or ElastiCache.
- **Missing DLQ for event-driven Lambda** — failed processing → event lost. Configure Dead Letter Queue (SQS or SNS) on Lambda.
""",
      questions=[
          {"id":"sls-q1","type":"mcq","prompt":"What is the Lambda cold start problem and when is it most impactful?","choices":["Lambda restarts every invocation","First invocation after idle period: provider starts a new container for the function (300ms-5s delay). Most impactful for user-facing APIs (user perceives the latency), negligible for background batch jobs or async processing","Cold start only affects Java","Cold start is unavoidable and unfixable"],"answerIndex":1,"explanation":"Cold start = container init time. Background jobs: 2s cold start = fine. User-facing API: 2s cold start = terrible UX. Mitigations: provisioned concurrency (keep containers warm), lightweight runtimes (Node.js/Python vs JVM), smaller packages.","tags":["serverless","cold-start"]},
          {"id":"sls-q2","type":"mcq","prompt":"AWS Step Functions vs chaining Lambda A → Lambda B — why prefer Step Functions?","choices":["Step Functions are faster","Direct Lambda chaining: A calls B synchronously — A consumes execution time (and cost) waiting for B. If B fails, no retry without custom code. Step Functions: orchestrates lambdas with retries, timeouts, parallel execution, and state persistence — managed, visible, cheaper for complex workflows","Step Functions are newer","Lambda chaining is deprecated"],"answerIndex":1,"explanation":"Lambda A waiting for Lambda B pays for both simultaneously. Step Functions: A completes, state saved, B starts when A's output is ready. Plus: visual workflow, built-in retries, catch/error handling, parallel branches.","tags":["serverless","step-functions"]},
          {"id":"sls-q3","type":"mcq","prompt":"Should a Lambda function store temporary state in a global variable between invocations?","choices":["Yes, for performance","No — Lambda may reuse containers (caching is fine) but you must treat each invocation as stateless. The same container might not be reused; a new container won't have the variable. Store persistent state in DynamoDB, S3, or ElastiCache","Global variables are forbidden","Only for read-only config"],"answerIndex":1,"explanation":"Container reuse is opportunistic. Lambda may reuse the container (reading the global is fine as a cache), or may start fresh (global not set). Write business logic assuming stateless. Use DynamoDB for session state, ElastiCache for shared cache.","tags":["serverless","state"]},
      ],
      flashcards=[
          {"id":"sls-fc1","front":"Serverless characteristics","back":"Zero server management. Pay per invocation (GB-second). Auto-scale to zero. Cold start latency. 15 min max execution. Stateless by design. Good for: event-driven, bursty, variable traffic, API backends.","tags":["serverless"]},
          {"id":"sls-fc2","front":"Cold start mitigation","back":"Provisioned concurrency: keep N warm instances ($$). Lambda SnapStart (Java): restore snapshot. Lightweight runtimes: Node.js/Python over JVM. Smaller deployment packages: faster init.","tags":["serverless","cold-start"]},
          {"id":"sls-fc3","front":"Common Lambda patterns","back":"HTTP API: API GW → Lambda → DB. Event processing: S3/SQS → Lambda. Fan-out: EventBridge → N Lambdas. Scheduled: cron → Lambda. Stream: Kinesis/SQS event source mapping.","tags":["serverless","patterns"]},
      ])

patch(BASE / "cloud-devops/aws-sqs.json",
      guide="""# AWS SQS — Simple Queue Service

SQS is AWS's managed **message queue service** providing reliable, asynchronous message delivery between distributed components.

## SQS Queue Types

```
Standard Queue:
  At-least-once delivery (duplicate possible)
  Best-effort ordering (not guaranteed)
  Nearly unlimited throughput
  Most use cases

FIFO Queue (First-In-First-Out):
  Exactly-once processing
  Strict ordering guaranteed
  Message groups (MessageGroupId) for parallel ordered streams
  Up to 3,000 TPS (300 without batching)
  Required when order AND no duplicates matter (financial transactions)
```

## Message Lifecycle

```
Producer → send → Queue → consumer polls → receives msg
                           ↓ message is INVISIBLE (visibility timeout)
                           ↓ process message
                           ↓ delete message (success) OR
                           ↓ visibility timeout expires → back to queue (failure/retry)

Default visibility timeout: 30 seconds
If consumer dies during processing: message reappears after timeout → retry
```

## Producer and Consumer (AWS SDK v3)

```javascript
const { SQSClient, SendMessageCommand, ReceiveMessageCommand, DeleteMessageCommand } = require('@aws-sdk/client-sqs');

const sqs    = new SQSClient({ region: 'us-east-1' });
const queueUrl = 'https://sqs.us-east-1.amazonaws.com/123/my-queue';

// Producer
await sqs.send(new SendMessageCommand({
  QueueUrl: queueUrl,
  MessageBody: JSON.stringify({ orderId: 123, userId: 456 }),
  DelaySeconds: 0
}));

// Consumer (long polling)
const { Messages } = await sqs.send(new ReceiveMessageCommand({
  QueueUrl: queueUrl,
  MaxNumberOfMessages: 10,
  WaitTimeSeconds: 20,   // Long polling: wait up to 20s for messages
}));

for (const msg of Messages || []) {
  const body = JSON.parse(msg.Body);
  await processOrder(body);
  // Delete to prevent re-delivery
  await sqs.send(new DeleteMessageCommand({
    QueueUrl: queueUrl,
    ReceiptHandle: msg.ReceiptHandle
  }));
}
```

## Dead Letter Queue (DLQ)

```
maxReceiveCount: 3  (try 3 times before DLQ)
If a message fails 3 times → SQS moves it to DLQ automatically

DLQ setup:
  Create SQS queue named "my-queue-dlq"
  Configure source queue: RedrivePolicy:
    { "maxReceiveCount": 3, "deadLetterTargetArn": "arn:...my-queue-dlq" }

Alarm on DLQ depth > 0 to alert on processing failures
```

## SQS vs SNS vs EventBridge

```
SQS:           Queue (pull) — consumers poll for messages
               Best for: task queues, decoupling, retry logic

SNS:           Topic (push) — fan-out to N subscribers simultaneously
               Best for: notifications, broadcast (email + SQS + Lambda)

EventBridge:   Event bus (rules-based routing)
               Best for: loosely coupled microservices, SaaS integrations
               Filter events by pattern, route to multiple targets

Typical pattern: SNS → SQS → Lambda (fan-out + queue buffer + processing)
```

## Common Pitfalls
- **Not using long polling** — short polling (WaitTimeSeconds=0) makes many empty requests. Long polling (20s) waits for messages → cheaper, lower latency.
- **Visibility timeout too short** — if processing takes 30s and timeout is 30s, the message reappears and another consumer picks it up → duplicate processing. Set timeout > expected processing time.
- **Forgetting to delete** — message not deleted after processing → reappears after visibility timeout → processes again. Always delete on success.
""",
      questions=[
          {"id":"sqs-q1","type":"mcq","prompt":"SQS visibility timeout purpose?","choices":["Sets message expiry","Makes message invisible to other consumers while one consumer processes it. If consumer succeeds: delete message. If consumer fails/crashes: timeout expires → message reappears for another consumer. Enables at-least-once delivery with retry","Limits message size","Enables FIFO ordering"],"answerIndex":1,"explanation":"Without visibility timeout, multiple consumers would receive the same message simultaneously. The timeout creates an exclusive processing window: only one consumer processes the message. If it fails, the message becomes available again.","tags":["SQS","visibility-timeout"]},
          {"id":"sqs-q2","type":"mcq","prompt":"SQS Standard vs FIFO queue: when is FIFO required?","choices":["FIFO is always better","FIFO when: message ORDER matters AND duplicates must be prevented (financial transactions, inventory updates). Standard: order and duplicates okay, need maximum throughput (stock events, log processing)","Standard is deprecated","FIFO for all AWS regions"],"answerIndex":1,"explanation":"Standard: occasional duplicates and out-of-order delivery acceptable (design consumers to be idempotent). FIFO: exactly-once, ordered — needed for sequential workflows (step 1 must complete before step 2) and financial correctness.","tags":["SQS","FIFO","standard"]},
          {"id":"sqs-q3","type":"mcq","prompt":"What is a Dead Letter Queue and when does SQS move messages to it?","choices":["A backup queue for all messages","After a configurable number of failed processing attempts (maxReceiveCount), SQS automatically moves the message to the DLQ. Prevents a problematic message from blocking the queue indefinitely. Alert on DLQ depth > 0","DLQ receives all deleted messages","DLQ is for overflow only"],"answerIndex":1,"explanation":"Poison pill: a message that always fails processing (e.g., malformed JSON). Without DLQ, it blocks the queue and consumes worker time forever. With DLQ: after 3 tries, moved aside for human inspection/replay.","tags":["SQS","DLQ"]},
      ],
      flashcards=[
          {"id":"sqs-fc1","front":"SQS Standard vs FIFO","back":"Standard: at-least-once, best-effort order, unlimited TPS. FIFO: exactly-once, strict order, 3000 TPS. Use FIFO for ordered workflows, financial ops. Standard for high-throughput, order-tolerant.","tags":["SQS"]},
          {"id":"sqs-fc2","front":"Visibility timeout","back":"Message received → invisible for timeout duration. Consumer must delete before timeout. Timeout expires without delete → message reappears → retry. Set > expected processing time.","tags":["SQS","visibility-timeout"]},
          {"id":"sqs-fc3","front":"Dead Letter Queue (DLQ)","back":"After maxReceiveCount failures → SQS moves to DLQ. Configure: RedrivePolicy with maxReceiveCount + deadLetterTargetArn. Alert on DLQ depth. Use for poisoned message inspection and replay.","tags":["SQS","DLQ"]},
      ])

print("\nBatch 4 done!")

