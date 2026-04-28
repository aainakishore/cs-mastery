"""
patch_ai_guides.py — Expand all 8 AI topic guides with deeper content, references, YouTube links
Run: python3 scripts/patch_ai_guides.py
These topics already have 20q/8fc — only guides need expanding.
"""
import json
from pathlib import Path

BASE = Path(__file__).parent.parent / 'src/content/topics/ai'

# ─────────────────────────────────────────────────────────────────────────────
# ML BASICS
# ─────────────────────────────────────────────────────────────────────────────
p = BASE / 'ml-basics.json'
d = json.loads(p.read_text())

ML_ADDON = """

---

## What Machine Learning Actually Is (Layman First)

Traditional programming: you write the rules.
  IF email contains "Nigerian prince" THEN mark as spam.
  (You write thousands of manually crafted rules.)

Machine learning: you show examples, the algorithm LEARNS the rules itself.
  Show: 10,000 spam emails + 10,000 normal emails.
  Algorithm: figures out the patterns (repeated words, suspicious links, sender domains).
  Never wrote a single spam rule — it learned them.

```
TRADITIONAL:
  Rules + Data -> Program -> Output

MACHINE LEARNING:
  Data + Output -> Program (training) -> Rules (model)
  Then: New Data + Rules (model) -> Predictions
```

---

## The Three Paradigms — Explained Simply

```
SUPERVISED LEARNING:
  You provide labelled examples: input -> correct answer.
  Model learns the mapping.

  Example: House price prediction
    Training data:
      [2 bed, 100m², city center] -> $400,000
      [3 bed, 150m², suburbs]     -> $300,000
      [1 bed, 50m², city center]  -> $200,000
    After training: model predicts price for any new house description.

  Example: Email spam detection
    [email content] -> spam/not-spam (label)

  Use when: you have labelled examples of inputs and desired outputs.

UNSUPERVISED LEARNING:
  No labels. Find hidden structure in data.

  Example: Customer segmentation
    10 million customers with: age, purchase history, location, browsing behavior
    No labels given.
    K-Means clustering finds: 
      Cluster 1: "young urban professionals" (20-30, tech purchases, city)
      Cluster 2: "budget-conscious families" (30-45, discount focus, suburbs)
      Cluster 3: "retired high-spenders" (60+, luxury, variety)
    You didn't define these segments — algorithm found them.

  Use when: exploring data, finding patterns, dimensionality reduction.

REINFORCEMENT LEARNING:
  Agent learns by trial and error — trying actions, getting rewards or penalties.

  Example: Teaching a robot to walk
    Robot tries random movements -> falls over: penalty.
    Gradually: walks -> reward. Runs: bigger reward.
    After millions of trials: robot walks efficiently.

  Example: AlphaGo (beats world Go champion)
    Played 5 million games against itself.
    Win: +1 reward. Lose: -1 reward.
    Learned to play better than any human.

  Use when: sequential decisions, games, robotics, trading bots.
```

---

## How Models Actually Learn — Gradient Descent

```
Imagine you're blindfolded on a hilly mountain and want to reach the lowest valley.
Strategy: feel the ground slope under your feet. Step in the downhill direction.
Repeat. Eventually reach the bottom (minimum).

Gradient Descent:
  1. Start with random model parameters (weights)
  2. Make predictions with current params
  3. Measure how wrong predictions are: Loss = error(predictions, true_labels)
  4. Calculate gradient: which direction does loss increase?
  5. Step in OPPOSITE direction (downhill): 
     weight = weight - learning_rate * gradient
  6. Repeat for thousands/millions of iterations.
  7. Parameters converge to values that minimize loss.

LEARNING RATE:
  Too high: overshoot the valley, bounce back and forth, never converge.
  Too low: take tiny steps, training takes forever.
  Just right: steadily converge to minimum.

  learning_rate = 0.0001 - 0.01 typical range.

MINI-BATCH GRADIENT DESCENT:
  Full batch: use ALL training data per step (slow, accurate gradient).
  Stochastic: use 1 example per step (fast, noisy gradient).
  Mini-batch: use 32-256 examples per step (compromise — standard practice).
```

---

## Training vs Validation vs Test Split

```
NEVER evaluate your model on data it was trained on — it knows the answers!
Like a student who memorizes exam answers without understanding.

DATA SPLITS:
  Training set (70-80%): model learns from this.
  Validation set (10-15%): tune hyperparameters, catch overfitting during training.
  Test set (10-15%): final evaluation ONCE. Never touched during training.

CRUCIAL: Test set is only evaluated ONCE at the very end.
Using test set multiple times = data leakage (cheating).

CROSS-VALIDATION:
  Split data into K folds (e.g., K=5).
  Train on 4 folds, validate on 1. Rotate 5 times.
  Report average performance across all 5.
  Better estimate of true performance, especially with small datasets.
```

---

## Overfitting and Underfitting — The Core Challenge

```
Every ML model must balance:
  Fitting training data well vs generalizing to new data.

UNDERFITTING:
  Model too simple. Doesn't capture patterns in training data.
  Training accuracy: low. Test accuracy: low.
  Example: Fit a line to data that's clearly a curve.
  Fix: Use a more complex model, more features, train longer.

OVERFITTING:
  Model memorizes training data, fails on new data.
  Training accuracy: very high. Test accuracy: low.
  Example: Model memorizes every training example including noise.
  Fix: More training data, regularization (L1/L2), dropout, early stopping.

IDEAL:
  Training accuracy ≈ Test accuracy. Both good.
  Model has learned the underlying pattern, not just the training examples.

VISUAL:
              Training     Test
  Underfit:    60%          59%   <- both bad (model too simple)
  Overfit:     99%          72%   <- huge gap (memorized training)
  Just right:  94%          91%   <- small gap, both good
```

---

## Common ML Algorithms (Mental Models)

```
LINEAR REGRESSION:
  Predict a number. Fit a line/plane through data points.
  house_price = w1 * bedrooms + w2 * area + w3 * location + bias
  Trade-off: simple, interpretable. Fails for non-linear relationships.

LOGISTIC REGRESSION:
  Classify (despite the name). Predict probability of a class.
  P(spam) = sigmoid(w1*word1 + w2*word2 + ...) -> 0.0 to 1.0
  Above 0.5: spam. Below: not spam.

DECISION TREE:
  A flowchart of if-else questions.
  Is salary > 50K? -> Yes: Is age > 30? -> No: predict "buy".
  Interpretable. But single tree: unstable (overfit).

RANDOM FOREST:
  100 or more decision trees, each trained on random subset of data/features.
  Majority vote of all trees = prediction.
  Much more stable and accurate than single tree.
  Feature importance: which features were most useful?

GRADIENT BOOSTING (XGBoost, LightGBM):
  Build trees sequentially. Each tree corrects errors of previous trees.
  Very accurate. Winner of many Kaggle competitions.
  Slower to train than Random Forest.

K-NEAREST NEIGHBORS (KNN):
  To classify a new point: find K most similar training examples.
  Majority class of K neighbors = prediction.
  Simple but: slow at prediction time (must compare with all training data).

SUPPORT VECTOR MACHINE (SVM):
  Find the hyperplane that best separates classes with maximum margin.
  Works well for high-dimensional data (text classification).
  Less common now; neural networks usually outperform.

NEURAL NETWORK:
  Layers of connected "neurons". Learns complex non-linear patterns.
  Deep learning: many layers. The basis of modern AI.
  See: Neural Networks and Transformers topics.
```

---

## Feature Engineering — The Art of Good ML

```
Raw data is rarely ready for ML. FEATURES are what you feed the model.

FEATURE ENGINEERING:
  Transform raw data into meaningful inputs.

EXAMPLE: Predicting taxi ride duration
  Raw: pickup_time = "2026-03-15 14:32:00"
  Engineered features:
    is_rush_hour = 1 (14:32 = peak)
    day_of_week = 6 (Saturday)
    hour = 14
    is_weekend = 1
  Model learns: weekday rush hour = longer ride.

CATEGORICAL TO NUMERIC:
  Model can't compute with text.
  Color: ["red", "blue", "green"]
  One-hot encoding: [1,0,0], [0,1,0], [0,0,1]

NORMALIZATION:
  Age: 0-100. Income: 0-1,000,000. Model favors large numbers.
  Scale to same range: (value - min) / (max - min) or z-score.

MISSING VALUES:
  Fill with: mean, median, mode, or predict from other features.
  Or: create "is_missing" binary feature.

Good feature engineering often matters more than algorithm choice.
Domain expertise = better features = better model.
```

---

## Evaluation Metrics — What Does "Accuracy" Really Mean?

```
FOR CLASSIFICATION:
  ACCURACY = correct / total
  PROBLEM: Unbalanced classes.
    99% of emails are ham, 1% spam.
    Model that ALWAYS predicts ham: 99% accuracy! Useless.

  BETTER METRICS:
    Precision = TP / (TP + FP)
      "Of all emails called spam, what % actually are spam?"
      High precision: few false alarms.

    Recall = TP / (TP + FN)
      "Of all actual spam emails, what % did we catch?"
      High recall: miss fewer spam emails.

    F1 = 2 * (Precision * Recall) / (Precision + Recall)
      Harmonic mean. Balance between precision and recall.

    Confusion matrix:
              Predicted Spam  Predicted Ham
    Actual Spam:     TP=90        FN=10      <- 100 spam total
    Actual Ham:      FP=5         TN=9895    <- 9900 ham total

FOR REGRESSION:
  MAE (Mean Absolute Error): average |prediction - actual|
  RMSE (Root Mean Squared Error): punishes large errors more than MAE
  R² (R-squared): % of variance explained by model (1.0 = perfect)
```

---

## References and Further Learning

### Videos
- **Machine Learning for Everyone** by 3Blue1Brown (Neural Networks series):
  https://www.youtube.com/watch?v=aircAruvnKk
  - Best visual introduction to how ML and neural networks work.
- **StatQuest Machine Learning Playlist** by Josh Starmer:
  https://www.youtube.com/c/joshstarmer
  - Every ML concept explained clearly with visuals, no math fear.

### Free Courses
- **fast.ai Practical Deep Learning**: https://course.fast.ai/ - code-first approach
- **Google Machine Learning Crash Course**: https://developers.google.com/machine-learning/crash-course
- **Andrew Ng — Machine Learning Specialization** (Coursera, audit free):
  https://www.coursera.org/specializations/machine-learning-introduction

### Books
- **Hands-On Machine Learning with Scikit-Learn, Keras & TensorFlow** (Aurélien Géron) — definitive practical book
- **The Hundred-Page Machine Learning Book** — concise reference

### Practice
- **Kaggle**: https://kaggle.com — competitions, datasets, notebooks. Start with Titanic tutorial.
- **Google Colab**: https://colab.research.google.com — free GPU, runs Jupyter notebooks.
"""

