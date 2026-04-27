#!/usr/bin/env python3
"""
Patch all incomplete topics: add 20 questions, 8 flashcards, expand guide with references.
Run: python3 scripts/patch_all_topics.py
Safe: skips any file that already has >= 20 questions AND >= 8 flashcards.
"""

import json
import os

BASE = os.path.join(os.path.dirname(__file__), '..', 'src', 'content', 'topics')

# ─────────────────────────────────────────────────────────────
#  HELPERS
# ─────────────────────────────────────────────────────────────
def load(path):
    with open(path) as f:
        return json.load(f)

def save(path, data):
    with open(path, 'w') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
    print(f"  ✓ saved {os.path.basename(path)}")

def patch(folder, filename, guide_addition, new_questions, new_flashcards, replace_guide=False):
    path = os.path.join(BASE, folder, filename)
    if not os.path.exists(path):
        print(f"  ✗ NOT FOUND: {path}")
        return
    d = load(path)

    # Guard: skip if already complete
    if len(d.get('questions', [])) >= 20 and len(d.get('flashcards', [])) >= 8:
        g = d.get('guide', '')
        if len(g) >= 3000 and '## References' in g:
            print(f"  – skip {filename} (already complete)")
            return

    # Expand guide
    g = d.get('guide', '')
    if replace_guide:
        d['guide'] = guide_addition
    elif '## References' not in g:
        d['guide'] = g.rstrip() + '\n\n' + guide_addition

    # Merge questions (avoid duplicate ids)
    existing_ids = {q['id'] for q in d.get('questions', [])}
    for q in new_questions:
        if q['id'] not in existing_ids:
            d['questions'].append(q)
            existing_ids.add(q['id'])

    # Merge flashcards (avoid duplicate ids)
    existing_fc_ids = {fc['id'] for fc in d.get('flashcards', [])}
    for fc in new_flashcards:
        if fc['id'] not in existing_fc_ids:
            d['flashcards'].append(fc)
            existing_fc_ids.add(fc['id'])

    save(path, d)


# ─────────────────────────────────────────────────────────────
#  STEP 1 — AI TOPICS
# ─────────────────────────────────────────────────────────────

# ── agents ──────────────────────────────────────────────────
patch('ai', 'agents.json',
guide_addition="""
## Tool Design Principles

```
Good tool design:
  ✓ Deterministic inputs/outputs the LLM can predict
  ✓ Returns structured data (JSON > prose)
  ✓ Named parameters that match natural language
  ✓ Includes error messages the agent can reason about

Bad tool design:
  ✗ Side-effectful without confirmation (send_email, delete_file)
  ✗ Returns 10,000 token HTML pages
  ✗ Ambiguous parameter names
```

## Agent Memory Architecture

```
Context window (ephemeral)
  ├── System prompt (agent persona, tools list)
  ├── Conversation history
  ├── Tool call results
  └── Working scratch (Thought/Action/Observation)

External memory (persistent)
  ├── Vector DB → semantic search (episodic memory)
  ├── Key-value store → exact lookup (facts, user prefs)
  └── Structured DB → relational queries
```

## Error Handling Pattern

```python
try:
    result = tool.run(inputs)
    observation = f"Tool succeeded: {result}"
except ToolException as e:
    observation = f"Tool failed with: {e}. Try a different approach."
# Feed observation back to LLM — agent adapts
```

## References & Further Learning
- 📄 **ReAct paper**: "ReAct: Synergizing Reasoning and Acting in Language Models" — Yao et al., 2022 (arxiv.org/abs/2210.03629)
- 📄 **HuggingGPT**: "HuggingGPT: Solving AI Tasks with ChatGPT and its Friends" — demonstrates multi-tool orchestration
- 🎥 **Andrej Karpathy** "Intro to LLM Agents" (YouTube)
- 🎥 **LangChain** official YouTube channel — agent tutorials
- 📖 **LangChain docs** — conceptual guide on agents: python.langchain.com/docs/modules/agents
- 📖 **AutoGen docs** — multi-agent framework: microsoft.github.io/autogen
- 🖼️ **Diagram**: ReAct loop flowchart — search "ReAct agent loop diagram"
""",
new_questions=[
  {"id":"agent-q4","type":"mcq","prompt":"Which component decides WHAT tool to call next in an agent?",
   "choices":["The tool registry","The LLM backbone — it generates the next Action based on Thought","The orchestration framework","The memory module"],
   "answerIndex":1,"explanation":"The LLM generates the next action. The framework executes it and feeds the Observation back. The LLM is the decision-maker.","tags":["agents","LLM"]},
  {"id":"agent-q5","type":"mcq","prompt":"What is 'tool hallucination' in an agent context?",
   "choices":["Agent uses a tool that doesn't exist — calls undefined tool names","Agent generates incorrect text","Tool returns wrong data","Memory overflow"],
   "answerIndex":0,"explanation":"LLMs may invent tool names not in the registered list. Tool schemas must list exact names; robust parsers should catch unknown tool names gracefully.","tags":["agents","hallucination"]},
  {"id":"agent-q6","type":"mcq","prompt":"Why should irreversible actions (send email, delete file) pause for human confirmation?",
   "choices":["Performance reasons","Agents can hallucinate or misinterpret intent — human-in-the-loop prevents real-world mistakes that can't be undone","Tool latency","API rate limits"],
   "answerIndex":1,"explanation":"Agents combine reasoning errors with execution power. Irreversible ops need a confirmation step before execution. Reversible ops (web search, read file) can be automated safely.","tags":["agents","safety"]},
  {"id":"agent-q7","type":"mcq","prompt":"An agent uses a vector DB as 'long-term memory'. What does it store?",
   "choices":["The model weights","Embeddings of past interactions/documents for semantic retrieval","SQL query cache","Tool execution logs"],
   "answerIndex":1,"explanation":"Vector DB stores embedded representations of past context. At runtime, the agent queries by similarity to retrieve relevant past information into the context window.","tags":["agents","memory"]},
  {"id":"agent-q8","type":"mcq","prompt":"What is the main benefit of structured tool outputs (JSON) vs prose?",
   "choices":["Smaller token count","LLM can reliably parse fields — names, values, types — without natural-language ambiguity","JSON is faster to generate","Prose causes loops"],
   "answerIndex":1,"explanation":"LLMs can extract structured data from JSON predictably. Prose responses require the LLM to parse natural language which introduces errors.","tags":["agents","tools"]},
  {"id":"agent-q9","type":"multi","prompt":"Which are valid agent memory types?",
   "choices":["Context window (short-term)","Vector database (semantic search)","SQL relational DB (structured queries)","Hardcoded if-else in code"],
   "answerIndexes":[0,1,2],"explanation":"Agents use context window (ephemeral), vector DB (semantic long-term), and structured DB. Hardcoded logic is not agent memory.","tags":["agents","memory"]},
  {"id":"agent-q10","type":"mcq","prompt":"In a multi-agent system, the 'orchestrator' role is:",
   "choices":["Executes tool calls","Stores memory","Delegates sub-tasks to specialised agents and aggregates results","Validates outputs"],
   "answerIndex":2,"explanation":"Orchestrator = the top-level planner. It breaks a task into sub-tasks and routes each to a specialised agent (researcher, coder, reviewer).","tags":["agents","multi-agent"]},
  {"id":"agent-q11","type":"codeOutput","prompt":"What does maxIterations=3 do in this agent call?",
   "code":"executor.invoke({'input': 'research 10 topics'}, config={'max_iterations': 3})",
   "choices":["Returns 3 results","Allows at most 3 tool calls before forcing a final answer","Times out after 3 seconds","Limits output to 3 paragraphs"],
   "answerIndex":1,"explanation":"maxIterations caps the Thought/Action/Observation loop. After 3 iterations, the agent returns whatever it has. Prevents infinite loops.","tags":["agents","safety"]},
  {"id":"agent-q12","type":"mcq","prompt":"Context window overflow is a risk for long-running agents because:",
   "choices":["The LLM gets confused by long conversations","Tool calls stop working","Each Observation adds tokens — eventually exceeding the model's context limit causing truncation of earlier reasoning","The agent slows down"],
   "answerIndex":2,"explanation":"Every tool result is appended to context. A long agent run can fill the context window, causing the LLM to lose earlier reasoning steps. Solution: periodic summarization or external memory.","tags":["agents","context"]},
  {"id":"agent-q13","type":"mcq","prompt":"What distinguishes Plan-and-Execute from ReAct?",
   "choices":["Plan-and-Execute has no tools","Plan-and-Execute creates a full plan upfront, then executes each step — ReAct interleaves planning and acting","They are identical","Plan-and-Execute is always better"],
   "answerIndex":1,"explanation":"ReAct: think-act-observe-repeat (dynamic, adaptive). Plan-and-Execute: generate full plan first, execute steps with sub-agents. P&E is better for predictable tasks; ReAct for exploratory ones.","tags":["agents","ReAct"]},
  {"id":"agent-q14","type":"mcq","prompt":"Tool descriptions in the system prompt should be:",
   "choices":["Minimal to save tokens","Precise: name, purpose, parameters, return format — so the LLM knows exactly when and how to call them","Examples only","Omitted — LLM knows all tools"],
   "answerIndex":1,"explanation":"The LLM selects tools based solely on the description in its context. Vague descriptions cause wrong tool selection or hallucinated parameters.","tags":["agents","tools"]},
  {"id":"agent-q15","type":"mcq","prompt":"'Function calling' in GPT-4 / Claude differs from plain text ReAct because:",
   "choices":["No difference","The model outputs a structured JSON action instead of free-text — the framework reliably parses it without regex","Function calling is slower","Function calling requires Python"],
   "answerIndex":1,"explanation":"Native function calling produces validated JSON tool calls. Plain ReAct requires regex/parsing of text like 'Action: tool_name(args)' which is error-prone.","tags":["agents","function-calling"]},
  {"id":"agent-q16","type":"multi","prompt":"Challenges unique to multi-agent systems vs single agent?",
   "choices":["Error propagation between agents","Inter-agent communication overhead","Harder debugging — which agent made the mistake?","Agents can't use tools"],
   "answerIndexes":[0,1,2],"explanation":"Multi-agent adds: cascading failures, communication cost, and debugging complexity. Each agent can introduce errors that propagate downstream.","tags":["agents","multi-agent"]},
  {"id":"agent-q17","type":"mcq","prompt":"Why should agents return partial results if maxIterations is hit?",
   "choices":["The framework requires it","Better than an error — partial information is still useful; caller can retry or use what's available","Saves API cost","Improves accuracy"],
   "answerIndex":1,"explanation":"A graceful degradation answer (even incomplete) is more useful than a hard failure to the end user. Design agents to return best-effort results on cutoff.","tags":["agents","safety"]},
  {"id":"agent-q18","type":"mcq","prompt":"In LangGraph, why use a state machine for agents vs simple loops?",
   "choices":["State machines are faster","State machine makes agent flow explicit — nodes=actions, edges=transitions — enabling branching, retries, checkpoints","Required for tool use","LangGraph doesn't support loops"],
   "answerIndex":1,"explanation":"A DAG/state-machine approach makes control flow inspectable and serializable. You can pause, resume, branch on tool errors, and replay — not possible in a hidden while-loop.","tags":["agents","LangGraph"]},
  {"id":"agent-q19","type":"mcq","prompt":"What is 'grounding' in agent context?",
   "choices":["Connecting agent to electricity","Anchoring agent outputs to verified real-world data (search results, DB queries) to reduce hallucination","Training technique","Memory compression"],
   "answerIndex":1,"explanation":"Grounding = tying the LLM's reasoning to factual external data sources. A grounded agent retrieves before it claims, reducing confabulation.","tags":["agents","hallucination"]},
  {"id":"agent-q20","type":"mcq","prompt":"Which evaluation metric matters most for production agents?",
   "choices":["Token count","Task completion rate — did the agent accomplish the goal correctly within budget?","Response length","Model perplexity"],
   "answerIndex":1,"explanation":"Task completion rate (did it succeed?) + efficiency (how many tool calls / tokens?) are the production metrics. Perplexity measures language model quality, not task success.","tags":["agents","evaluation"]},
],
new_flashcards=[
  {"id":"agent-fc4","front":"Tool hallucination","back":"Agent calls a tool name not in its registry. Prevent by: strict JSON schema validation, listing only real tool names in system prompt, catching parse errors and re-prompting.","tags":["agents","hallucination"]},
  {"id":"agent-fc5","front":"Plan-and-Execute vs ReAct","back":"ReAct: interleave Thought/Action/Observation dynamically. Plan-and-Execute: create full plan upfront → sub-agents execute. P&E = predictable tasks; ReAct = exploratory.","tags":["agents","planning"]},
  {"id":"agent-fc6","front":"Agent memory layers","back":"Context window (ephemeral, token-limited) → Vector DB (semantic retrieval, persistent) → Structured DB (relational queries). Use all three for production agents.","tags":["agents","memory"]},
  {"id":"agent-fc7","front":"Human-in-the-loop","back":"Pause before irreversible actions (delete, send, pay). Use a ConfirmationTool that requires human approval. Automate only reversible ops (read, search, compute).","tags":["agents","safety"]},
  {"id":"agent-fc8","front":"Function calling vs text ReAct","back":"Function calling: model outputs structured JSON tool call — reliable parsing. Text ReAct: model writes 'Action: tool(args)' — requires fragile regex. Use native function calling in production.","tags":["agents","function-calling"]},
])


