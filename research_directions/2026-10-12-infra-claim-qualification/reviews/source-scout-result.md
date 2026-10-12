The proposed benchmark is a good fit for the failure pattern in the supplied report: it separates semantic support, contradiction, and abstention from minimal-span exact match. The documentation packet must be frozen locally by release tag or commit and hashed before claims are authored.

## Six candidate sections and 18 claims

Evidence IDs below refer to passages to include in the frozen packet.

### 1. Kubernetes — GPU scheduling

Primary section: [Schedule GPUs](https://kubernetes.io/docs/tasks/manage-gpus/scheduling-gpus/), last-modified upstream commit shown as `8f2d5571cc`.

Evidence:

- **K1:** GPU resources are exposed through device plugins as custom schedulable resources.
- **K2:** GPU limits may appear without requests; Kubernetes uses the limit as the request.
- **K3:** If both are specified, requests and limits must be equal; requests alone are not permitted.
- **K4:** Node labels/selectors can target different GPU types.

Claims, scoped only to this section:

1. **Supported:** “A pod may specify a GPU limit without a separate GPU request; Kubernetes then uses the limit as the request.” Evidence: K2.
2. **Contradicted:** “Kubernetes permits a pod to specify a GPU request without specifying a GPU limit.” Evidence: K3 explicitly says it cannot.
3. **Insufficient:** “The maximum number of pods allowed to share one physical GPU is four.” Missing: the section gives neither a sharing limit nor a physical-GPU multiplexing policy.

License: Kubernetes website content is [CC BY 4.0](https://github.com/kubernetes/website/blob/main/LICENSE). Retain attribution and the license notice.

### 2. PyTorch — CUDA memory accounting

Primary section: [CUDA semantics: Memory management](https://docs.pytorch.org/docs/stable/notes/cuda.html#memory-management). Freeze the chosen PyTorch release rather than the mutable `stable` alias.

Evidence:

- **P1:** `memory_allocated()` measures memory occupied by tensors.
- **P2:** `memory_reserved()` measures total memory managed by the caching allocator.
- **P3:** Unused allocator-managed memory can still appear used in `nvidia-smi`.
- **P4:** `empty_cache()` releases unused cached memory but does not free memory occupied by tensors.

Claims:

4. **Supported:** “Within PyTorch’s CUDA allocator accounting, reserved memory can exceed tensor-occupied memory.” Evidence: P1–P3.
5. **Contradicted:** “Calling `empty_cache()` frees GPU memory still occupied by live tensors.” Evidence: P4 says it does not.
6. **Insufficient:** “Creating a CUDA context consumes exactly 512 MiB on every supported GPU.” Missing: no fixed context-overhead amount or hardware-independent value appears in the section.

License: PyTorch’s repository license permits redistribution and modification under BSD-style conditions ([license terms](https://github.com/pytorch/pytorch/blob/main/LICENSE)). Verify that the selected documentation snapshot carries the same repository-wide license; I did not independently verify a per-page documentation notice.

### 3. vLLM — automatic prefix caching

Primary section: [Automatic Prefix Caching](https://docs.vllm.ai/en/latest/design/prefix_caching/). Replace `latest` with the selected release or source commit in the packet.

Evidence:

- **V1:** vLLM reuses KV-cache blocks when a later request has the same prefix.
- **V2:** Block hashes incorporate the parent hash, exact block tokens, and relevant extra hashes.
- **V3:** Only full blocks are cached.
- **V4:** Optional cache salts restrict reuse to requests sharing the salt.

Claims:

7. **Supported:** “A block’s cache identity depends on both its own tokens and preceding-prefix state.” Evidence: V2.
8. **Contradicted:** “Automatic prefix caching stores and reuses partially filled blocks.” Evidence: V3 explicitly limits caching to full blocks.
9. **Insufficient:** “Under a 70% cache-hit rate, prefix caching reduces median time-to-first-token by exactly 35%.” Missing: the design section supplies no workload, hardware, latency measurements, or such quantitative relationship.

License: vLLM is distributed under [Apache License 2.0](https://github.com/vllm-project/vllm/blob/main/LICENSE). Preserve required notices.

### 4. Ray — fractional accelerator sharing

Primary section: [Accelerator Support: Fractional Accelerators](https://docs.ray.io/en/latest/ray-core/scheduling/accelerators.html#fractional-accelerators), rendered as Ray 2.59.0 when inspected. Freeze the `ray-2.59.0` source snapshot rather than `latest`.

Evidence:

- **R1:** Fractional requirements allow multiple tasks or actors to share an accelerator.
- **R2:** Four `num_gpus=0.25` tasks can execute concurrently on one NVIDIA GPU.
- **R3:** Users are responsible for keeping tasks within their accelerator-memory share.
- **R4:** Ray packs fractional assignments onto one accelerator before moving to another to reduce fragmentation.
- **R5:** Ray’s assignment can be bypassed; it does not itself prevent code from using other accelerators.

Claims:

10. **Supported:** “Ray normally packs fractional accelerator assignments onto an accelerator before assigning the next accelerator.” Evidence: R4.
11. **Contradicted:** “A fractional Ray GPU reservation automatically enforces the corresponding fraction of GPU memory.” Evidence: R3 and R5 place enforcement responsibility on the application/user.
12. **Insufficient:** “Two actors each requesting 0.5 GPU achieve the same combined throughput as one actor requesting a full GPU.” Missing: no model, workload, throughput measurement, or performance equivalence is supplied.

License: Ray’s documentation repository is covered by [Apache License 2.0](https://github.com/ray-project/ray/blob/master/LICENSE), subject to its bundled third-party notices.

### 5. Slurm — power saving and node resume

Primary section: [Slurm Power Saving Guide](https://slurm.schedmd.com/power_save.html). The live URL is mutable; freeze the corresponding file from a selected Slurm release and record its hash.

Evidence:

- **S1:** With automatic power saving enabled, nodes idle for `SuspendTime` are suspended through `SuspendProgram`.
- **S2:** Nodes needed for allocated work are resumed through `ResumeProgram`.
- **S3:** A resumed node that fails to register within `ResumeTimeout` becomes `DOWN`, and its allocated jobs are requeued.
- **S4:** Enabling automatic power saving requires specified programs, timeouts, and rates.

Claims:

13. **Supported:** “Under automatic power saving, failure to register a resumed node within `ResumeTimeout` causes the node to become `DOWN` and its allocated jobs to be requeued.” Evidence: S3.
14. **Contradicted:** “Automatic Slurm power saving requires no suspend or resume program configuration.” Evidence: S4 requires both programs or named `PowerAction` equivalents.
15. **Insufficient:** “Suspending an idle node saves 420 watts on the benchmark cluster.” Missing: the guide contains no cluster-specific power draw or measured energy savings.

License caveat: Slurm says its code **and documentation** are under [GPL v2 or later](https://github.com/SchedMD/slurm/blob/master/COPYING). This is redistributable but copyleft, not permissive in the usual legal classification. If “permissive” is a strict eligibility requirement, exclude Slurm; no permissively licensed substitute with equally direct scheduler sleep/resume semantics was verified in this bounded scout.

### 6. vLLM — OpenAI-compatible serving

Primary, version-pinned section: [vLLM 0.21.0 OpenAI-Compatible Server](https://docs.vllm.ai/en/v0.21.0/serving/openai_compatible_server/).

Evidence:

- **O1:** The server implements Completions, Chat Completions, and additional APIs.
- **O2:** Chat Completions applies only to text-generation models with a chat template.
- **O3:** The Completions `suffix` parameter is unsupported.
- **O4:** The Chat Completions `user` parameter is ignored.
- **O5:** A model repository’s `generation_config.json` can override default sampling values unless `--generation-config vllm` is used.

Claims:

16. **Supported:** “By default, a model repository’s `generation_config.json` may override some server sampling defaults.” Evidence: O5.
17. **Contradicted:** “vLLM 0.21.0 supports the `suffix` parameter on `/v1/completions`.” Evidence: O3 explicitly says it is unsupported.
18. **Insufficient:** “The server sustains 500 requests per second for an 8B model on one H100.” Missing: the section specifies interfaces, not that hardware/workload configuration or any measured throughput.

License: same vLLM [Apache-2.0 license](https://github.com/vllm-project/vllm/blob/main/LICENSE).

## Strongest cheap workflow

Use an authored qualification fixture, not a performance experiment:

1. Freeze the six source files and licenses by commit/release; store SHA-256 hashes.
2. Assign paragraph-level evidence IDs before writing claims.
3. Have one author construct balanced triples and an independent reviewer adjudicate them without model outputs.
4. Require exact JSON: `verdict ∈ {supported, contradicted, insufficient}` and a sorted list of evidence IDs; require an empty evidence list for insufficient, plus a separately scored missing-information field.
5. Score verdict and evidence selection separately. Permit multiple predeclared minimal evidence sets so factual but slightly broader citations do not recreate the earlier exact-span artifact.
6. Keep qualification accuracy separate from subsequent measured latency, throughput, energy, or economics.

This fixture establishes documentation-grounding qualification only. It is not measured evidence of cost savings, energy reduction, serving efficiency, production reliability, or economic value.

## Claims not to make

Do not claim that:

- the benchmark is novel, representative of all AI-infrastructure work, uncontaminated, or predictive of production performance;
- prefix caching, fractional GPUs, or node suspension improves efficiency by any unmeasured amount;
- documentation support proves an operation will succeed on a real cluster;
- API compatibility is complete OpenAI behavioral compatibility;
- logical GPU reservations enforce memory or security isolation;
- authored qualification cases constitute economic, latency, throughput, or energy evidence;
- passing 18 cases establishes general reliability;
- this proposal changes or supersedes the frozen 8/12 result.

## Concrete report-review defects

- [REPORT.txt:24](</Users/maxf/.local/state/cross-model/coopgpt-46e183e1e9e1/20261011-220927-9a02eb93/workspace/research_directions/2026-10-11-mac-grounded-qa/REPORT.txt:24>) shows that two factual answers failed because of span breadth. A new benchmark would repeat this defect if evidence IDs have only one exact gold set. Verify candidate scoring against all independently accepted minimal evidence sets.
- [REPORT.txt:29](</Users/maxf/.local/state/cross-model/coopgpt-46e183e1e9e1/20261011-220927-9a02eb93/workspace/research_directions/2026-10-11-mac-grounded-qa/REPORT.txt:29>) documents two abstention failures, one involving intent versus achieved outcome. Exclude such pragmatic ambiguity and verify every insufficient item by explicitly listing the absent field.
- [REPORT.txt:79](</Users/maxf/.local/state/cross-model/coopgpt-46e183e1e9e1/20261011-220927-9a02eb93/workspace/research_directions/2026-10-11-mac-grounded-qa/REPORT.txt:79>) recommends an application-specific correctness contract but does not define evidence-selection scoring or contradiction handling. Verify the new schema and adjudication rules before inspecting any model output.
- [REPORT.txt:42](</Users/maxf/.local/state/cross-model/coopgpt-46e183e1e9e1/20261011-220927-9a02eb93/workspace/research_directions/2026-10-11-mac-grounded-qa/REPORT.txt:42>) contains `original11434`, apparently a missing separator. Check the underlying readiness log before correcting it; it likely means “original endpoint on port 11434.”

Limitations: I verified the live primary pages and repository license texts, but did not create immutable packet snapshots or verify exact source commits for PyTorch, Ray, Slurm, and vLLM’s prefix-caching page. Slurm’s GPL license also fails a strict “permissive license” requirement. No files were modified and no model, training, cluster, or serving execution was performed.