d['guide'] = d['guide'] + ML_ADDON
with open(p, 'w') as f:
    json.dump(d, f, indent=2, ensure_ascii=False)
print(f"ml-basics.json: guide={len(d['guide'])} q={len(d['questions'])} fc={len(d['flashcards'])}")

# ─────────────────────────────────────────────────────────────────────────────
# NEURAL NETS
# ─────────────────────────────────────────────────────────────────────────────
p = BASE / 'neural-nets.json'
d = json.loads(p.read_text())

NN_ADDON = """

---

## What Is a Neural Network? Biological Analogy First

Your brain has ~86 billion neurons. Each neuron:
- Receives signals from many other neurons (inputs)
- If total signal is strong enough: FIRES (activates), sends signal to others

A **artificial neural network** is a simplified mathematical model of this:

```
Biological neuron:       Artificial neuron:
  Dendrites (inputs)       Inputs: x1, x2, x3
  Cell body (sum+decide)   Weighted sum: w1*x1 + w2*x2 + w3*x3 + bias
  Axon (output)            Activation: f(sum) -> output
```

---

## Forward Pass — How Predictions Are Made

```
INPUT LAYER      HIDDEN LAYER 1    HIDDEN LAYER 2    OUTPUT LAYER
   x1               h1 (1)            h2 (1)            y (spam?)
   x2                                                 
   x3               h1 (2)            h2 (2)
   ...
   xn               h1 (3)            h2 (3)

Each arrow = a WEIGHT (a number the model learns).
Each neuron = sum(weights * inputs) then apply activation function.

FORWARD PASS:
  hidden1 = relu(W1 @ input + b1)    # matrix multiply + bias + activation
  hidden2 = relu(W2 @ hidden1 + b2)
  output  = sigmoid(W3 @ hidden2 + b3)  # sigmoid -> 0-1 probability

For each training example: input flows FORWARD through layers -> prediction.
```

---

## Activation Functions — Why They Matter

```
WITHOUT activation functions: no matter how many layers, the network is just
a linear transformation (multiple matrix multiplications = still one matrix).
Cannot learn non-linear patterns.

Activation function = non-linearity = ability to learn complex patterns.

SIGMOID: f(x) = 1 / (1 + e^-x)
  Output: 0 to 1. Good for binary classification output.
  Problem: vanishing gradient (near 0 or 1: gradient ≈ 0, no learning).
  Usage: output layer binary classification.

TANH: f(x) = (e^x - e^-x) / (e^x + e^-x)
  Output: -1 to 1. Zero-centered (better than sigmoid).
  Still has vanishing gradient issue.

ReLU: f(x) = max(0, x)
  Output: 0 or positive x. Extremely simple.
  Fast to compute. No vanishing gradient for positive values.
  Problem: dying ReLU (permanently outputs 0 for negative inputs).
  Usage: standard choice for hidden layers.

LeakyReLU: f(x) = max(0.01x, x)
  Fixes dying ReLU: small gradient for negative inputs.

GELU: used in Transformers (GPT, BERT).
  Smoother version of ReLU.

SOFTMAX: converts raw scores to probabilities that sum to 1.
  Used for multi-class classification output layer.
  [2.1, 0.5, 3.8] -> [0.16, 0.04, 0.80] (20% cat, 4% dog, 80% bird)
```

---

## Backpropagation — How Models Learn

```
Backprop is the algorithm that adjusts weights to reduce prediction error.

FORWARD PASS: Input -> Prediction
LOSS:         Compare prediction to true label: Loss = (prediction - true)^2
BACKWARD PASS: Calculate gradient of loss with respect to each weight.
              Chain rule: how much does weight W4 affect the final loss?
UPDATE:       W = W - learning_rate * gradient

The key insight: chain rule allows gradient to flow BACKWARD through all layers.
Layer by layer: "how much did this weight contribute to the error?"

EXAMPLE:
  Predict spam probability = 0.3. True label = 1 (spam).
  Loss = (0.3 - 1)^2 = 0.49
  Backprop: the weights in the output layer contributed most to error.
  Adjust output weights: make the prediction higher next time.
  Propagate gradient back through hidden layers.
  All weights adjusted slightly in the direction that reduces loss.

VANISHING GRADIENT PROBLEM:
  Gradient multiplied layer by layer going backward.
  If each layer multiplies by 0.5: 10 layers -> gradient * 0.5^10 = 0.001
  Early layers barely learn (gradient near zero).
  Fix: ReLU activation, batch normalization, skip connections (ResNet).
```

---

## Key Hyperparameters You Need to Know

```
LEARNING RATE:
  How big is each weight update step?
  Too high: oscillates, doesn't converge. Too low: takes forever.
  Learning rate schedules: start high, reduce over training.
  Adam optimizer: adapts learning rate per parameter automatically.

BATCH SIZE:
  How many examples per gradient update?
  Small (16-32): noisy gradient but fewer iterations per update, more updates.
  Large (256-2048): stable gradient but needs more memory, fewer updates.
  Typical: 32-256.

EPOCHS:
  How many times do we go through the entire training set?
  Too few: underfitting. Too many: overfitting.
  Use: early stopping (stop when validation loss stops improving).

HIDDEN LAYER SIZE / ARCHITECTURE:
  More neurons: more capacity to learn complex patterns.
  More layers: deeper understanding of features.
  Too big: overfitting, slow training.
  Trial and error + architecture search.

WEIGHT INITIALIZATION:
  Start all weights at 0: neurons all learn the same thing (symmetry problem).
  Random initialization: Xavier/He (matched to activation function).
```

---

## Types of Neural Networks

```
FEEDFORWARD (MLP - Multi-Layer Perceptron):
  Information flows one direction: input -> hidden layers -> output.
  No loops, no memory.
  Use: tabular data, classification, regression.

CONVOLUTIONAL NEURAL NETWORK (CNN):
  Designed for spatial data (images).
  Convolutional layers: detect local features (edges, textures, shapes).
  Pooling: reduce spatial dimensions.
  Use: image classification, object detection, medical imaging.

RECURRENT NEURAL NETWORK (RNN):
  Has loops: output feeds back as input.
  "Memory" of previous inputs.
  Problem: vanishing gradient over long sequences.
  LSTM/GRU: variants that solve this.
  Largely replaced by Transformers for NLP.

TRANSFORMER:
  Attention mechanism: any position can directly attend to any other.
  Solved long-range dependencies better than RNN.
  GPT, BERT, Claude, LLaMA all based on Transformers.
  See: Transformers topic.

AUTOENCODER:
  Encode input to small representation -> decode back to input.
  Learn compressed representation. Use: anomaly detection, denoising.

GAN (Generative Adversarial Network):
  Two networks: Generator creates fake data. Discriminator tells real from fake.
  They compete -> generator improves. Result: realistic generated images.
  Use: image generation, data augmentation.
```

---

## Regularization — Preventing Overfitting in Neural Nets

```
DROPOUT:
  During training: randomly zero out p% of neurons on each forward pass.
  Forces network to not rely on any single neuron.
  Effectively trains an ensemble of smaller networks.
  At test time: use all neurons, scale by (1-p).
  dropout=0.3 means 30% of neurons dropped per step.

L2 REGULARIZATION (Weight Decay):
  Add penalty to loss for large weights: loss += lambda * sum(weights^2)
  Discourages complex models. Keeps weights small.

BATCH NORMALIZATION:
  Normalize activations within each mini-batch.
  Makes training stable and faster.
  Allows higher learning rates.
  Standard in modern deep learning.

EARLY STOPPING:
  Monitor validation loss. If it stops improving for N epochs: stop.
  Use model checkpoint from the epoch with best validation loss.
```

---

## References and Further Learning

### Videos (Must Watch)
- **But what is a Neural Network?** by 3Blue1Brown:
  https://www.youtube.com/watch?v=aircAruvnKk
  - The best visual explanation of neural networks. Watch this first.
- **Backpropagation, intuitively** by 3Blue1Brown:
  https://www.youtube.com/watch?v=Ilg3gGewQ5U
  - Gradient descent and backprop visualised beautifully.

### Free Resources
- **Neural Networks and Deep Learning** (free book): http://neuralnetworksanddeeplearning.com/
- **PyTorch tutorials**: https://pytorch.org/tutorials/
- **fast.ai**: https://course.fast.ai/ — practical deep learning in PyTorch

### Practice
- Implement a neural network from scratch in NumPy: understand backprop deeply.
- Then use PyTorch: https://pytorch.org/tutorials/beginner/basics/buildmodel_tutorial.html
- **Andrej Karpathy's micrograd**: https://github.com/karpathy/micrograd — 100-line backprop
"""