# ── fine-tuning ─────────────────────────────────────────────
patch('ai', 'fine-tuning.json',
guide_addition="""
## LoRA — Low-Rank Adaptation

```
Full fine-tune:
  Update all W (7B params × fp32 = 28GB gradients)
  Cost: 8× A100s, days

LoRA:
  Freeze W, learn small ΔW = A × B  (rank r = 8–64)
  A: (d × r), B: (r × d) — total params: 2 × d × r  (tiny!)
  Forward: h = (W + AB)x = Wx + ABx

Memory: 100× less than full fine-tune. Runs on 1× A100.
```

## Instruction Fine-tuning Format

```json
{
  "messages": [
    {"role": "system", "content": "You are a financial analyst."},
    {"role": "user",   "content": "What is EBITDA?"},
    {"role": "assistant","content": "EBITDA = Earnings Before Interest, Taxes, Depreciation and Amortisation..."}
  ]
}
```
Each training example = one conversation. 1000–10000 high-quality examples typically suffice.

## RLHF Pipeline

```
Step 1: Supervised Fine-tuning (SFT)
  Training data: human-written ideal responses

Step 2: Reward Model
  Human preferences: rank completions A > B > C
  Train RM to predict human scores

Step 3: PPO (Proximal Policy Optimisation)
  LLM generates responses → RM scores → gradient update
  Penalty term (KL divergence) keeps model close to SFT base

Result: ChatGPT-style helpfulness and safety alignment
```

## When Is Fine-tuning the Right Choice?

```
✓ Use fine-tuning when:
  - Consistent style/persona required
  - Domain vocabulary not in base model
  - Latency sensitive (no long system prompt)
  - Small model needed (distillation)

✗ Don't fine-tune when:
  - You just need to inject facts → use RAG
  - You need up-to-date knowledge → RAG + retrieval
  - You have < 100 examples → few-shot prompting
  - Budget is tight → prompt engineering first
```

## References & Further Learning
- 📄 **LoRA paper**: "LoRA: Low-Rank Adaptation of Large Language Models" — Hu et al. (arxiv.org/abs/2106.09685)
- 📄 **RLHF paper**: "Training language models to follow instructions with human feedback" — Ouyang et al. (InstructGPT, arxiv.org/abs/2203.02155)
- 📄 **QLoRA**: "QLoRA: Efficient Finetuning of Quantized LLMs" (arxiv.org/abs/2305.14314)
- 🎥 **Andrej Karpathy** "Let's build the GPT Tokenizer" + "nanoGPT" — foundational understanding
- 🎥 **HuggingFace** — "Fine-tuning a language model" tutorial series (YouTube + Docs)
- 📖 **HuggingFace TRL docs** — SFT, RLHF, DPO trainers: huggingface.co/docs/trl
- 🖼️ **Diagram**: LoRA matrix decomposition — search "LoRA low rank adaptation diagram"
""",
new_questions=[
  {"id":"ft-q4","type":"mcq","prompt":"LoRA reduces fine-tuning cost by:",
   "choices":["Reducing the number of training steps","Freezing the original weights and only training small low-rank matrices ΔW = A×B","Using 8-bit quantization","Distilling into a smaller model"],
   "answerIndex":1,"explanation":"LoRA inserts trainable rank-r matrices alongside frozen weights. Instead of updating billions of params, you update millions. Memory drops ~100×.","tags":["fine-tuning","LoRA"]},
  {"id":"ft-q5","type":"mcq","prompt":"What is catastrophic forgetting?",
   "choices":["Model loses weights on disk","Fine-tuned model loses general capabilities in areas not covered by training data","Training loss diverges","GPU memory exhaustion"],
   "answerIndex":1,"explanation":"Fine-tuning on narrow data can overwrite general knowledge. Mitigations: LoRA (original weights frozen), regularization, replay of general data.","tags":["fine-tuning","overfitting"]},
  {"id":"ft-q6","type":"mcq","prompt":"RLHF uses a reward model for:",
   "choices":["Evaluating code syntax","Scoring completions based on learned human preferences to guide PPO training","Blocking harmful content","Reducing hallucination directly"],
   "answerIndex":1,"explanation":"The reward model is trained on human pairwise preferences (A>B). It then scores the LLM's outputs during PPO — the LLM learns to maximize these scores.","tags":["fine-tuning","RLHF"]},
  {"id":"ft-q7","type":"mcq","prompt":"When should you use RAG instead of fine-tuning?",
   "choices":["When you want style consistency","When you need to inject up-to-date or large factual knowledge — fine-tuning can't store documents","When latency is critical","When using a small model"],
   "answerIndex":1,"explanation":"Fine-tuning teaches style and behavior. RAG teaches facts at inference time. Knowledge that changes frequently (company docs, news) belongs in a retrieval system, not weights.","tags":["fine-tuning","RAG"]},
  {"id":"ft-q8","type":"mcq","prompt":"Why split training data into train/validation sets for fine-tuning?",
   "choices":["Required by the framework","To detect overfitting — training loss drops but validation loss rising = memorization, not generalization","To speed up training","Validation used for RLHF only"],
   "answerIndex":1,"explanation":"Train loss measures performance on seen data. Val loss measures generalization. Early stopping when val loss stops improving prevents overfitting.","tags":["fine-tuning","overfitting"]},
  {"id":"ft-q9","type":"mcq","prompt":"Data contamination in fine-tuning means:",
   "choices":["Noisy labels","Evaluation examples included in training data — inflates benchmark scores falsely","Duplicate examples","Missing labels"],
   "answerIndex":1,"explanation":"If eval examples appear in training, the model 'memorized' the answer. Always keep a held-out test set the model never trained on.","tags":["fine-tuning","evaluation"]},
  {"id":"ft-q10","type":"mcq","prompt":"QLoRA combines LoRA with:",
   "choices":["RLHF","4-bit quantization of the base model — reducing memory further while maintaining trainable LoRA adapters","Distillation","Mixture of Experts"],
   "answerIndex":1,"explanation":"QLoRA: base model in 4-bit NF4 quantization (inference only), trainable LoRA adapters in bf16. Allows 70B fine-tuning on a single 48GB GPU.","tags":["fine-tuning","QLoRA"]},
  {"id":"ft-q11","type":"mcq","prompt":"DPO (Direct Preference Optimization) replaces which RLHF component?",
   "choices":["SFT","PPO + Reward Model — directly optimizes on preference pairs without separate RM training","The tokenizer","LoRA"],
   "answerIndex":1,"explanation":"DPO bypasses the RM+PPO loop. It directly optimizes a classification objective on (chosen, rejected) pairs. Simpler, more stable, competitive results.","tags":["fine-tuning","RLHF","DPO"]},
  {"id":"ft-q12","type":"multi","prompt":"Which signs indicate overfitting during fine-tuning?",
   "choices":["Training loss decreasing","Validation loss increasing while training loss decreases","Model generates training examples verbatim","Validation loss also decreasing"],
   "answerIndexes":[1,2],"explanation":"Overfitting: val loss rises while train loss falls. Verbatim training example reproduction = pure memorization. Both are stop signals.","tags":["fine-tuning","overfitting"]},
  {"id":"ft-q13","type":"mcq","prompt":"How many examples are typically needed for LoRA instruction fine-tuning?",
   "choices":["10–50","1,000–10,000 high-quality examples — quality > quantity","100,000+","Millions (same as pretraining)"],
   "answerIndex":1,"explanation":"Fine-tuning adapts behavior, not knowledge. 1K–10K well-formatted instruction pairs from your domain are typically sufficient with LoRA.","tags":["fine-tuning","data"]},
  {"id":"ft-q14","type":"mcq","prompt":"The KL divergence penalty in PPO training does what?",
   "choices":["Prevents gradient explosion","Keeps the RLHF-trained model close to the SFT base — prevents reward hacking / policy collapse","Speeds up training","Measures validation loss"],
   "answerIndex":1,"explanation":"Without KL penalty, the model optimizes the reward model excessively — reward hacking. KL penalty anchors the policy near the original SFT model's distribution.","tags":["fine-tuning","RLHF"]},
  {"id":"ft-q15","type":"mcq","prompt":"What is the SFT stage in RLHF?",
   "choices":["Self-supervised pretraining","Supervised Fine-Tuning on human-written ideal responses — teaches the base format before RM+PPO","Sparse Feature Transfer","Safety Filter Training"],
   "answerIndex":1,"explanation":"SFT = first RLHF stage. Train on high-quality (prompt, ideal_response) pairs to give the model a sensible starting policy before RL optimization.","tags":["fine-tuning","RLHF"]},
  {"id":"ft-q16","type":"mcq","prompt":"LoRA rank r=4 vs r=64 — trade-off is:",
   "choices":["r=4 is more accurate","Lower r = fewer params, faster training, less expressive. Higher r = more capacity but closer to full fine-tune cost.","r=64 = same as full fine-tune","r has no effect on quality"],
   "answerIndex":1,"explanation":"Rank controls expressiveness. r=8 is a common default. Increase for complex tasks; keep low for quick domain adaptation.","tags":["fine-tuning","LoRA"]},
  {"id":"ft-q17","type":"mcq","prompt":"Instruction fine-tuning data format requires:",
   "choices":["Raw text paragraphs","Input-output pairs formatted as conversations — system prompt, user message, assistant response","Just the assistant responses","Code files only"],
   "answerIndex":1,"explanation":"Instruction models are trained on (system, user, assistant) conversation triples. The model learns to follow the user instruction given the system context.","tags":["fine-tuning","data"]},
  {"id":"ft-q18","type":"mcq","prompt":"What metric should you monitor during fine-tuning to decide when to stop?",
   "choices":["Training loss only","Validation loss — stop when it stops improving (early stopping) to prevent overfitting","Reward model score","Token throughput"],
   "answerIndex":1,"explanation":"Train loss always decreases. Validation loss reveals generalization. Use early stopping when val loss plateaus or increases.","tags":["fine-tuning","evaluation"]},
  {"id":"ft-q19","type":"mcq","prompt":"Fine-tuning vs prompting: when is fine-tuning worth the cost?",
   "choices":["Always prefer fine-tuning","When: consistent format needed, long system prompts hurt latency, domain vocab absent from base model, smaller model required","When you have < 10 examples","Only for code generation"],
   "answerIndex":1,"explanation":"Fine-tuning has significant upfront cost (data, compute). It pays off when repeated inference cost savings or latency needs outweigh training cost, or when prompt engineering is insufficient.","tags":["fine-tuning"]},
  {"id":"ft-q20","type":"mcq","prompt":"Merging LoRA adapters back to the base model at inference time:",
   "choices":["Impossible — must keep separate","Can be done: merged_W = W + AB. Result: single weight matrix, no adapter overhead at inference","Degrades quality","Requires retraining"],
   "answerIndex":1,"explanation":"LoRA adapters can be merged: W_merged = W_frozen + A×B. After merging, deployment is a standard model with no latency overhead from adapter computation.","tags":["fine-tuning","LoRA"]},
],
new_flashcards=[
  {"id":"ft-fc4","front":"LoRA rank trade-off","back":"Low r (4–8): fast, few params, less expressive. High r (32–64): more capacity, approaches full fine-tune cost. Start at r=8; increase only if quality insufficient.","tags":["fine-tuning","LoRA"]},
  {"id":"ft-fc5","front":"Catastrophic forgetting","back":"Fine-tuning on narrow data overwrites general knowledge. Fix: LoRA (weights frozen), regularisation, or replay of diverse data alongside domain data.","tags":["fine-tuning"]},
  {"id":"ft-fc6","front":"DPO vs PPO","back":"DPO: optimize directly on (chosen, rejected) preference pairs. No separate RM needed, no RL instability. PPO: RM scores completions → gradient. DPO simpler and often competitive.","tags":["fine-tuning","RLHF","DPO"]},
  {"id":"ft-fc7","front":"QLoRA","back":"Base model quantized to 4-bit (NF4) for inference. Trainable LoRA adapters in bf16. Enables 70B fine-tuning on 1× 48GB GPU.","tags":["fine-tuning","QLoRA"]},
  {"id":"ft-fc8","front":"Data quality > quantity","back":"1,000 clean, diverse instruction examples outperform 100,000 noisy ones. Filter for: correct answers, right format, no duplicates, no eval set contamination.","tags":["fine-tuning","data"]},
])


