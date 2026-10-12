"""Author-selected infrastructure review fixtures; no model outputs used."""
from pathlib import Path
import hashlib,html,json,re
BASE=Path(__file__).resolve().parent

def excerpt(source,start,end,identifier,strip_html=False):
    text=(BASE/source).read_text();a=text.index(start);b=text.index(end,a)+len(end)
    raw=text[a:b];shown=raw
    if strip_html:shown=html.unescape(re.sub(r'<[^>]*>',' ',raw));shown=' '.join(shown.split())
    return dict(id=identifier,text=shown,source_file=source,source_char_start=a,source_char_end=b,source_text_sha256=hashlib.sha256(raw.encode()).hexdigest(),transformation='strip_html_and_collapse_whitespace' if strip_html else 'verbatim')

def main():
    packets={}
    def packet(key,specs):
        source=next(x['source_file'] for x in json.loads((BASE/'SOURCE_MANIFEST.json').read_text()) if x['id']==key)
        packets[key]=[excerpt(source,a,b,'D'+str(i+1),key=='slurm_gres') for i,(a,b) in enumerate(specs)]
    packet('kubernetes',[
      ('As an administrator, you have to install GPU drivers','GPU vendor. Here are some links to vendors\' instructions:'),
      ('GPUs are only supposed to be specified','* You cannot specify GPU `requests` without specifying `limits`.'),
      ('If different nodes in your cluster have different types of GPUs','to schedule pods to appropriate nodes.'),
      ('That label key `accelerator` is just an example','a different label key if you prefer.')])
    packet('vllm_apc',[
      ('Automatic Prefix Caching (APC in short)','allowing the new query to skip the computation of the shared part.'),
      ('Set `enable_prefix_caching=True`','Here is an example:'),
      ('APC in general does not reduce the performance of vLLM.','(so that the computation cannot be reused).'),
      ('Under `--mamba-cache-mode align`','- the model does not use multi-module MTP')])
    packet('torch_memory',[
      ('PyTorch uses a caching memory allocator','managed by the caching allocator.'),
      ('Calling {meth}`~torch.cuda.empty_cache`','so it can not increase the amount of GPU memory available for PyTorch.'),
      ('For more advanced users, we offer','underlying allocation patterns produced by your code.'),
      ('Use of a caching allocator can interfere','`PYTORCH_NO_CUDA_MEMORY_CACHING=1` in your environment to disable caching.')])
    packet('ray_resources',[
      ('Ray resources are *logical*','Ray mainly uses logical resources for admission control during scheduling.'),
      ("- Resource requirements of tasks or actors don't limit actual physical resource usage.",'their resource requirements specify.'),
      ('- Ray does provide {ref}`GPU <gpu-support>` isolation','which most machine learning frameworks respect for GPU assignment.'),
      ('You cannot dynamically update the resource capacities','after Ray starts on that node.')])
    packet('slurm_gres',[
      ('<p>Requests for typed vs non-typed generic resources','a GPU of the same type to create a job step.</p>'),
      ('<P>Jobs will be allocated specific generic resources','for use by other jobs.</P>'),
      ('<P>All of these options are supported','<I>sbatch --gres=gpu:kepler:2 ...</I>.</P>'),
      ('<P>Job steps can be allocated generic resources','A simple example is shown below.</P>')])
    packet('vllm_sleep',[
      ('Level 1 sleep will offload the model weights','Please make sure there\'s enough CPU memory to store the model weights.'),
      ('Level 2 sleep will discard both','`collective_rpc("reload_weights")`.'),
      ('During RLHF training, vLLM allows you','**Note** that `is_sleeping` will report `true` until all components are awake.'),
      ('Set `sleep_preserve_parameter_names`','This option does not filter updates.')])
    cases=[]
    def add(source,claim,label,proofs,relevant,why,kind):
        identifier=hashlib.sha256(('coop-infra-20261012:'+source+':'+claim).encode()).hexdigest()[:20]
        cases.append(dict(request_id=identifier,source_id=source,passages=packets[source],claim=claim,label=label,acceptable_evidence=proofs,relevant_evidence=relevant,rationale=why,reasoning=kind,max_output_tokens=256))
    add('kubernetes','For our proposed container, after the vendor driver and device plugin are installed, a GPU limit can be specified without an explicit GPU request; Kubernetes uses that limit as the request.', 'supported',[['D2']],['D1','D2'],'The setup is a stated premise; D2 suffices for the conclusion. D1 corroborates that premise context.','conditional')
    add('kubernetes','For a cluster with different GPU types, node labels and selectors can steer a Pod to suitable nodes, and the label key does not have to be accelerator.', 'supported',[['D3','D4']],['D3','D4'],'D3 gives routing mechanism and D4 says accelerator is an example rather than mandatory key.','conditional')
    add('kubernetes','For the custom GPU resource described here, setting the request to one GPU and the limit to two GPUs is permitted.', 'contradicted',[['D2']],['D2'],'D2 explicitly requires equal values when both are supplied.','direct')
    add('kubernetes','The described GPU device plugin allows a container to request half of a physical GPU through its custom resource field.', 'insufficient',[],[],'The packet gives equality/default rules but no fractional GPU granularity or device-sharing policy. Neither fractional permission nor prohibition is established.','missing_information')
    add('vllm_apc','For a request that shares an existing prefix, the documented APC benefit targets prompt processing rather than generation of new tokens.', 'supported',[['D3']],['D1','D3'],'Shared prefix is a premise; D3 explicitly confines the benefit to prefill, not decode. D1 corroborates the mechanism.','conditional')
    add('vllm_apc','Enabling APC lets a request with no prefix in common with existing queries reuse their prefix computations.', 'contradicted',[['D3']],['D1','D3'],'D3 explicitly rules out reuse when new queries share no prefix; D1 is relevant corroboration.','conditional')
    add('vllm_apc','For the hybrid Mamba option described here, enabling the shared-prefix checkpoint flag is sufficient even when the model uses multi-module MTP.', 'contradicted',[['D4']],['D4'],'D4 gives conjunctive prerequisites including that model does not use multi-module MTP.','conditional')
    add('vllm_apc','APC keeps its cached prefix blocks available after a full server process restart.', 'insufficient',[],[],'The packet does not specify persistence across process restart. Neither survival nor loss of cached blocks is established.','missing_information')
    add('torch_memory','The documented allocated-memory functions track tensors, whereas the reserved-memory functions track the total memory managed by the caching allocator.', 'supported',[['D1']],['D1','D2'],'D1 distinguishes these accounting concepts; D2 corroborates the tensor/cache distinction.','direct')
    add('torch_memory','Calling empty_cache while tensors are still live releases the GPU memory occupied by those tensors for another process.', 'contradicted',[['D2']],['D1','D2'],'D2 explicitly says occupied tensor memory is not freed; D1 gives the accounting context.','conditional')
    add('torch_memory','The described PyTorch caching allocator uses first-fit selection to choose an available memory block.', 'insufficient',[],[],'The packet describes accounting, memory release and debugging, but not the free-block selection algorithm. First-fit is neither established nor explicitly rejected.','missing_information')
    add('torch_memory','Disabling CUDA memory caching makes our training job finish faster than leaving caching enabled.', 'insufficient',[],[],'D4 recommends disabling for a debugging use, not measured end-to-end speed of this job. D1 says the allocator accelerates allocation but does not establish whole-job runtime in either configuration.','missing_information')
    add('ray_resources','Starting a head node with zero logical CPUs can prevent CPU-requiring work from being scheduled there even when the machine has physical CPUs.', 'supported',[['D1']],['D1'],'D1 provides this exact admission-control example and scope.','conditional')
    add('ray_resources','Ray provides visible-device GPU isolation by setting CUDA_VISIBLE_DEVICES, which most machine-learning frameworks respect for assignment.', 'supported',[['D3']],['D3'],'D3 explicitly documents visible-device isolation and its framework qualification.','direct')
    add('ray_resources','Our proposed Ray task declaring num_cpus=1 is prevented by Ray from launching threads that use multiple physical CPUs.', 'contradicted',[['D2']],['D1','D2'],'D2 explicitly denies physical-usage enforcement; D1 explains logical resources.','conditional')
    add('ray_resources','Ray can move a running GPU actor to another node without restarting that actor.', 'insufficient',[],[],'The packet describes admission control and resource assignment but says nothing about migration of a running actor or its restart semantics.','missing_information')
    add('slurm_gres','For our proposed typed-GPU allocation, the job step should request GPUs of that same type.', 'supported',[['D1']],['D1','D3','D4'],'D1 requires same type across allocation and step; D3 defines type and D4 corroborates allocation-to-step scope.','conditional')
    add('slurm_gres','Suspending a job makes its allocated generic resources available for other jobs to use.', 'contradicted',[['D2']],['D2'],'D2 explicitly states suspension does not release those resources to other jobs.','direct')
    add('slurm_gres','A submission using the --gpus option will be accepted even when select/cons_tres is not configured.', 'contradicted',[['D3']],['D3'],'D3 explicitly states these --gpu* requests are rejected without select/cons_tres.','conditional')
    add('slurm_gres','Our cluster has enough free GPUs of type tesla to start a two-GPU job right now.', 'insufficient',[],[],'Syntax/type examples do not specify cluster inventory, allocation occupancy or real-time availability.','missing_information')
    add('vllm_sleep','After waking only the model weights with tags=["weights"], is_sleeping can remain true until the remaining components are awake.', 'supported',[['D3']],['D3'],'D3 describes selective wake and explicitly says is_sleeping remains true until all components awake.','conditional')
    add('vllm_sleep','In our proposed pause-and-resume workflow, level 1 sleep retains the existing KV-cache contents so requests resume with that unchanged cache.', 'contradicted',[['D1']],['D1','D4'],'D1 states the KV cache is discarded and its content forgotten; D4 explicitly says level-1 behavior is unchanged.','direct')
    add('vllm_sleep','The level-1 CPU backup of model weights is compressed before being stored in host memory.', 'insufficient',[],[],'The packet establishes that level-1 weights are backed up in CPU memory but does not specify compression or its absence.','missing_information')
    add('vllm_sleep','Our current serving engine will finish waking from sleep in under five hundred milliseconds.', 'insufficient',[],[],'No measured or guaranteed latency for this deployment is present. It is not ruled out either.','missing_information')
    cases.sort(key=lambda c:hashlib.sha256(('order:'+c['request_id']).encode()).hexdigest())
    (BASE/'packets.json').write_text(json.dumps(packets,indent=2,sort_keys=True)+'\n')
    (BASE/'cases.json').write_text(json.dumps(cases,indent=2,sort_keys=True)+'\n')
    blind=[{k:j[k] for k in ('request_id','source_id','passages','claim')} for j in cases]
    (BASE/'BLIND_CASES.json').write_text(json.dumps(blind,indent=2,sort_keys=True)+'\n')
    print('Constructed',len(cases),'prospective cases across',len(packets),'source sections.')
if __name__=='__main__':main()