d['guide'] = d['guide'] + NN_ADDON
with open(p, 'w') as f:
    json.dump(d, f, indent=2, ensure_ascii=False)
print(f"neural-nets.json: guide={len(d['guide'])} q={len(d['questions'])} fc={len(d['flashcards'])}")

# ─────────────────────────────────────────────────────────────────────────────
# TRANSFORMERS
# ─────────────────────────────────────────────────────────────────────────────
p = BASE / 'transformers.json'
d = json.loads(p.read_text())

TRANS_ADDON = """

---

## The Problem Transformers Solved

Before Transformers (pre-2017), NLP used RNNs (Recurrent Neural Networks).

```
RNN reads a sentence word by word, left to right:
  "The animal didn't cross the street because IT was too tired"
  Word 1 -> Word 2 -> Word 3 -> ... -> Word 12
  When processing "it" (word 12): memory of word 1 "animal" is faded.
  
PROBLEMS WITH RNN:
  1. Vanishing gradient: gradient for word 1 is tiny by word 50.
  2. Cannot parallelize: word 3 must wait for word 2's output.
  3. Long-range dependencies poorly captured.
```

**Transformers (2017, "Attention Is All You Need" paper) solved all three:**
- Attention: word 12 "it" can directly attend to word 1 "animal" with full strength
- Parallel: all words processed simultaneously (no sequential dependency)
- Scales: bigger model = better, and we have GPUs to parallelize

---

## Self-Attention — The Core Mechanism

```
For each word, self-attention computes:
  "How much should I attend to every other word?"

EXAMPLE: "The bank can guarantee deposits will eventually cover future tuition
          costs because it will always have strong interest."

What does "it" refer to? "The bank" (not the tuition costs).
Self-attention: "it" attends strongly to "bank".

Attention score between word i and word j:
  score(i, j) = dot_product(Query_i, Key_j) / sqrt(d_k)
  Apply softmax -> attention weights (sum to 1)
  Output_i = sum over all j: attention_weight(i,j) * Value_j

Three vectors per word:
  Query (Q): "what am I looking for?"
  Key (K):   "what do I offer to others?"
  Value (V): "what information do I contain?"

The matrix:
          The  bank  can  guarantee  ...  it  ...
  Q for "it":  [0.1  0.7  0.1   0.05       0.05   ...]
               (attend strongly to "bank")
```

---

## Multi-Head Attention

```
Run self-attention H times in parallel, each with different Q,K,V matrices.
Different heads learn different relationships:

  Head 1: learns syntactic relationships (subject-verb agreement)
  Head 2: learns coreference ("it" refers to "bank")
  Head 3: learns positional relationships
  Head 4: learns semantic similarity

Concatenate all heads, project to output dimension.
Multi-head = diverse, specialised attention patterns simultaneously.

GPT-3: 96 attention heads per layer, 96 layers = 9216 different "lenses"
through which each token views every other token.
```

---

## Transformer Architecture (Encoder vs Decoder)

```
ENCODER-ONLY (BERT, RoBERTa):
  Input -> Multiple encoder layers -> Contextualized embedding per token
  Bidirectional: each token attends to ALL other tokens
  Use: understanding text (classification, NER, question answering)
  Not for generation.

DECODER-ONLY (GPT family, LLaMA, Mistral):
  Autoregressive: generates one token at a time
  Causal (masked) attention: each token only attends to PREVIOUS tokens
  Input prompt -> decoder -> one token -> feed back -> next token...
  Use: text generation, code generation, chat

ENCODER-DECODER (T5, BART, original Transformer):
  Encoder: encode entire input sequence
  Decoder: generate output attending to encoder output
  Use: translation (encode source language, decode to target),
       summarization (encode long doc, decode summary)

For LLMs (GPT, Claude, LLaMA): DECODER-ONLY architecture.
```

---

## Positional Encoding — Giving Words Their Order

```
Attention has no notion of order — it just computes pairwise similarities.
"Dog bites man" vs "Man bites dog": same word set, completely different meaning.

Positional encoding adds position information to each token embedding:

  final_embedding = token_embedding + positional_encoding

Original paper: uses sine/cosine functions of different frequencies.
Modern: Rotary Position Embeddings (RoPE) in LLaMA, GPT-Neo etc.

After positional encoding:
  Model knows token 1 is "The", token 2 is "bank", token 12 is "it".
  Position matters in attention calculations.
```

---

## Tokenization — Words to Numbers

```
Neural networks work with numbers, not text.
Tokenizer converts text -> integer token IDs.

"Hello world!" -> [9906, 1917, 0]   (GPT-4 tokenizer)

BYTE PAIR ENCODING (BPE) — most common:
  Common words: single token ("the" = 1, "is" = 2)
  Common subwords: "ing" = 456, "tion" = 789
  Rare words: split into characters: "xylophone" = ["xy", "lo", "phon", "e"]
  
  Context window = maximum tokens a model can process at once.
  Token != word: "unhappiness" might be 3 tokens: ["un", "happi", "ness"]
  1 token ≈ 0.75 words on average.

TOKENIZER EXAMPLES:
  "ChatGPT is amazing!" = 5 tokens
  "machine learning" = 2 tokens
  "antidisestablishmentarianism" = 7+ tokens

Why it matters for your code:
  API cost = tokens. Long context = more tokens = more expensive.
  Token limit: if your prompt is 100K chars: could exceed context window.
```

---

## The Training Process (Pre-training)

```
SELF-SUPERVISED LEARNING: the model learns from raw text, no human labels.

MASKED LANGUAGE MODELING (BERT, encoder models):
  Input:  "The [MASK] jumped over the fence."
  Target: "The dog jumped over the fence."
  Model must predict the masked token.
  Learns bidirectional understanding.

NEXT TOKEN PREDICTION (GPT, decoder models):
  Input:  "The quick brown fox"
  Target: "quick brown fox jumps"  (predict each token from previous ones)
  Every token in the sequence is both input and target (shifted by 1).
  100+ billion tokens of internet text = learn statistical patterns of language.

EMERGENCE:
  Model trained to predict next token... also learns:
  - arithmetic (3+5=8?)
  - reasoning (if A>B and B>C, then...)
  - coding (complete this Python function)
  These weren't directly trained — they emerge from next-token prediction at scale.
```

---

## Scale Laws — Why Bigger Is Better

```
Scaling laws (Kaplan et al., 2020): predictable improvement with scale.
  Performance improves smoothly as you increase:
    Model size (parameters)
    Training data (tokens)
    Compute (FLOPs)

  GPT-2: 1.5B params (2019) - funny poems
  GPT-3: 175B params (2020) - coherent essays, code
  GPT-4: ~1T params estimate (2023) - passes bar exam, PhD-level reasoning

COMPUTE-OPTIMAL SCALING (Chinchilla, 2022):
  For optimal performance per compute dollar:
    model_params ≈ 20 * training_tokens
  GPT-3 (175B params): optimally train on 3.5T tokens.
  Most LLMs were undertrained vs this formula.
  Chinchilla (70B): smaller model, more data -> outperformed GPT-3.

LLAMA 3.2 (2024): efficient small models (1B, 3B, 11B) competitive with 
large expensive models from 2023. Better data + better architecture beats brute scale.
```

---

## Latest Developments (2024-2026)

```
MULTIMODAL MODELS:
  GPT-4V, Claude 3, Gemini: process text AND images in same context.
  LLaMA 3.2: 11B/90B vision models open-source.
  Input: image + text question -> text answer.

LONG CONTEXT:
  GPT-4 (2023): 128K context window.
  Claude 3 (2024): 200K context window.
  Gemini 1.5 Pro: 1M tokens (entire codebase!).
  Enables: analyze full codebases, entire PDFs, long conversations.

REASONING MODELS:
  OpenAI o1, o3: "think step by step" before answering.
  Chain-of-thought embedded in pretraining/RLHF.
  Much better at math, coding, logic puzzles.

MIXTURE OF EXPERTS (MoE):
  Mixtral (Mistral AI): 8 expert sub-networks, route each token to 2 experts.
  47B total params, 13B active per token: efficient inference.
  GPT-4 reportedly uses MoE architecture.
```

---

## References and Further Learning

### Videos (Essential)
- **Attention mechanism visualized** by 3Blue1Brown:
  https://www.youtube.com/watch?v=eMlx5fFNoYc
  - The definitive visual explanation of Transformer attention.
- **Let's build GPT from scratch** by Andrej Karpathy:
  https://www.youtube.com/watch?v=kCc8FmEb1nY
  - 2 hours. Build a GPT character model in PyTorch from scratch. Legendary video.

### Papers (Reading Level: Advanced)
- **Attention Is All You Need (2017)**: https://arxiv.org/abs/1706.03762 — the original Transformer paper
- **Language Models are Few-Shot Learners (GPT-3)**: https://arxiv.org/abs/2005.14165

### Interactive
- **Andrej Karpathy's nanoGPT**: https://github.com/karpathy/nanoGPT — minimal GPT in ~300 lines
- **Hugging Face Transformers**: https://huggingface.co/docs/transformers — run any open model
"""