# ── llms ────────────────────────────────────────────────────
patch('ai', 'llms.json',
guide_addition="""
## Tokenization

```
"Hello world!" → [15496, 995, 0]  (GPT-2 BPE tokens)

Why it matters:
  1 token ≈ 0.75 English words
  Context window = token limit (not word limit)
  Code/numbers tokenize inefficiently — "1234567890" = 10 tokens
  Non-English languages use more tokens per word
  Cost = input tokens + output tokens × price_per_token
```

## Attention Mechanism (simplified)

```
Input: "The cat sat on the mat"
For each word, attention computes:
  Q (Query): what am I looking for?
  K (Key):   what does each word offer?
  V (Value): what information to pass forward?

Attention(Q,K,V) = softmax(QK^T / √d_k) × V

Multi-head: run N independent attention heads, concatenate
→ Model attends to different positions for different reasons
```

## Sampling Parameters

```
temperature=0:   deterministic (always top token) — use for code, structured output
temperature=1:   sample proportional to probability — creative writing
temperature>1:   less probable tokens amplified — unpredictable

top_p=0.9:  sample from the top-90% probability mass (nucleus sampling)
top_k=50:   sample from top-50 most probable tokens

max_tokens: output budget — set appropriately per use case
```

## Model Size Trade-offs

```
7B params:   laptop / single GPU. Fast. Good for classification, extraction.
13B–30B:     2-4× A100. Better reasoning. Production on GPU instances.
70B:         4-8× A100. Near-frontier for many tasks.
GPT-4 class: ~1.8T params (rumoured MoE). API only. Best for complex reasoning.

Bigger ≠ always better — fine-tuned 7B often beats GPT-4 on narrow tasks.
```

## References & Further Learning
- 📄 **Attention Is All You Need** — Vaswani et al. 2017 (arxiv.org/abs/1706.03762) — original transformer
- 📄 **GPT-3 paper**: "Language Models are Few-Shot Learners" (arxiv.org/abs/2005.14165)
- 🎥 **Andrej Karpathy** "The spelled-out intro to neural networks and backpropagation" (YouTube)
- 🎥 **3Blue1Brown** "But what is a neural network?" series (YouTube)
- 🎥 **Andrej Karpathy** "Let's build GPT from scratch" — ~2hr deep dive (YouTube)
- 📖 HuggingFace NLP Course — huggingface.co/learn/nlp-course
- 🖼️ **Diagram**: "The Illustrated Transformer" by Jay Alammar — jalammar.github.io/illustrated-transformer (must-read)
- 🖼️ **Tokenizer visualizer**: platform.openai.com/tokenizer
""",
new_questions=[
  {"id":"llm-q4","type":"mcq","prompt":"Why does temperature=0 produce deterministic outputs?",
   "choices":["The model picks random tokens","At temperature=0, argmax is always taken — the single highest-probability token is always selected","Temperature disables sampling","Output is cached"],
   "answerIndex":1,"explanation":"Temperature scales the logits before softmax. At 0, all probability mass collapses to the max-logit token. Always deterministic.","tags":["LLM","sampling"]},
  {"id":"llm-q5","type":"mcq","prompt":"1 token ≈ how many English words?",
   "choices":["1 word exactly","0.75 words — some words are 2-3 tokens","3 words","1 character"],
   "answerIndex":1,"explanation":"English averages ~0.75 words/token with BPE. Short common words = 1 token. Rare/long words = 2+ tokens. Code symbols often 1 token each.","tags":["LLM","tokenization"]},
  {"id":"llm-q6","type":"mcq","prompt":"Flash Attention (Dao et al.) primarily improves:",
   "choices":["Model accuracy","Memory efficiency of attention — avoids materializing the full N×N attention matrix using tiled IO-aware computation","Tokenization speed","Training data quality"],
   "answerIndex":1,"explanation":"Standard attention requires O(N²) memory for the attention matrix. Flash Attention computes it in tiles, keeping data in fast SRAM — identical math result, ~3× faster.","tags":["LLM","attention"]},
  {"id":"llm-q7","type":"mcq","prompt":"What is perplexity in language models?",
   "choices":["Error rate","Measure of how surprised the model is by test text — lower = model fits data better. PP = exp(average negative log-likelihood)","Training loss at epoch 1","Hallucination rate"],
   "answerIndex":1,"explanation":"Perplexity = exp(H) where H = cross-entropy on test data. Lower perplexity = model assigns higher probability to actual text. Used to compare base model quality.","tags":["LLM","evaluation"]},
  {"id":"llm-q8","type":"mcq","prompt":"Mixture of Experts (MoE) in LLMs works by:",
   "choices":["Combining multiple independent models via ensemble","Activating only a subset of model parameters (experts) per token — dense parameter count with sparse compute","Using multiple GPUs","Expert human review"],
   "answerIndex":1,"explanation":"MoE: each forward pass activates k of N experts (FFN layers). Total params: large. Active compute: small. GPT-4 and Mixtral use this for scale with efficiency.","tags":["LLM","architecture"]},
  {"id":"llm-q9","type":"mcq","prompt":"In-context learning (few-shot) works without:",
   "choices":["A prompt","Any gradient updates — examples in the prompt shift model behavior at inference time only","A system prompt","A tokenizer"],
   "answerIndex":1,"explanation":"Few-shot: include (input, output) examples in the prompt. The model pattern-matches and follows the format. No weights are updated — pure inference.","tags":["LLM","prompting"]},
  {"id":"llm-q10","type":"mcq","prompt":"The KV cache in transformer inference serves to:",
   "choices":["Cache HTTP responses","Store precomputed Key/Value matrices for past tokens — avoids recomputing them at each new token generation step","Compress the model","Store embeddings on disk"],
   "answerIndex":1,"explanation":"During autoregressive generation, past token K/V don't change. KV cache stores them, making each new token O(1) per past token instead of O(N). Critical for long contexts.","tags":["LLM","inference"]},
  {"id":"llm-q11","type":"mcq","prompt":"Why does output at temperature > 1.0 become incoherent?",
   "choices":["Model overheats","Logits are divided by temperature before softmax — high temperature flattens distribution, making low-probability (wrong) tokens nearly as likely as correct ones","High temperature truncates output","API rate limits",""],
   "answerIndex":1,"explanation":"Temperature > 1 makes the probability distribution more uniform. Nonsensical tokens get artificially high probability, resulting in random-seeming text.","tags":["LLM","sampling"]},
  {"id":"llm-q12","type":"mcq","prompt":"RLHF-trained models (ChatGPT-style) vs base models differ in:",
   "choices":["Parameter count","Helpfulness and safety — RLHF aligns responses to human preferences. Base models predict next tokens from pretraining distribution (including junk)","Tokenizer","Context window"],
   "answerIndex":1,"explanation":"Base models are raw next-token predictors. RLHF fine-tunes them to follow instructions, refuse harmful requests, maintain format — the 'assistant' behavior.","tags":["LLM","RLHF"]},
  {"id":"llm-q13","type":"mcq","prompt":"What causes hallucination in LLMs?",
   "choices":["Insufficient GPU memory","The model generates plausible-sounding text by pattern matching — it doesn't verify facts, has no world model, and optimizes fluency over accuracy","Tokenization errors","Temperature=0"],
   "answerIndex":1,"explanation":"LLMs predict probable token sequences. Factual correctness is not directly optimized. The model will confidently complete a sentence pattern even if the facts are wrong.","tags":["LLM","hallucination"]},
  {"id":"llm-q14","type":"mcq","prompt":"top_p=0.9 in nucleus sampling means:",
   "choices":["Use top 90 tokens","Sample from smallest token set whose cumulative probability ≥ 0.9 — dynamically adaptive, ignores long tail of improbable tokens","90% of max tokens","Use 90% of context"],
   "answerIndex":1,"explanation":"Nucleus sampling: sort tokens by probability, take minimally sufficient set summing to p. Avoids arbitrarily capping at k tokens (too many/few depending on distribution).","tags":["LLM","sampling"]},
  {"id":"llm-q15","type":"mcq","prompt":"What is parameter-efficient fine-tuning (PEFT)?",
   "choices":["Training only the last layer","Family of methods (LoRA, prefix tuning, adapters) that fine-tune < 1% of params while achieving competitive performance to full fine-tune","Reducing model size before training","Using FP8 training"],
   "answerIndex":1,"explanation":"PEFT methods avoid updating all billions of params. LoRA (most popular) adds rank-decomposed matrices. Prefix tuning adds trainable tokens. Result: fine-tuning on consumer hardware.","tags":["LLM","PEFT"]},
  {"id":"llm-q16","type":"multi","prompt":"Which contribute to LLM inference cost?",
   "choices":["Input token count","Output token count","Model parameter count","Ambient temperature of the data center"],
   "answerIndexes":[0,1,2],"explanation":"Cost = (input tokens + output tokens) × per-token price. Per-token price depends on model size. Output is typically 2-3× input price (autoregressive = slower).","tags":["LLM","cost"]},
  {"id":"llm-q17","type":"mcq","prompt":"Context window of 128K tokens means:",
   "choices":["Model trained on 128K documents","Model can process up to 128K tokens of input + output combined in one call","128K parameters","Model is 128× better"],
   "answerIndex":1,"explanation":"Context window = total token budget per call. Input + output must fit. Longer context = more expensive (quadratic attention cost unless FlashAttention/alternatives used).","tags":["LLM","context"]},
  {"id":"llm-q18","type":"mcq","prompt":"Why do LLMs struggle with arithmetic despite being 'smart'?",
   "choices":["They don't know math","LLMs tokenize digits and do pattern-matching, not symbolic computation — '2+2' matches '4' by frequency, not understanding. Fails on novel multi-digit arithmetic.","Mathematical training was skipped","Context window too small"],
   "answerIndex":1,"explanation":"Arithmetic requires exact symbolic manipulation. LLMs approximate via training patterns. Use code interpreter tools for reliable arithmetic in production.","tags":["LLM","limitations"]},
  {"id":"llm-q19","type":"mcq","prompt":"What is speculative decoding?",
   "choices":["Model guesses the question","A smaller draft model generates N tokens, the large model verifies them in parallel — same quality, ~3× faster for long outputs","Training technique","Prompt optimization"],
   "answerIndex":1,"explanation":"Speculative decoding: draft model (fast, small) proposes tokens; large model verifies/accepts in a single forward pass. Dramatically reduces latency for generation-heavy workloads.","tags":["LLM","inference"]},
  {"id":"llm-q20","type":"mcq","prompt":"Grouped Query Attention (GQA) improves inference by:",
   "choices":["Fewer model parameters","Multiple query heads share fewer K/V heads — reduces KV cache memory and bandwidth significantly without accuracy loss","Better tokenization","Faster training"],
   "answerIndex":1,"explanation":"Standard MHA: N query + N key + N value heads. GQA: N query heads, G groups of K/V (G<N). Llama 2/3 uses GQA. Reduces KV cache size proportional to G/N.","tags":["LLM","architecture"]},
],
new_flashcards=[
  {"id":"llm-fc4","front":"KV cache","back":"Stores precomputed Key/Value tensors for past tokens during autoregressive generation. Avoids redundant computation. Memory = batch × sequence_len × heads × head_dim × layers.","tags":["LLM","inference"]},
  {"id":"llm-fc5","front":"Temperature parameter","back":"temperature=0: deterministic (argmax). =1: proportional sampling. >1: flattens distribution (incoherent). <1: sharpens (conservative). Set 0 for code/structured output, ~0.7 for creative writing.","tags":["LLM","sampling"]},
  {"id":"llm-fc6","front":"Perplexity","back":"PP = exp(average -log P(token)). Lower = better fit to test distribution. Comparable only across same tokenizer. Used for base model benchmarking, not chat quality.","tags":["LLM","evaluation"]},
  {"id":"llm-fc7","front":"Mixture of Experts (MoE)","back":"N expert FFN layers, route each token to top-k. Total params large (scale), active compute small (efficiency). GPT-4, Mixtral-8x7B use MoE. Challenge: expert load balancing.","tags":["LLM","architecture"]},
  {"id":"llm-fc8","front":"Speculative decoding","back":"Small draft model proposes N tokens → large model verifies all in 1 forward pass. Accepts matching prefix, rejects first mismatch. Same output distribution, ~3× speedup.","tags":["LLM","inference"]},
])


