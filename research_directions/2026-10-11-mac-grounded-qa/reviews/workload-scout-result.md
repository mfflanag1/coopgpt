Recommendation: run one bounded SQuAD 2.0 calibration on the cached `qwen3:32b`, retaining the prior KEEP extraction only as a secondary capability diagnostic.

### Recommended workload: SQuAD 2.0 extractive QA

Why it fits:

- Official Stanford dataset: answerable questions require extracting a passage span; unanswerable questions require abstention. This resembles document/support retrieval more closely than synthetic record copying.
- Public development set is only **4 MB**; training is 40 MB. It is distributed under **CC BY-SA 4.0**. Stanford also provides the official evaluation procedure. [Official dataset, downloads, license, and task description](https://rajpurkar.github.io/SQuAD-explorer/)
- It supports natural request-length variation through passage and question length. Freeze length strata before inference rather than padding or adding demonstrations.
- Scoring can be fully mechanical: fixed JSON such as `{"answer":"..."}` or `{"answer":null}`, schema validation, then the official normalized exact-match score against all reference answers. Preserve token-overlap F1 only as a diagnostic; do not silently substitute it for the qualification gate.

Limitations:

- SQuAD passages are Wikipedia, not private support documents, and its questions were crowd-generated. It measures grounded reading and abstention, not end-to-end customer value.
- SQuAD 2.0 is old and widely published. Its public dev examples may have appeared in model training, so this is a local engineering qualification—not clean held-out generalization or an accuracy estimate for production traffic.
- Context lengths are mixed but relatively bounded by the dataset’s paragraph template. They do not represent long-document RAG, multi-turn support, or tool use.
- “Exact” normalization can accept differences in case, punctuation, articles, and whitespace. Freeze the official normalization implementation and additionally require schema-valid single-field output.

### Deterministic baseline

Freeze a small, hash-identified dev subset before seeing outputs, stratified by:

- answerable versus unanswerable;
- measured prompt-token bins;
- preferably distinct articles across development and confirmation.

Use `temperature: 0`, `seed: 0`, `think: false`, a fixed context window and output cap, and no retries. Record the exact Ollama/model manifests. The dataset, prompt, schema, and scorer can be deterministic; model execution is only best-effort reproducible across runtime or hardware changes and should not be described as mathematically deterministic.

Use the existing fresh KEEP generator as the second and final option: rerun a fresh, disjoint copy with `qwen3:32b` solely to answer “can this stack reliably filter and copy structured records?” Its strict ordering and whole-array exactness are valuable regression checks, but failures can overstate practical harm, while successes say little about document-QA value. It should not supply the useful-work denominator for an economic or pooling claim.

### Qwen3/Ollama request

Ollama’s chat API defines `think: false` as requesting no thinking output and accepts either `"json"` or a JSON Schema in `format`; its documentation recommends schema validation and lower temperature for more deterministic structured output. Check `/api/show` first because thinking controls are model-specific. [Ollama chat API](https://docs.ollama.com/api/chat), [thinking controls](https://docs.ollama.com/capabilities/thinking), [structured outputs](https://docs.ollama.com/capabilities/structured-outputs)

```json
{
  "model": "qwen3:32b",
  "messages": [
    {
      "role": "user",
      "content": "/no_think\nReturn the answer span from the passage, or null if unsupported."
    }
  ],
  "think": false,
  "stream": false,
  "format": {
    "type": "object",
    "properties": {
      "answer": { "type": ["string", "null"] }
    },
    "required": ["answer"],
    "additionalProperties": false
  },
  "options": {
    "temperature": 0,
    "seed": 0
  }
}
```

Qwen’s official documentation independently identifies `/no_think` as its prompt-level soft switch and `enable_thinking=False` as the chat-template hard switch. The latter is framework-specific; for Ollama, use its documented top-level `think:false`, with `/no_think` as explicit prompt redundancy rather than pretending `chat_template_kwargs` is an Ollama field. [Qwen3 thinking/non-thinking documentation](https://qwen.readthedocs.io/en/stable/inference/transformers.html)

### Evidence defects/gaps

- [PROTOCOL.txt:41](/Users/maxf/.local/state/cross-model/coopgpt-46e183e1e9e1/20261011-202115-01bbb845/workspace/research_directions/2026-10-11-mac-quality-calibration/PROTOCOL.txt:41) makes array order part of correctness. [REPORT.txt:23](/Users/maxf/.local/state/cross-model/coopgpt-46e183e1e9e1/20261011-202115-01bbb845/workspace/research_directions/2026-10-11-mac-quality-calibration/REPORT.txt:23) documents a semantically correct set rejected only for order. That is valid for protocol conformance but unsuitable as the sole economically relevant metric. Verification: prospectively report separate semantic-set and serialization-contract scores without rescoring the old gate.
- [REPORT.txt:53](/Users/maxf/.local/state/cross-model/coopgpt-46e183e1e9e1/20261011-202115-01bbb845/workspace/research_directions/2026-10-11-mac-quality-calibration/REPORT.txt:53) notes that context accounting may omit cached/template tokens. Verification: tokenize the fully rendered Qwen chat template with the exact model tokenizer and compare it against Ollama’s reported prompt counts before freezing length bins.
- The supplied protocol has no Qwen3 thinking-mode control because it pinned Llama. Verification for the next run: save `/api/show`, assert that `false` is supported, and retain responses proving the reasoning field is empty.

Decisive next step: freeze a modest, length-stratified SQuAD 2.0 dev subset and qualification threshold, then run it once on cached `qwen3:32b` in non-thinking structured-output mode. Do not start energy or pooling measurements until that gate passes.