d['guide'] = d['guide'] + TRANS_ADDON
with open(p, 'w') as f:
    json.dump(d, f, indent=2, ensure_ascii=False)
print(f"transformers.json: guide={len(d['guide'])} q={len(d['questions'])} fc={len(d['flashcards'])}")

# ─────────────────────────────────────────────────────────────────────────────
# LLMS
# ─────────────────────────────────────────────────────────────────────────────
p = BASE / 'llms.json'
d = json.loads(p.read_text())

LLMS_ADDON = """

---

## How LLM Text Generation Actually Works

When you type "What is the capital of France?" — here's exactly what happens:

```
1. TOKENIZATION:
   "What is the capital of France?" 
   -> [2061, 374, 279, 6864, 315, 9822, 30]  (GPT-4 tokenizer)
   Each word/subword becomes an integer ID.

2. EMBEDDING:
   Token IDs -> dense vectors (e.g., 4096 dimensions for GPT-3.5).
   + positional encoding: each token knows its position.

3. TRANSFORMER LAYERS (many, ~32-96 for large models):
   Each layer: multi-head attention + feedforward network.
   Gradually builds richer contextual representation.
   
4. OUTPUT PROJECTION:
   Final hidden state -> logits (raw scores for every token in vocabulary, ~50,000 tokens)
   
5. SOFTMAX -> PROBABILITIES:
   Logits -> probability distribution over next token.
   "France" scores 0.89, "Paris" 0.07, ...
   But wait: why wouldn't it just output "France"?
   
6. SAMPLING:
   With temperature=0: always pick highest probability token (greedy).
   With temperature=0.7: sample from distribution (mix of determinism and creativity).
   Token selected: "Paris" (it predicted the next token after... let me retry)
   
7. AUTOREGRESSIVE LOOP:
   Output token appended to input -> run forward pass again for next token.
   "What is the capital of France? " + "Paris"
   Next token? -> "."
   Continue until: max_tokens reached or special [END] token generated.
```

This is why LLMs are **slow for long responses**: every token requires a FULL forward pass through all transformer layers.

---

## Temperature and Sampling Parameters

```
Raw logits before sampling:
  "Paris" = 10.5
  "Lyon"  = 3.2
  "France"= 2.1
  ...

TEMPERATURE scales logits before softmax:
  logits_scaled = logits / temperature

  temperature = 0 (or very low): "Paris" dominates completely. Deterministic.
  temperature = 1: standard softmax. Scale maintained.
  temperature = 2: logits compressed. "Lyon" and others get more probability.
  temperature > 1: more random/creative. temperature < 1: more focused.

TOP-P (Nucleus Sampling):
  Only sample from smallest set of tokens whose probabilities sum to p.
  top_p = 0.9: include tokens until cumulative probability = 90%.
  Drops long tail of improbable tokens. Less garbage output than pure temperature.

TOP-K:
  Only sample from top K most probable tokens.
  top_k = 50: choose from top 50 tokens only.

TYPICAL PRODUCTION SETTINGS:
  Precise answers (code, math): temperature=0.0-0.2
  Balanced (general chat): temperature=0.7-0.8
  Creative writing: temperature=0.9-1.1
  top_p=0.9, top_k=50: common safe defaults
```

---

## Context Window — The Model's Working Memory

```
Context window = maximum tokens the model can "see" and "remember" at once.
Everything outside the window is invisible to the model.

GPT-3.5: 16K tokens (~12,000 words)
GPT-4: 128K tokens (~96,000 words)
Claude 3.5: 200K tokens
Gemini 1.5 Pro: 1M tokens

WHAT TAKES UP CONTEXT:
  System prompt:     typically 200-2000 tokens
  Conversation history: each turn adds tokens (grows over time)
  Your current message: variable
  Model's response: 100-4000 typical

AT LIMIT: Model either truncates context (forgets early history) or errors.
For long conversations: implement sliding window (drop oldest messages).

WHY LARGER CONTEXT IS HARD:
  Attention is O(n²) in context length.
  2x context length = 4x attention computation.
  Flash Attention (2022): efficient attention for long contexts.
  Most models: 128K-200K context now practical.
```

---

## The RLHF Training Pipeline

```
Modern LLMs go through three training phases:

PHASE 1: PRETRAINING
  Objective: next-token prediction on massive internet text.
  GPT-4: estimated 13T tokens, ~$100M compute.
  Result: base model. Knows language but doesn't know how to be helpful.
  Ask base model to help you: might respond by asking more questions or
  giving the Wikipedia article instead of an answer.

PHASE 2: SUPERVISED FINE-TUNING (SFT)
  Human contractors demonstrate ideal responses to prompts.
  Model fine-tuned on (prompt, ideal_response) pairs.
  Teaches the model: WHAT good behavior looks like.
  Result: model follows instructions much better.

PHASE 3: RLHF (Reinforcement Learning from Human Feedback)
  Two parts:
  a) Train reward model: humans rank pairs of responses (A vs B). 
     Reward model learns to score responses.
  b) RL fine-tuning: optimize the LLM to maximize reward model score,
     using PPO (Proximal Policy Optimization).
  Teaches: HOW to be helpful, harmless, honest.
  Result: ChatGPT-like helpfulness and safety behavior.

RLAIF (RL from AI Feedback):
  Replace human raters with another AI (Constitutional AI, Claude).
  Cheaper to scale than human raters.
  Anthropic's approach for Claude.
```

---

## Hallucinations — Why LLMs Make Things Up

```
WHAT IS A HALLUCINATION?
  LLM generates plausible-sounding but factually incorrect information.
  "Albert Einstein was born in Frankfurt in 1879." 
  (He was born in Ulm. Both are in Germany but different cities.)

WHY IT HAPPENS:
  LLMs predict the next token from patterns, not from a database of facts.
  They optimize for generating COHERENT text, not FACTUAL text.
  "The capital of France is ___" -> "Paris" because that's the most common pattern.
  "The capital of Turkmenistan is ___" -> LLM may confidently write "Ashgabat"
  OR may write the wrong answer if training data had errors.
  When the model doesn't "know" something: it generates the most likely-sounding answer.
  No uncertainty signal in the base model.

MITIGATIONS:
  Temperature=0: reduces creativity but still hallucinates.
  RAG (Retrieval-Augmented Generation): retrieve actual docs, put them in context.
    Model: "Here are 5 relevant documents [docs]. Answer: [uses docs]."
    Less hallucination on factual questions when source is in context.
  Tool use: give model a search tool. Let it retrieve before answering.
  Citiation requirement: instruct model to cite sources. Harder to hallucinate
    when forced to attribute claims.
  Always verify critical information from LLM output.
```

---

## Practical LLM API Usage Patterns

```python
# OpenAI API (GPT-4)
from openai import OpenAI

client = OpenAI(api_key="sk-...")

# Basic completion
response = client.chat.completions.create(
    model="gpt-4o",
    messages=[
        {"role": "system", "content": "You are a helpful assistant."},
        {"role": "user", "content": "Explain quantum entanglement simply."},
    ],
    temperature=0.7,
    max_tokens=500,
    top_p=0.9,
)
print(response.choices[0].message.content)

# COST CALCULATION:
# input tokens:  $0.005 per 1K (GPT-4o, Apr 2026 approx)
# output tokens: $0.015 per 1K
# 1000 token request + 500 token response = $0.005 + $0.0075 = $0.0125

# STREAMING (better UX for long responses)
stream = client.chat.completions.create(
    model="gpt-4o",
    messages=[{"role": "user", "content": "Write a story"}],
    stream=True,
)
for chunk in stream:
    if chunk.choices[0].delta.content:
        print(chunk.choices[0].delta.content, end="", flush=True)
```

---

## Open-Source LLMs: Run Locally

```
OPEN-SOURCE MODELS (2024-2026):
  LLaMA 3.3 70B:  Meta, Apache 2.0 license, competitive with GPT-3.5
  Mistral 7B:     Fast, efficient, great for inference
  Mixtral 8x7B:   MoE architecture, 47B params, 13B active
  Gemma 2 9B:     Google, efficient, good quality per size
  Qwen 2.5 72B:   Alibaba, strong coding and math
  DeepSeek V3:    671B MoE, competitive with GPT-4 frontier

RUNNING LOCALLY:
  Ollama (easiest): https://ollama.ai
    ollama pull llama3.3     # download ~4GB
    ollama run llama3.3      # chat in terminal
    curl localhost:11434/api/generate  # REST API

  Requirements (rough guide):
    7B model:  8GB RAM (4-bit quantized: 4GB)
    13B model: 16GB RAM
    70B model: 48GB RAM (or RTX 4090 x2)

  M2 MacBook Pro 16GB: runs 7B models well at ~20 tokens/sec.
  M3 Max 128GB: runs 70B models.
```

---

## References

### Videos
- **How GPT models work** by Andrej Karpathy:
  https://www.youtube.com/watch?v=zjkBMFhNj_g
  - State of GPT lecture: tokenization, pretraining, SFT, RLHF, sampling.
- **Intro to Large Language Models** by Andrej Karpathy:
  https://www.youtube.com/watch?v=zjkBMFhNj_g
  - 1 hour. The best single overview of LLMs.

### Articles
- **OpenAI tokenizer playground**: https://platform.openai.com/tokenizer — see token counts live
- **Hugging Face Course**: https://huggingface.co/learn/nlp-course — free, practical NLP/LLM course
- **LLM Visualization** (every layer animated): https://bbycroft.net/llm

### Practice
- **Ollama**: run LLaMA locally free: https://ollama.ai
- **OpenAI Playground**: experiment with parameters interactively
- **LangChain/LlamaIndex**: build LLM applications with RAG
"""