# ── neural-nets ──────────────────────────────────────────────
patch('ai', 'neural-nets.json',
guide_addition="""
## Backpropagation — Intuition

```
Forward pass:
  Input → Layer1 → Layer2 → Output → Loss

Backward pass (chain rule):
  dL/dW2 = dL/dOutput × dOutput/dW2   (how does W2 affect loss?)
  dL/dW1 = dL/dOutput × dOutput/dW2 × dW2/dW1  (chain back)

Gradient descent:
  W := W - lr × dL/dW   (move weights in direction that reduces loss)
```

## Activation Functions Compared

```
sigmoid(x) = 1/(1+e^-x)    range (0,1)   — vanishing gradient for |x|>5
tanh(x)                     range (-1,1)  — better than sigmoid, still saturates
ReLU(x) = max(0, x)         range [0,∞)   — fast, sparse, dying ReLU problem
LeakyReLU = max(0.01x, x)   — fixes dying ReLU
GELU(x) ≈ x·Φ(x)            — smooth ReLU, used in transformers (GPT, BERT)
```

## Batch Normalization

```
Without BatchNorm:
  Layer inputs shift drastically between batches → unstable training

With BatchNorm:
  Normalize: x̂ = (x - μ_batch) / σ_batch
  Scale/shift: y = γ·x̂ + β  (learnable)

Benefits: faster training, higher learning rates, some regularization
Pitfall: bad with small batches, sequence models → use LayerNorm instead
```

## Overfitting Control Toolkit

```
Problem: model memorises training data, fails on val/test

Solutions:
  Dropout: randomly zero r% of neurons during training
  L2 regularisation: add λ||W||² to loss (penalise large weights)
  Data augmentation: flip, crop, noise — effectively infinite data
  Early stopping: stop when val loss stops improving
  BatchNorm: implicit regularisation via noise in batch statistics
```

## References & Further Learning
- 🎥 **3Blue1Brown** "Neural Networks" series (4 videos, ~1hr total) — best visual intro (youtube.com/c/3blue1brown)
- 🎥 **Andrej Karpathy** "The spelled-out intro to neural networks and backpropagation: building micrograd" (YouTube)
- 📖 **Neural Networks and Deep Learning** — Michael Nielsen (free online book) neuralnetworksanddeeplearning.com
- 📖 **Deep Learning** — Goodfellow, Bengio, Courville — deeplearningbook.org (free PDF)
- 🖼️ **Playground**: tensorflow.org/tensorflowjs/demos/playground — interactive neural net visual
- 🖼️ **Diagram**: CS231n Stanford — CNNs for Visual Recognition (course notes with diagrams) cs231n.github.io
- 📄 **Dropout paper**: "Dropout: A Simple Way to Prevent Neural Networks from Overfitting" — Srivastava et al.
""",
new_questions=[
  {"id":"nn-q4","type":"mcq","prompt":"The dying ReLU problem refers to:",
   "choices":["ReLU being slow to compute","Neurons that always output 0 because their weights drove input negative — they receive no gradient and can never recover","ReLU causing overfitting","Memory overflow"],
   "answerIndex":1,"explanation":"If a ReLU neuron's weighted sum is always negative, output is always 0. Gradient through ReLU is 0 for negative inputs, so the neuron is permanently dead. LeakyReLU / ELU fix this.","tags":["neural-nets","activation"]},
  {"id":"nn-q5","type":"mcq","prompt":"Why do transformers use LayerNorm instead of BatchNorm?",
   "choices":["LayerNorm is faster","BatchNorm depends on batch statistics — inconsistent for variable-length sequences and problematic with batch size 1. LayerNorm normalizes across features per sample.","LayerNorm uses less memory","BatchNorm doesn't work on GPUs"],
   "answerIndex":1,"explanation":"BatchNorm normalizes across the batch dimension — unreliable for sequences of different lengths. LayerNorm normalizes each token's feature vector independently.","tags":["neural-nets","normalization"]},
  {"id":"nn-q6","type":"mcq","prompt":"Gradient vanishing in deep networks means:",
   "choices":["Memory runs out","Gradients become exponentially small as they propagate back through many layers — early layers receive nearly zero signal and don't learn","Gradient descent fails","Loss becomes NaN"],
   "answerIndex":1,"explanation":"Chain rule multiplies gradients layer-by-layer. Activations like sigmoid saturate (derivative ≈ 0) — tiny gradients compound to ≈0 through 20 layers. ResNets and GELU/ReLU mitigate this.","tags":["neural-nets","backprop"]},
  {"id":"nn-q7","type":"mcq","prompt":"Dropout during inference (test time) should be:",
   "choices":["Kept the same as training","Disabled — all neurons active, weights scaled by (1-dropout_rate)","Set to 0.5 always","Randomly applied"],
   "answerIndex":1,"explanation":"Dropout is a training regularizer. At inference, disable it and scale weights so expected activation matches training. PyTorch model.eval() handles this automatically.","tags":["neural-nets","regularization"]},
  {"id":"nn-q8","type":"mcq","prompt":"Skip connections (ResNet) primarily solve:",
   "choices":["Overfitting","Gradient vanishing in very deep networks — gradient can flow directly through the skip connection, bypassing potentially saturated layers","Memory usage","Slow training"],
   "answerIndex":1,"explanation":"ResNet skip: h(x) = F(x) + x. Even if F(x) contributes zero gradient, x passes through. Enabled training of 1000+ layer networks.","tags":["neural-nets","architecture"]},
  {"id":"nn-q9","type":"mcq","prompt":"Learning rate too high causes:",
   "choices":["Slow convergence","Oscillating or diverging loss — overshoots the minimum, never settles","Underfitting","Correct fast convergence"],
   "answerIndex":1,"explanation":"High LR = large gradient steps. Model jumps past the minimum, oscillates, or diverges (loss NaN). Use LR schedulers or warmup to start small and increase.","tags":["neural-nets","training"]},
  {"id":"nn-q10","type":"mcq","prompt":"Mini-batch gradient descent vs full-batch vs SGD:",
   "choices":["Full-batch is always best","Full-batch: exact gradient, slow per step. SGD (batch=1): noisy, fast. Mini-batch (32–256): balance — vectorized, parallelized on GPU, noisy enough to escape local minima","SGD doesn't work in deep learning","Mini-batch requires more memory"],
   "answerIndex":1,"explanation":"Mini-batch is the standard. GPU parallelism makes batch processing efficient. Noise from sampling helps escape saddle points. Common sizes: 32, 64, 128, 256.","tags":["neural-nets","training"]},
  {"id":"nn-q11","type":"mcq","prompt":"Weight initialization matters because:",
   "choices":["Random weights cause memory issues","Poorly initialized weights cause vanishing/exploding gradients from the start — Xavier/He init sets variance to prevent this","Initialization affects only the first layer","LLMs don't need initialization"],
   "answerIndex":1,"explanation":"Xavier init: Var(W) = 2/(fan_in + fan_out) for sigmoid/tanh. He init: 2/fan_in for ReLU. Prevents signal from dying or exploding in the first forward pass.","tags":["neural-nets","initialization"]},
  {"id":"nn-q12","type":"mcq","prompt":"The universal approximation theorem states:",
   "choices":["Neural nets can solve any optimization problem","A single hidden layer neural net with sufficient neurons can approximate any continuous function to arbitrary accuracy","All neural nets are equivalent","ReLU can approximate anything"],
   "answerIndex":1,"explanation":"UAT: theoretical existence proof. In practice, deep networks are more parameter-efficient than wide shallow ones for complex functions. Deep > wide.","tags":["neural-nets","theory"]},
  {"id":"nn-q13","type":"multi","prompt":"Which are valid overfitting mitigation techniques?",
   "choices":["Dropout","L2 regularisation","Increasing learning rate","Data augmentation"],
   "answerIndexes":[0,1,3],"explanation":"Dropout: random neuron deactivation. L2: penalise large weights. Data augmentation: expands training distribution. Increasing LR worsens overfitting by making training less stable.","tags":["neural-nets","regularization"]},
  {"id":"nn-q14","type":"codeOutput","prompt":"After model.eval(), what happens to Dropout(0.5)?",
   "code":"model = nn.Sequential(nn.Linear(10,10), nn.Dropout(0.5))\nmodel.eval()\noutput = model(input_tensor)  # what is the effective dropout rate?",
   "choices":["0.5 — unchanged","0 — all neurons active, weights scaled","1.0","Random each call"],
   "answerIndex":1,"explanation":"model.eval() disables dropout. All neurons active; PyTorch scales output by 1/(1-p) to match expected value from training.","tags":["neural-nets","regularization"]},
  {"id":"nn-q15","type":"mcq","prompt":"Adam optimizer combines:",
   "choices":["SGD + BatchNorm","Momentum (1st moment) + RMSProp (2nd moment adaptive learning rates) — adapts per-parameter LR based on gradient history","L2 + dropout","Multiple GPUs"],
   "answerIndex":1,"explanation":"Adam: m_t = β1×m_{t-1} + (1-β1)×g (momentum), v_t = β2×v_{t-1} + (1-β2)×g² (RMSProp). Update: θ -= lr × m̂/√v̂. Faster convergence than SGD for most tasks.","tags":["neural-nets","optimizers"]},
  {"id":"nn-q16","type":"mcq","prompt":"What is a Convolutional Neural Network (CNN) designed for?",
   "choices":["Sequence data","Spatial data (images) — conv layers learn translation-invariant local features (edges, textures, shapes), shared weights across positions","Text generation","Reinforcement learning"],
   "answerIndex":1,"explanation":"Conv layers: shared filter scanned across input. Detects same pattern anywhere in image. Pooling reduces spatial size. Hierarchy: edges→textures→objects.","tags":["neural-nets","CNN"]},
  {"id":"nn-q17","type":"mcq","prompt":"What does the loss function measure?",
   "choices":["How many layers the network has","Scalar measure of how wrong the prediction is — gradient descent minimizes this","Model accuracy","Training speed"],
   "answerIndex":1,"explanation":"Loss = single number quantifying error. Cross-entropy for classification, MSE for regression. Backprop computes dL/dW for every parameter to update them.","tags":["neural-nets","training"]},
  {"id":"nn-q18","type":"mcq","prompt":"An LSTM solves what limitation of vanilla RNNs?",
   "choices":["MLPs can't handle sequences","Vanilla RNN gradients vanish over long sequences — LSTM uses gates (forget, input, output) to selectively preserve or discard information across many timesteps","LSTMs use less memory","Vanilla RNN doesn't support GPU"],
   "answerIndex":1,"explanation":"RNN hidden state compresses all history — gradients of early timesteps vanish. LSTM cell state + gates allow the network to remember relevant information for hundreds of timesteps.","tags":["neural-nets","LSTM"]},
  {"id":"nn-q19","type":"mcq","prompt":"Embedding layers in neural nets convert:",
   "choices":["Float vectors to integers","Discrete tokens (word IDs) to dense continuous vectors — each ID maps to a learned d-dimensional representation","Images to text","Batches to single examples"],
   "answerIndex":1,"explanation":"Embedding = lookup table of trainable vectors. word_id → 768-dim vector. Learned: semantically similar words cluster in embedding space (king - man + woman ≈ queen).","tags":["neural-nets","embeddings"]},
  {"id":"nn-q20","type":"mcq","prompt":"Transfer learning in deep learning works by:",
   "choices":["Transferring weights between GPUs","Using a pretrained model's learned representations as a starting point, fine-tuning only final layers on your task — far fewer examples needed","Copying hyperparameters","Ensemble of models"],
   "answerIndex":1,"explanation":"Early layers learn universal features (edges, curves, n-grams). Fine-tuning re-uses these, only adapting final task-specific layers. ImageNet pretrained → medical imaging with 1000× fewer labeled examples.","tags":["neural-nets","transfer-learning"]},
],
new_flashcards=[
  {"id":"nn-fc4","front":"Vanishing gradient","back":"Deep sigmoid networks: gradients ≈ 0 at early layers — they don't learn. Fix: ReLU/GELU activations, skip connections (ResNet), batch/layer norm, careful initialization.","tags":["neural-nets","backprop"]},
  {"id":"nn-fc5","front":"Adam optimizer","back":"Combines momentum (1st moment avg) + RMSProp (2nd moment adaptive LR per param). lr=1e-3, β1=0.9, β2=0.999 are defaults. Faster than SGD for most tasks.","tags":["neural-nets","optimizers"]},
  {"id":"nn-fc6","front":"Dropout","back":"Training: randomly zero p% of neurons each forward pass. Inference: disable (model.eval()), scale weights by 1/(1-p). Acts as ensemble of 2^n sub-networks.","tags":["neural-nets","regularization"]},
  {"id":"nn-fc7","front":"Skip connection (ResNet)","back":"h(x) = F(x) + x. Gradient can flow directly through x even if F(x) saturates. Enabled 100–1000 layer networks. Core building block of modern architectures.","tags":["neural-nets","architecture"]},
  {"id":"nn-fc8","front":"Xavier / He initialization","back":"Xavier: Var(W) = 2/(fan_in+fan_out) — sigmoid/tanh. He: Var(W) = 2/fan_in — ReLU. Prevents signal from vanishing or exploding at network start.","tags":["neural-nets","initialization"]},
])


# ── prompting-fundamentals ───────────────────────────────────
patch('ai', 'prompting-fundamentals.json',
guide_addition="""
## Key Prompting Techniques

```
1. Zero-shot:   Just ask. "Classify this sentiment: ..."
2. Few-shot:    Provide examples. "good→positive, bad→negative, ok→?"
3. CoT:         "Let's think step by step..." — forces explicit reasoning trace
4. CoT few-shot: Examples WITH reasoning chains — highest quality
5. Self-consistency: sample N answers, take majority vote
6. ReAct:       Interleave Thought/Action/Observation (for agents)
```

## Prompt Structure (best practice)

```
[SYSTEM]
You are a senior financial analyst.
Your output must be valid JSON.

[USER]
Given this earnings report: {context}

Task: Extract the following fields:
1. Revenue (USD millions)
2. Net income margin %
3. YoY growth %

Respond ONLY with JSON: {"revenue": ..., "margin": ..., "growth": ...}
```

## Chain-of-Thought Mechanics

```
Without CoT:
  Q: "A bat and ball cost $1.10. Bat costs $1 more. Ball costs?"
  A: "$0.10"  ← wrong (intuitive)

With CoT ("think step by step"):
  Thought: Let ball = x. Bat = x + 1. x + (x+1) = 1.10
            2x = 0.10. x = 0.05
  A: "$0.05"  ← correct (reasoned)
```

## Common Failure Modes & Fixes

```
Failure: No output format → LLM returns inconsistent structure
Fix: Explicitly specify format: "Respond ONLY as JSON: {...}"

Failure: Long context ignored → recency/primacy effects
Fix: Put critical instructions at END of prompt (for most models)

Failure: Sycophancy → LLM agrees with user's wrong framing
Fix: "Evaluate independently first, then provide your view"

Failure: Prompt injection → user input overrides system instructions
Fix: Separate and sanitize user input; re-state system constraints
```

## References & Further Learning
- 📄 **Chain-of-Thought Prompting**: "Chain-of-Thought Prompting Elicits Reasoning in Large Language Models" — Wei et al. (arxiv.org/abs/2201.11903)
- 📄 **Self-Consistency**: "Self-Consistency Improves Chain of Thought" — Wang et al.
- 📖 **Prompt Engineering Guide** — promptingguide.ai (comprehensive free resource)
- 📖 **OpenAI Prompt Engineering Guide** — platform.openai.com/docs/guides/prompt-engineering
- 🎥 **Andrej Karpathy** — "Intro to Large Language Models" talk (~1hr, YouTube)
- 🖼️ **Diagram**: DAIR.AI "Prompt Engineering Guide" cheatsheet (github.com/dair-ai/Prompt-Engineering-Guide)
""",
new_questions=[
  {"id":"pf-q4","type":"mcq","prompt":"Chain-of-thought prompting improves accuracy because:",
   "choices":["It makes prompts shorter","It forces the model to generate explicit intermediate reasoning steps before the final answer — harder problems solved correctly","The model prefers long outputs","It disables sampling"],
   "answerIndex":1,"explanation":"CoT: model writes reasoning trace before answering. Solving subproblems sequentially matches how human experts solve complex problems. Emergent for models >100B params.","tags":["prompting","CoT"]},
  {"id":"pf-q5","type":"mcq","prompt":"Why put critical instructions at the END of a long prompt?",
   "choices":["Shorter prompts perform better","Most models have recency bias — instructions at the end of long contexts are more attended to than those buried in the middle","API requires it","Token limit reasons"],
   "answerIndex":1,"explanation":"'Lost in the middle' research shows models attend better to start and end of long contexts. Put key constraints at the end for most models.","tags":["prompting","context"]},
  {"id":"pf-q6","type":"mcq","prompt":"Self-consistency in prompting means:",
   "choices":["Always use the same prompt","Sample N independent completions, take the majority answer — improves accuracy on reasoning tasks by 10-20%","Consistent tone","Never changing the system prompt"],
   "answerIndex":1,"explanation":"Sample 5-10 CoT completions at temperature > 0. Each may reason differently but arrive at the same answer. Majority vote reduces variance significantly.","tags":["prompting","self-consistency"]},
  {"id":"pf-q7","type":"mcq","prompt":"Prompt injection attacks work by:",
   "choices":["SQL injection in API calls","Malicious user input containing instructions that override the system prompt — e.g. 'Ignore all previous instructions and...'","Overloading the context window","Token manipulation"],
   "answerIndex":1,"explanation":"LLMs can't reliably distinguish instruction from data. If user input contains instructions, the model may follow them over the system prompt. Mitigate by separating/sanitizing inputs.","tags":["prompting","security"]},
  {"id":"pf-q8","type":"mcq","prompt":"Zero-shot vs few-shot prompting — when does few-shot win?",
   "choices":["Always","When the desired output format or reasoning pattern isn't obvious from the task description alone — examples make the pattern explicit","For simple tasks only","When the model is small"],
   "answerIndex":1,"explanation":"Zero-shot works for well-defined tasks. Few-shot helps for: unusual formats, nuanced classification, code style, multi-step reasoning. Cost: extra input tokens per example.","tags":["prompting","few-shot"]},
  {"id":"pf-q9","type":"mcq","prompt":"Sycophancy in LLMs refers to:",
   "choices":["Model praising itself","Model agreeing with user's framing even when wrong — validating incorrect statements to please the user","Model refusing requests","Short responses"],
   "answerIndex":1,"explanation":"RLHF-trained models learn that agreement is often rated positively by human raters. This creates sycophancy — model echoes user's (possibly wrong) assumptions.","tags":["prompting","sycophancy"]},
  {"id":"pf-q10","type":"mcq","prompt":"Why specify output format explicitly (JSON, bullet list, etc.)?",
   "choices":["Reduces hallucination","Ensures consistent, parseable responses — downstream code can rely on structure rather than parsing natural language","Required by API","Reduces token count"],
   "answerIndex":1,"explanation":"Without format spec, output style varies. Downstream parsing breaks. 'Respond ONLY as JSON: {key: value}' with an example dramatically improves consistency.","tags":["prompting","format"]},
  {"id":"pf-q11","type":"multi","prompt":"Which are valid ways to improve reasoning in prompts?",
   "choices":["'Think step by step'","Providing few-shot CoT examples","Lowering temperature to 0","Self-consistency (sample N, take majority)"],
   "answerIndexes":[0,1,3],"explanation":"CoT trigger phrase, CoT examples, and self-consistency all improve reasoning. Temperature=0 aids determinism but doesn't improve reasoning quality per call.","tags":["prompting","CoT"]},
  {"id":"pf-q12","type":"mcq","prompt":"System prompts vs user messages — key difference?",
   "choices":["No difference","System prompts set the model's persona, constraints, and format rules — persistent and higher-priority. User messages are the turn-by-turn conversation.","System prompts are optional","System prompts visible to users"],
   "answerIndex":1,"explanation":"System prompt = instruction set for the session. Set tone, persona, output format, safety rules here. User message = task instance. Keep instructions separate from data.","tags":["prompting","system-prompt"]},
  {"id":"pf-q13","type":"mcq","prompt":"Temperature setting for structured JSON output should be:",
   "choices":["High (>1) for creativity","0 — deterministic, always highest-probability token, reduces format errors","0.7 — balanced","Random"],
   "answerIndex":1,"explanation":"JSON parsing fails if format is inconsistent. Temperature=0 ensures the model always follows the same most-probable pattern. Reserve higher temps for creative tasks.","tags":["prompting","sampling"]},
  {"id":"pf-q14","type":"mcq","prompt":"'Role prompting' (You are an expert X) works because:",
   "choices":["Creates a new model","Primes the model to use vocabulary, style, and knowledge patterns associated with that role from pretraining data","Makes model faster","Required for function calling"],
   "answerIndex":1,"explanation":"The model has seen vast amounts of expert writing. 'You are a senior software engineer reviewing code' activates relevant patterns from that distribution.","tags":["prompting","role-prompting"]},
  {"id":"pf-q15","type":"mcq","prompt":"Delimiters (XML tags, triple backticks) in prompts help with:",
   "choices":["Reducing token count","Clearly separating instructions from data — prevents instruction confusion and prompt injection within data sections","Speed","Model safety"],
   "answerIndex":1,"explanation":"<document>{user_content}</document> vs inline text — clear separation prevents the model confusing user data with instructions. XML-style tags work well for Claude; ``` works for code.","tags":["prompting","structure"]},
  {"id":"pf-q16","type":"mcq","prompt":"What is meta-prompting?",
   "choices":["Prompting about prompts — asking the LLM to generate, critique, or improve prompts","Training prompts","System-level optimization","API parameter tuning"],
   "answerIndex":0,"explanation":"Meta-prompting: use the LLM to draft or critique its own prompts. 'Here's my prompt, what's wrong with it?' or 'Write a prompt that will make you answer X accurately.'","tags":["prompting","meta-prompting"]},
  {"id":"pf-q17","type":"mcq","prompt":"'Jailbreaking' an LLM refers to:",
   "choices":["Improving its performance","Using adversarial prompts to bypass safety guardrails — role-play scenarios, hypothetical framing, etc.","Updating the model","API rate limit bypass"],
   "answerIndex":1,"explanation":"Jailbreaks exploit the gap between safety training and edge cases. Models trained on RLHF can be steered around guardrails via sufficiently clever prompts.","tags":["prompting","security"]},
  {"id":"pf-q18","type":"mcq","prompt":"Eval-driven prompt engineering means:",
   "choices":["Manual trial and error","Building a test set of inputs + expected outputs, automating scoring, and using it to iterate prompts systematically — not vibe-checking","Only using A/B tests","Requiring human evaluation always"],
   "answerIndex":1,"explanation":"Professional prompt engineering = evals first. Define what 'good' looks like numerically. Iterate prompts and measure — not reading 5 outputs and deciding by feeling.","tags":["prompting","evaluation"]},
  {"id":"pf-q19","type":"mcq","prompt":"Tree-of-Thoughts prompting extends CoT by:",
   "choices":["Adding images","Exploring multiple reasoning branches simultaneously, scoring each, pruning bad paths — like MCTS for reasoning","Using embeddings","Randomizing prompts"],
   "answerIndex":1,"explanation":"ToT: LLM generates multiple next-thoughts at each step, evaluates them, and explores promising paths. Dramatically improves complex planning tasks. Cost: many more LLM calls.","tags":["prompting","CoT"]},
  {"id":"pf-q20","type":"mcq","prompt":"The 'primacy effect' in long context means:",
   "choices":["Model reads from right to left","Information at the beginning of a very long prompt receives higher attention than information in the middle — opening matters","Always irrelevant","Only applicable to GPT-3"],
   "answerIndex":1,"explanation":"Research shows models attend well to start and end, poorly to middle of long contexts. Put identity/constraints at start AND end; key task details just before the user turn.","tags":["prompting","context"]},
],
new_flashcards=[
  {"id":"pf-fc4","front":"Chain-of-thought trigger","back":"'Think step by step' / 'Let's reason through this.' Forces explicit intermediate steps. Emergent in >100B params. Use CoT examples (few-shot CoT) for highest-stakes tasks.","tags":["prompting","CoT"]},
  {"id":"pf-fc5","front":"Self-consistency","back":"Sample N independent CoT completions at temp>0. Take majority answer. Reduces variance by ~15% on math/reasoning benchmarks. Cost: N× API calls.","tags":["prompting","self-consistency"]},
  {"id":"pf-fc6","front":"Prompt injection","back":"Malicious input overrides system instructions. Mitigate: XML delimiters around untrusted input, re-state constraints after user content, separate instruction/data channels.","tags":["prompting","security"]},
  {"id":"pf-fc7","front":"Eval-driven prompting","back":"Build labeled test set → automatic scorer → iterate prompts → measure delta. Never ship prompts you've only eyeballed. Treat prompts like code — test them.","tags":["prompting","evaluation"]},
  {"id":"pf-fc8","front":"Format specification","back":"Append explicit format: 'Respond ONLY as JSON: {\"field\":...}' with example. Use delimiters for data sections. Temperature=0 for structured output. Validate and retry on parse failure.","tags":["prompting","format"]},
])