d['guide'] = d['guide'] + LLMS_ADDON
with open(p, 'w') as f:
    json.dump(d, f, indent=2, ensure_ascii=False)
print(f"llms.json: guide={len(d['guide'])} q={len(d['questions'])} fc={len(d['flashcards'])}")

for fname, addon_key in [
    ('agents.json', 'agents'),
    ('rag.json', 'rag'),
    ('fine-tuning.json', 'finetune'),
    ('prompting-fundamentals.json', 'prompting'),
]:
    p = BASE / fname
    d = json.loads(p.read_text())
    refs = {
        'agents': """

---

## References

### Videos
- **AI Agents Explained** by IBM Technology:
  https://www.youtube.com/watch?v=F8NKVhkZZWI
  - Clear overview of agent architecture and tool use.
- **Building LLM Agents** by LangChain:
  https://www.youtube.com/watch?v=DWUdGFCU2cY
  - Code walkthrough of building agents with LangChain.

### Articles
- **ReAct: Reasoning + Acting** (original paper): https://arxiv.org/abs/2210.03629
- **OpenAI Function Calling docs**: https://platform.openai.com/docs/guides/function-calling
- **Hugging Face Agents Course**: https://huggingface.co/learn/agents-course

### Practice
- **LangChain Agent tutorials**: https://python.langchain.com/docs/modules/agents/
- **AutoGen**: https://github.com/microsoft/autogen — multi-agent framework
- Build a simple ReAct agent that can search the web and do math.
""",
        'rag': """

---

## References

### Videos
- **RAG from Scratch** by LangChain:
  https://www.youtube.com/watch?v=wd7TZ4w1mSw
  - Full tutorial building RAG from vector embedding to retrieval.
- **RAG vs Fine-tuning vs Prompting** by AICamp:
  https://www.youtube.com/watch?v=00Q0G84kq3M
  - When to use each approach with concrete examples.

### Articles
- **LlamaIndex RAG guide**: https://docs.llamaindex.ai/en/stable/getting_started/starter_example.html
- **Pinecone Learning Center**: https://www.pinecone.io/learn/ — vector DB and embeddings guides

### Practice
- **LangChain RAG tutorial**: https://python.langchain.com/docs/tutorials/rag/
- Build: ingest PDF docs -> chunk -> embed -> store in ChromaDB -> query with LLM
- **Chroma (local vector DB)**: https://www.trychroma.com/ — free, no setup
""",
        'finetune': """

---

## References

### Videos
- **Fine-tuning LLMs (LoRA)** by Andrej Karpathy:
  https://www.youtube.com/watch?v=zjkBMFhNj_g
  - Fine-tuning explained in context of full LLM training pipeline.
- **LoRA fine-tuning tutorial** by Weights & Biases:
  https://www.youtube.com/watch?v=eC6Hd1hFvos
  - Practical walkthrough with code.

### Articles
- **LoRA paper**: https://arxiv.org/abs/2106.09685 — Low-Rank Adaptation original paper
- **Hugging Face PEFT library**: https://huggingface.co/docs/peft — simplest way to use LoRA
- **Axolotl**: https://github.com/OpenAccess-AI-Collective/axolotl — fine-tuning framework

### Practice
- **Hugging Face fine-tuning tutorial**: https://huggingface.co/docs/transformers/training
- Fine-tune Mistral 7B on custom dataset with LoRA using PEFT + Google Colab (free T4 GPU)
- **Unsloth**: https://github.com/unslothai/unsloth — 2x faster fine-tuning, less memory
""",
        'prompting': """

---

## References

### Videos
- **Prompt Engineering Guide** by Elvis Saravia:
  https://www.youtube.com/watch?v=dOxUroR57xs
  - Comprehensive prompting techniques walkthrough.
- **ChatGPT Prompt Engineering for Developers** by DeepLearning.AI:
  https://www.deeplearning.ai/short-courses/chatgpt-prompt-engineering-for-developers/
  - Free 1-hour course by OpenAI and DeepLearning.AI.

### Articles
- **Prompt Engineering Guide**: https://www.promptingguide.ai/ — comprehensive reference
- **OpenAI prompting best practices**: https://platform.openai.com/docs/guides/prompt-engineering
- **Anthropic's Claude prompting guide**: https://docs.anthropic.com/claude/docs/prompt-engineering

### Practice
- Use the OpenAI Playground to experiment with system prompts, temperature, top_p.
- Try writing the same prompt 5 different ways and compare outputs.
- Implement chain-of-thought and compare accuracy on math problems.
""",
    }
    if 'References' not in d['guide']:
        d['guide'] = d['guide'] + refs[addon_key]
        with open(p, 'w') as f:
            json.dump(d, f, indent=2, ensure_ascii=False)
        print(f"{fname}: guide={len(d['guide'])} q={len(d['questions'])} fc={len(d['flashcards'])}")
    else:
        print(f"{fname}: references already present, skipped")