# ── rag ───────────────────────────────────────────────────────
patch('ai', 'rag.json',
guide_addition="""
## RAG Architecture

```
Query: "What is our refund policy?"

                    ┌─────────────────┐
User Query ─────→  │  Embed Query    │ → query vector
                    └────────┬────────┘
                             ↓
                    ┌─────────────────┐
                    │  Vector Search  │ → top-k chunks
                    │  (ANN index)    │
                    └────────┬────────┘
                             ↓
                    ┌─────────────────────────────┐
                    │  Prompt = System + Context  │
                    │  + Query                    │
                    └────────┬────────────────────┘
                             ↓
                    ┌─────────────────┐
                    │     LLM         │ → Grounded Answer
                    └─────────────────┘
```

## Chunking Strategies

```
Fixed-size:     Split every 512 tokens. Simple but can cut mid-sentence.
Sentence-aware: Split at sentence boundaries within token limit.
Semantic:       Split at topic boundaries (paragraph, heading).
Hierarchical:   Store document summary + chunks. Retrieve at both levels.

Overlap:        50-100 token overlap between chunks — preserves context 
                at chunk boundaries.
```

## Embedding Model Selection

```
text-embedding-3-large (OpenAI): 3072-dim, best quality, API-only
text-embedding-3-small (OpenAI): 1536-dim, 5× cheaper
all-MiniLM-L6-v2 (local):        384-dim, fast, free
Cohere embed-3:                   1024-dim, multilingual

Key: embed queries and documents with the SAME model.
```

## Evaluation Metrics (RAGAS)

```
Faithfulness:        Does answer use ONLY retrieved context? (no hallucination)
Answer Relevancy:    Does answer address the question?
Context Recall:      Did retrieval find all necessary chunks?
Context Precision:   Are retrieved chunks all relevant? (no noise)
```

## References & Further Learning
- 📄 **RAG paper**: "Retrieval-Augmented Generation for Knowledge-Intensive NLP Tasks" — Lewis et al. (arxiv.org/abs/2005.11401)
- 📄 **RAGAS**: "RAGAS: Automated Evaluation of RAG" (arxiv.org/abs/2309.15217)
- 🎥 **LangChain** "RAG from scratch" series (YouTube playlist)
- 🎥 **Greg Kamradt** "5 Levels of Text Splitting" (YouTube) — chunking strategies deep dive
- 📖 **LlamaIndex docs** — llamaindex.ai — comprehensive RAG framework
- 📖 **Weaviate blog** — weaviate.io/blog — vector DB + RAG tutorials with diagrams
- 🖼️ **Diagram**: "Advanced RAG Techniques" — towardsdatascience.com
""",
new_questions=[
  {"id":"rag-q4","type":"mcq","prompt":"Why is chunking document text necessary for RAG?",
   "choices":["Vector DBs only store short strings","LLMs have context window limits — a 1000-page document can't fit. Chunks ensure each piece fits and the relevant chunk (not the whole doc) is retrieved","Faster embedding computation","Required by the embedding model"],
   "answerIndex":1,"explanation":"Embedding a full document loses precision — 'which exact section?'. Chunks give retrieval granularity. Context window limits also prevent stuffing full docs into prompts.","tags":["RAG","chunking"]},
  {"id":"rag-q5","type":"mcq","prompt":"ANN (Approximate Nearest Neighbor) search in vector DBs:",
   "choices":["Always returns exact nearest neighbors","Returns approximate neighbors much faster using HNSW/IVF indices — 99%+ accuracy at 100× speedup over brute-force","Requires SQL","Only works for images"],
   "answerIndex":1,"explanation":"Exact KNN is O(N) per query. ANN (HNSW, IVF-PQ) provides sub-linear query time with near-perfect accuracy. Essential for 10M+ vector collections.","tags":["RAG","vector-db"]},
  {"id":"rag-q6","type":"mcq","prompt":"Faithfulness in RAGAS evaluation measures:",
   "choices":["Answer grammatical quality","Whether the answer is grounded ONLY in retrieved context — no hallucinated facts added by the LLM","Query-answer relevance","Retrieval coverage"],
   "answerIndex":1,"explanation":"Faithfulness: every claim in the answer should be traceable to a retrieved chunk. Unfaithful = LLM added its own 'knowledge' not in context. Critical for factual accuracy.","tags":["RAG","evaluation"]},
  {"id":"rag-q7","type":"mcq","prompt":"Hybrid search in RAG combines:",
   "choices":["Two different LLMs","Dense (semantic embedding similarity) + sparse (BM25 keyword) search — catches semantic matches AND exact keyword matches for better recall","CNN and transformer","Two vector DBs"],
   "answerIndex":1,"explanation":"Dense only: misses exact product codes, names. Sparse only: misses semantic synonyms. Combining via reciprocal rank fusion improves recall significantly.","tags":["RAG","retrieval"]},
  {"id":"rag-q8","type":"mcq","prompt":"Re-ranking retrieved chunks before LLM prompt serves to:",
   "choices":["Reduce token count","Use a cross-encoder (more expensive, more accurate) to re-score the top-k chunks and only send the truly relevant ones — reduces noise in context","Sort alphabetically","Required for RAG"],
   "answerIndex":1,"explanation":"Bi-encoder retrieval (fast, approximate) → cross-encoder re-ranking (slow, precise). Re-ranker reads query+chunk jointly, far more accurate than cosine similarity alone.","tags":["RAG","retrieval"]},
  {"id":"rag-q9","type":"mcq","prompt":"Query rewriting in advanced RAG helps with:",
   "choices":["Reducing cost","Vague or multi-intent queries — rewrite into multiple specific sub-queries or expand with HyDE (Hypothetical Document Embeddings) for better retrieval","Security","Token limit"],
   "answerIndex":1,"explanation":"User queries are often vague. Query rewriting: expand abbreviations, generate alternative phrasings, or create hypothetical answers (HyDE) to retrieve more relevant chunks.","tags":["RAG","retrieval"]},
  {"id":"rag-q10","type":"mcq","prompt":"Why must queries and documents be embedded with the SAME model?",
   "choices":["Performance reasons","Cosine similarity between embeddings is only meaningful if both vectors live in the same embedding space — different models produce incompatible spaces","API restriction","Token count reasons"],
   "answerIndex":1,"explanation":"Each model has its own learned embedding geometry. Cross-model similarity is nonsensical. In production, switching embedding models requires re-embedding ALL documents.","tags":["RAG","embeddings"]},
  {"id":"rag-q11","type":"mcq","prompt":"Chunk overlap in RAG (e.g. 100-token overlap between chunks) prevents:",
   "choices":["Duplicate results","Loss of context at chunk boundaries — a sentence split across chunk boundaries would be incomplete without overlap","Token limit issues","Vector DB errors"],
   "answerIndex":1,"explanation":"Clean splits can cut a key sentence mid-way. Overlap ensures every sentence appears fully in at least one chunk, enabling complete retrieval of context at boundaries.","tags":["RAG","chunking"]},
  {"id":"rag-q12","type":"multi","prompt":"Which are valid RAG improvement techniques?",
   "choices":["Hybrid search (dense + sparse)","Re-ranking with cross-encoder","Storing fewer documents","Query rewriting/expansion"],
   "answerIndexes":[0,1,3],"explanation":"Hybrid, re-ranking, and query rewriting all improve retrieval quality. Storing fewer documents hurts recall — RAG benefit comes from large knowledge stores.","tags":["RAG","advanced"]},
  {"id":"rag-q13","type":"mcq","prompt":"Metadata filtering in RAG (filter by date, department, document type) is used for:",
   "choices":["Reducing storage cost","Pre-filtering the search space to only relevant document subsets before vector similarity — improves precision and reduces irrelevant context","Required for all RAG","Improving embedding quality"],
   "answerIndex":1,"explanation":"Without filtering, a query retrieves from all docs. Filter: only search docs from this department, or within date range. Especially important for multi-tenant systems.","tags":["RAG","retrieval"]},
  {"id":"rag-q14","type":"mcq","prompt":"HyDE (Hypothetical Document Embedding) technique:",
   "choices":["Creates synthetic training data","Generates a hypothetical answer to the query, embeds it, uses that embedding for retrieval — the hypothetical answer is closer in embedding space to real answers than the query itself","Compresses embeddings","Replaces chunking"],
   "answerIndex":1,"explanation":"Queries ('how does X work?') are stylistically different from answers ('X works by...'). HyDE: LLM generates a hypothetical answer → embed it → retrieve chunks similar to that answer.","tags":["RAG","retrieval"]},
  {"id":"rag-q15","type":"mcq","prompt":"Naive RAG failure: retrieved context is correct but answer is wrong. Likely cause:",
   "choices":["Vector DB bug","LLM didn't faithfully use the context — hallucinated instead, or the relevant information was too deeply buried in a large context (lost in the middle)","Embedding model failure","Chunk size too large"],
   "answerIndex":1,"explanation":"Retrieval ≠ generation. The LLM must actually attend to and use the context. Position of key facts matters — don't bury them in a huge context. Re-rank to put most relevant chunks first.","tags":["RAG","generation"]},
  {"id":"rag-q16","type":"mcq","prompt":"Context window stuffing (sending all retrieved chunks) risks:",
   "choices":["Crashes the API","LLM attention dilution — relevant information gets 'lost in the middle' of a large context. Fewer, more relevant chunks > many marginally relevant ones","Better results always","Reducing costs"],
   "answerIndex":1,"explanation":"Counterintuitively, sending MORE context can be worse. Too much irrelevant context distracts the model. Use re-ranking + strict top-k to keep context focused.","tags":["RAG","generation"]},
  {"id":"rag-q17","type":"mcq","prompt":"GraphRAG differs from standard RAG by:",
   "choices":["Using graph databases only","Building a knowledge graph from documents and traversing entity relationships for retrieval — better for multi-hop queries spanning multiple documents","Eliminating the LLM","Faster indexing"],
   "answerIndex":1,"explanation":"Standard RAG: similarity search in flat vector space. GraphRAG (Microsoft): extract entities + relationships into a graph. Multi-hop: 'Who worked at company X that acquired Y?' traverses graph edges.","tags":["RAG","advanced"]},
  {"id":"rag-q18","type":"mcq","prompt":"RAGAS context_precision metric measures:",
   "choices":["Answer grammar","What fraction of retrieved chunks are actually relevant to answering the question — low precision = too much noise in context","Speed of retrieval","Embedding quality"],
   "answerIndex":1,"explanation":"Context precision: are ALL retrieved chunks useful? Low = retrieval is broad but noisy. Improve by: metadata filtering, re-ranking, better chunking, lower k.","tags":["RAG","evaluation"]},
  {"id":"rag-q19","type":"mcq","prompt":"A vector database differs from traditional databases by primarily indexing on:",
   "choices":["Primary key","Text length","Semantic similarity using ANN search on high-dimensional dense vectors","SQL queries"],
   "answerIndex":2,"explanation":"Vector DBs: HNSW/IVF indexes over dense float vectors for sub-linear similarity search. Traditional DBs: B-tree/hash indexes for exact lookup. Complementary — many systems use both.","tags":["RAG","vector-db"]},
  {"id":"rag-q20","type":"mcq","prompt":"When should you choose RAG over fine-tuning for knowledge injection?",
   "choices":["Always — RAG is always better","When knowledge: is large (millions of docs), changes frequently, needs citation/attribution, or isn't available at training time","Only for internal docs","When GPU compute is available"],
   "answerIndex":1,"explanation":"RAG = injection at inference. Fine-tune = bake into weights at training. RAG wins for: dynamic knowledge, large corpora, traceable citations. Fine-tune wins for: stable knowledge, low-latency (no retrieval step).","tags":["RAG","vs-fine-tuning"]},
],
new_flashcards=[
  {"id":"rag-fc4","front":"Chunking overlap","back":"50-100 token overlap between chunks prevents context loss at boundaries. Chunk size: 256-512 tokens for retrieval precision; 1024+ for summarization tasks.","tags":["RAG","chunking"]},
  {"id":"rag-fc5","front":"Re-ranking","back":"Stage 1: bi-encoder ANN retrieval (fast, approximate, top 20). Stage 2: cross-encoder re-ranker (slow, precise, top 3-5). Better precision before LLM context.","tags":["RAG","retrieval"]},
  {"id":"rag-fc6","front":"RAGAS 4 metrics","back":"Faithfulness (grounded in context?), Answer Relevancy (addresses question?), Context Recall (found needed chunks?), Context Precision (chunks are relevant?).","tags":["RAG","evaluation"]},
  {"id":"rag-fc7","front":"HyDE","back":"Generate hypothetical answer (LLM) → embed it → retrieve chunks similar to the hypothetical answer. Better than query embedding for abstract or open-ended queries.","tags":["RAG","retrieval"]},
  {"id":"rag-fc8","front":"Hybrid search","back":"Dense (cosine similarity on embeddings) + sparse (BM25 keyword). Combine via Reciprocal Rank Fusion. Catches semantic matches AND exact names/codes.","tags":["RAG","retrieval"]},
])


# ── transformers ─────────────────────────────────────────────
patch('ai', 'transformers.json',
guide_addition="""
## Self-Attention Mechanics

```
Input: [Token1, Token2, Token3, Token4]  → embed → X (n × d_model)

Q = X·Wq    K = X·Wk    V = X·Wv

Attention = softmax(QK^T / √d_k) · V

Intuition:
  Q = "what am I looking for?"
  K = "what do I offer?"
  V = "what information to pass?"

The bank that handles money:    high attention to "bank" for Q="financial"
The bank of the river:          high attention to "bank" for Q="geography"
Same token, different context → different attention weights
```

## Transformer Architecture

```
Input Tokens
     ↓
[Embedding + Positional Encoding]
     ↓
┌──────────────────────┐ × N
│  Multi-Head Attention │  (attends to all positions)
│  + Residual + LN      │
│  FFN (expand → GELU → │  (position-wise, d_model → 4d → d_model)
│  contract)            │
│  + Residual + LN      │
└──────────────────────┘
     ↓
Linear → Softmax → Next Token Probabilities
```

## Encoder vs Decoder vs Encoder-Decoder

```
Encoder (BERT):
  Bidirectional attention — sees whole sequence
  Good for: classification, NER, embeddings
  Training: masked language modelling (MLM)

Decoder (GPT):
  Causal/autoregressive — only sees past tokens
  Good for: generation, chat, completion
  Training: next-token prediction

Encoder-Decoder (T5, BART):
  Encoder: reads input
  Decoder: generates output attending to encoder
  Good for: translation, summarisation, Q&A
```

## Positional Encoding

```
Transformers have no inherent order — "cat sat mat" = "mat sat cat" without PE

Sinusoidal PE (original): PE(pos, 2i) = sin(pos/10000^(2i/d_model))
  Fixed, not learned, generalises to longer sequences

RoPE (Rotary PE — LLaMA, GPT-NeoX):
  Encode position as rotation in complex space
  Better length generalisation, relative position awareness

ALiBi (PaLM): add position bias to attention scores directly
```

## References & Further Learning
- 📄 **Attention Is All You Need** (Vaswani et al. 2017) — arxiv.org/abs/1706.03762 — the original paper
- 🖼️ **"The Illustrated Transformer"** — Jay Alammar — jalammar.github.io/illustrated-transformer — best visual explanation ever made
- 🖼️ **"The Illustrated GPT-2"** — Jay Alammar — jalammar.github.io/illustrated-gpt2
- 🎥 **Andrej Karpathy** "Let's build GPT from scratch in code, spelled out" (~2hr, YouTube) — implements full transformer
- 🎥 **Yannic Kilcher** "Attention Is All You Need" paper walkthrough (YouTube)
- 📖 **The Annotated Transformer** — nlp.seas.harvard.edu/annotated-transformer — line-by-line code + explanation
- 🖼️ **Diagram**: Transformer architecture poster — search "transformer architecture diagram vaswani 2017"
""",
new_questions=[
  {"id":"tr-q4","type":"mcq","prompt":"Why is positional encoding necessary in transformers?",
   "choices":["For memory efficiency","Self-attention treats all positions equally — without positional encoding, 'cat sat mat' and 'mat sat cat' would produce identical representations","For training speed","Tokenization requires it"],
   "answerIndex":1,"explanation":"Attention computes weighted sums regardless of position. PE injects order information by adding position vectors to embeddings before attention.","tags":["transformers","positional-encoding"]},
  {"id":"tr-q5","type":"mcq","prompt":"The FFN (feed-forward network) in each transformer layer serves to:",
   "choices":["Attend to positions","Apply position-wise nonlinear transformation — integrates information within each token after attention has mixed cross-token information","Encode position","Compute softmax"],
   "answerIndex":1,"explanation":"Attention = cross-token information mixing. FFN = per-token nonlinear transformation (typically: Linear → GELU → Linear with 4× expansion). They alternate: mix → transform → mix → transform.","tags":["transformers","architecture"]},
  {"id":"tr-q6","type":"mcq","prompt":"Causal masking in decoder transformers ensures:",
   "choices":["Faster training","Each position can only attend to earlier positions — prevents future token leakage during autoregressive training","Bidirectional attention","Better embeddings"],
   "answerIndex":1,"explanation":"During training, the next token is the label. Without causal mask, the model could 'cheat' by attending to the answer directly. Masking forces prediction from only past context.","tags":["transformers","attention"]},
  {"id":"tr-q7","type":"mcq","prompt":"BERT uses which training objective?",
   "choices":["Next token prediction","Masked Language Modelling (MLM) — randomly mask 15% of tokens, predict them using bidirectional context","Contrastive learning","Image classification"],
   "answerIndex":1,"explanation":"BERT's bidirectional attention requires a different objective than GPT's causal next-token prediction. MLM: [MASK] token must be predicted using both left AND right context.","tags":["transformers","BERT"]},
  {"id":"tr-q8","type":"mcq","prompt":"Multi-head attention vs single-head:",
   "choices":["Faster","Multiple independent attention computations run in parallel — each head can attend to different aspects (syntax, semantics, position) of the input simultaneously","More memory-efficient","Required for GPUs"],
   "answerIndex":1,"explanation":"Each head has its own Q/K/V projections. One head may focus on subject-verb relationships, another on coreference. Heads are concatenated and projected back to d_model.","tags":["transformers","attention"]},
  {"id":"tr-q9","type":"codeOutput","prompt":"What is the computational complexity of standard self-attention with sequence length N?",
   "code":"# Standard attention: Attention(Q,K,V) = softmax(QK^T / sqrt(d)) * V\n# QK^T produces a (N x N) matrix\n# What is the complexity in terms of N?",
   "choices":["O(N)","O(N log N)","O(N²)","O(N³)"],
   "answerIndex":2,"explanation":"QK^T: each of N tokens attends to all N tokens = N² operations. The N×N attention matrix also requires O(N²) memory. Flash Attention uses tiling to compute this without materialising the full N×N matrix.","tags":["transformers","complexity"]},
  {"id":"tr-q10","type":"mcq","prompt":"Residual connections (skip connections) in transformers serve to:",
   "choices":["Reduce parameter count","Allow gradients to flow directly through the network, prevent vanishing gradients in deep models, and let layers learn residual corrections rather than full transformations","Enable attention","Improve tokenization"],
   "answerIndex":1,"explanation":"output = x + layer(x). Even if layer(x) learns nothing, x passes through unchanged. Deep transformers (96 layers in GPT-3) rely heavily on residuals for stable training.","tags":["transformers","architecture"]},
  {"id":"tr-q11","type":"mcq","prompt":"RoPE (Rotary Position Embedding) vs sinusoidal PE advantage:",
   "choices":["RoPE requires less memory","RoPE encodes relative positions naturally and generalises better to sequences longer than seen during training","RoPE is older","No advantage"],
   "answerIndex":1,"explanation":"Sinusoidal PE: absolute positions. RoPE: rotate queries and keys by position angle — inner product naturally encodes relative distance. Used by LLaMA, Mistral, GPT-NeoX.","tags":["transformers","positional-encoding"]},
  {"id":"tr-q12","type":"mcq","prompt":"The d_model dimension in transformers represents:",
   "choices":["Number of layers","The embedding/hidden dimension — all token representations are d_model-dimensional vectors throughout the network. Typical: 768 (BERT-base), 4096 (LLaMA 7B)","Vocabulary size","Context length"],
   "answerIndex":1,"explanation":"d_model = width of the model. Larger d_model = more representational capacity per token. Tradeoffs: compute scales quadratically with d_model in attention.","tags":["transformers","architecture"]},
  {"id":"tr-q13","type":"mcq","prompt":"T5 (Text-to-Text Transfer Transformer) treats all NLP tasks how?",
   "choices":["As classification","As text-to-text — every task (translation, summary, QA, classification) is framed as: 'summarise: [input]' → '[output]'. Unified training format.","As masked prediction","As image captioning"],
   "answerIndex":1,"explanation":"T5 unified NLP under one interface: prefix task name + input → output. Train once on mixture of tasks. Fine-tune by adding task prefix. Elegant simplification of encoder-decoder models.","tags":["transformers","T5"]},
  {"id":"tr-q14","type":"mcq","prompt":"Flash Attention speeds up transformer training/inference by:",
   "choices":["Reducing model parameters","Tiling the attention computation to stay within GPU SRAM — avoids materialising the full N×N attention matrix in HBM, reducing memory IO by ~10×","Approximating attention","Using faster hardware"],
   "answerIndex":1,"explanation":"Bottleneck in attention = HBM (slow) memory reads/writes for N×N matrix. Flash Attention: compute in tiles, keep intermediate values in fast SRAM. Same exact result, ~3× faster.","tags":["transformers","Flash Attention"]},
  {"id":"tr-q15","type":"multi","prompt":"Which are encoder-only transformer models?",
   "choices":["BERT","RoBERTa","GPT-4","DeBERTa"],
   "answerIndexes":[0,1,3],"explanation":"BERT, RoBERTa, DeBERTa are encoder-only (bidirectional, MLM training). GPT-4 is decoder-only (autoregressive). Encoder-only models excel at classification, NER, embeddings.","tags":["transformers","architecture"]},
  {"id":"tr-q16","type":"mcq","prompt":"Scaled dot-product attention divides QK^T by √d_k because:",
   "choices":["Normalization convention","For large d_k, dot products become very large → softmax saturates (gradients ≈ 0). Dividing by √d_k keeps magnitudes stable.","To match output dimension","Required by the loss function"],
   "answerIndex":1,"explanation":"If Q·K are random unit vectors in d_k dimensions, their dot product variance is d_k. Scaling by 1/√d_k normalises variance to 1, preventing softmax from peaking (all attention on one token).","tags":["transformers","attention"]},
  {"id":"tr-q17","type":"mcq","prompt":"Layer Normalisation in transformers is applied:",
   "choices":["Before each batch","After the residual addition (Post-LN) in original paper, or before each sub-layer (Pre-LN) in GPT-style models — Pre-LN more stable for deep networks","Only in BERT","To the embedding layer only"],
   "answerIndex":1,"explanation":"Pre-LN (GPT, LLaMA): normalize inputs to each sub-layer → more training stability for very deep models. Post-LN (original paper) can diverge with very deep models without warm-up.","tags":["transformers","normalization"]},
  {"id":"tr-q18","type":"mcq","prompt":"What does the vocabulary size V affect in transformer models?",
   "choices":["Number of attention heads","Embedding matrix size (V × d_model) and final linear projection (d_model × V) — both are large. V=50K (GPT-2), 128K (Llama 3).","Sequence length","Number of layers"],
   "answerIndex":1,"explanation":"Embedding table: V × d_model params. Output projection: d_model × V. For V=128K, d=4096: 524M params just in these two matrices. Vocabulary design affects memory and tokenization efficiency.","tags":["transformers","vocabulary"]},
  {"id":"tr-q19","type":"mcq","prompt":"Why does increasing transformer depth (layers) improve performance up to a point?",
   "choices":["More layers = faster inference","Deeper networks learn hierarchical representations — lower layers: syntax/local patterns; higher layers: semantics/reasoning. But: vanishing gradients, diminishing returns beyond ~96 layers.","More parameters always help","Depth affects only training speed"],
   "answerIndex":1,"explanation":"Hierarchy: early layers → tokens/syntax, middle → phrase structure, late → semantics/entity types. Very deep models hit diminishing returns and training instability. Width also matters.","tags":["transformers","architecture"]},
  {"id":"tr-q20","type":"mcq","prompt":"Attention 'heads' in multi-head attention are combined by:",
   "choices":["Addition","Concatenation followed by a linear projection — [head1 | head2 | ... | headN] × W_O → d_model","Average pooling","Softmax"],
   "answerIndex":1,"explanation":"MHA: run h heads of d_k=d_model/h each. Concatenate all head outputs → (N × h·d_v). Multiply by W_O (h·d_v × d_model) to project back. Parameter W_O learns to combine head perspectives.","tags":["transformers","attention"]},
],
new_flashcards=[
  {"id":"tr-fc4","front":"Causal masking","back":"Decoder: mask future tokens in attention matrix (set to -inf before softmax). Ensures autoregressive property: each token only attends to itself and previous tokens during training AND inference.","tags":["transformers","attention"]},
  {"id":"tr-fc5","front":"Multi-head attention (MHA)","back":"h parallel attention heads, each d_k=d_model/h. Each learns different relationships. Concatenate → linear project W_O. GPT-3: 96 heads, d_model=12288, d_k=128.","tags":["transformers","attention"]},
  {"id":"tr-fc6","front":"Encoder vs Decoder","back":"Encoder (BERT): bidirectional, MLM training, classification/embeddings. Decoder (GPT): causal, next-token prediction, generation. Encoder-decoder (T5): sequence-to-sequence tasks.","tags":["transformers","architecture"]},
  {"id":"tr-fc7","front":"Flash Attention","back":"Tile-based attention avoiding N×N HBM materialisation. Same math result as standard attention. ~3× speedup, ~10× memory reduction. Required for long-context (>8K) training.","tags":["transformers","Flash Attention"]},
  {"id":"tr-fc8","front":"Scaling laws","back":"Chinchilla (Hoffmann et al.): optimal training: N_params ≈ 20 × training_tokens. 7B model → ~140B tokens optimal. Compute-optimal models outperform over-parameterized undertrained ones.","tags":["transformers","scaling"]},
])

print("\n✅ Step 1 (AI topics) complete")
print("Run: python3 scripts/validate_topics.py to check")

