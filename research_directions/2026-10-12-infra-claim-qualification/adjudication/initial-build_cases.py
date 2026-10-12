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
      ('Level-2 sleep backs up selected GPU parameters','This option does not filter updates.')])
    cases=[]
    def add(source,claim,label,proofs,relevant,why,kind):
        identifier=hashlib.sha256(('coop-infra-20261012:'+source+':'+claim).encode()).hexdigest()[:20]
        cases.append(dict(request_id=identifier,source_id=source,passages=packets[source],claim=claim,label=label,acceptable_evidence=proofs,relevant_evidence=relevant,rationale=why,reasoning=kind,max_output_tokens=256))
    add('kubernetes','After the vendor driver and device plugin are installed, a container can specify a GPU limit without an explicit GPU request; Kubernetes uses that limit as the request.', 'supported',[['D1','D2']],['D1','D2'],'D1 states vendor setup prerequisites; D2 explicitly permits limit-only resources and supplies request default.','conditional')
    add('kubernetes','For a cluster with different GPU types, node labels and selectors can steer a Pod to suitable nodes, and the label key does not have to be accelerator.', 'supported',[['D3','D4']],['D3','D4'],'D3 gives routing mechanism and D4 says accelerator is an example rather than mandatory key.','conditional')
    add('kubernetes','For the custom GPU resource described here, setting the request to one GPU and the limit to two GPUs is permitted.', 'contradicted',[['D2']],['D2'],'D2 explicitly requires equal values when both are supplied.','direct')
    add('kubernetes','Our production node gpu-west-02 already has the required vendor driver and device plugin installed.', 'insufficient',[],[],'Packet specifies required setup, but contains no observed state of gpu-west-02. Neither installed nor absent is established.','missing_deployment_state')
    add('vllm_apc','When a request shares an existing prefix, APC can reuse that shared computation while leaving the new-token decoding phase without the APC speedup.', 'supported',[['D1','D3']],['D1','D3'],'D1 establishes shared-prefix reuse; D3 confines benefit to prefill, not decode.','conditional')
    add('vllm_apc','Enabling APC lets a request with no prefix in common with existing queries reuse their prefix computations.', 'contradicted',[['D3']],['D1','D3'],'D3 explicitly rules out reuse when new queries share no prefix; D1 is relevant corroboration.','conditional')
    add('vllm_apc','For the hybrid Mamba option described here, enabling the shared-prefix checkpoint flag is sufficient even when the model uses multi-module MTP.', 'contradicted',[['D4']],['D4'],'D4 gives conjunctive prerequisites including that model does not use multi-module MTP.','conditional')
    add('vllm_apc','APC reduced our production service energy per successful request by fifteen percent last week.', 'insufficient',[],[],'Packet describes mechanism and limits, not measured energy or last-week deployment outcomes. It establishes neither this reduction nor its negation.','missing_measurement')
    add('torch_memory','The documented allocated-memory functions track tensors, whereas the reserved-memory functions track the total memory managed by the caching allocator.', 'supported',[['D1']],['D1'],'D1 distinguishes these two accounting concepts explicitly.','direct')
    add('torch_memory','Calling empty_cache while tensors are still live releases the GPU memory occupied by those tensors for another process.', 'contradicted',[['D2']],['D1','D2'],'D2 explicitly says occupied tensor memory is not freed; D1 gives the accounting context.','conditional')
    add('torch_memory','Worker Cedar currently has twelve GiB reserved by the PyTorch caching allocator.', 'insufficient',[],[],'No live worker measurements are supplied. Accounting APIs do not reveal an actual reading.','missing_deployment_state')
    add('torch_memory','Disabling CUDA memory caching makes our training job finish faster than leaving caching enabled.', 'insufficient',[],[],'D4 recommends disabling for a debugging use, not measured end-to-end speed of this job. D1 says the allocator accelerates allocation but does not establish whole-job runtime in either configuration.','missing_measurement')
    add('ray_resources','Starting a head node with zero logical CPUs can prevent CPU-requiring work from being scheduled there even when the machine has physical CPUs.', 'supported',[['D1']],['D1'],'D1 provides this exact admission-control example and scope.','conditional')
    add('ray_resources','Ray provides visible-device GPU isolation by setting CUDA_VISIBLE_DEVICES, which most machine-learning frameworks respect for assignment.', 'supported',[['D3']],['D3'],'D3 explicitly documents visible-device isolation and its framework qualification.','direct')
    add('ray_resources','A Ray task declaring num_cpus=1 is prevented by Ray from launching threads that use multiple physical CPUs.', 'contradicted',[['D2']],['D1','D2'],'D2 explicitly denies physical-usage enforcement; D1 explains logical resources.','conditional')
    add('ray_resources','The GPU assigned to our next Ray actor will be physical device number three.', 'insufficient',[],[],'Visible-device isolation is documented, but this actor allocation and physical device numbering are not supplied.','missing_deployment_state')
    add('slurm_gres','An allocation requested with a typed GPU should use that same GPU type when requesting GPUs for its job step.', 'supported',[['D1']],['D1'],'D1 requires typed/untyped consistency and same type across allocation and step.','conditional')
    add('slurm_gres','Suspending a job makes its allocated generic resources available for other jobs to use.', 'contradicted',[['D2']],['D2'],'D2 explicitly states suspension does not release those resources to other jobs.','direct')
    add('slurm_gres','A submission using the --gpus option will be accepted even when select/cons_tres is not configured.', 'contradicted',[['D3']],['D3'],'D3 explicitly states these --gpu* requests are rejected without select/cons_tres.','conditional')
    add('slurm_gres','Our cluster has enough free GPUs of type tesla to start a two-GPU job right now.', 'insufficient',[],[],'Syntax/type examples do not specify cluster inventory, allocation occupancy or real-time availability.','missing_deployment_state')
    add('vllm_sleep','After waking only the model weights with tags=["weights"], is_sleeping can remain true until the remaining components are awake.', 'supported',[['D3']],['D3'],'D3 describes selective wake and explicitly says is_sleeping remains true until all components awake.','conditional')
    add('vllm_sleep','Level 1 sleep retains the existing KV-cache contents so requests can resume with that unchanged cache.', 'contradicted',[['D1']],['D1'],'D1 states the KV cache is discarded and its content forgotten.','direct')
    add('vllm_sleep','Our serving host has enough available CPU RAM to back up the model weights during level 1 sleep.', 'insufficient',[],[],'D1 requires enough CPU memory, but neither actual free host RAM nor model-weight size is supplied.','missing_deployment_state')
    add('vllm_sleep','Our current serving engine will finish waking from sleep in under five hundred milliseconds.', 'insufficient',[],[],'No measured or guaranteed latency for this deployment is present. It is not ruled out either.','missing_measurement')
    cases.sort(key=lambda c:hashlib.sha256(('order:'+c['request_id']).encode()).hexdigest())
    (BASE/'packets.json').write_text(json.dumps(packets,indent=2,sort_keys=True)+'\n')
    (BASE/'cases.json').write_text(json.dumps(cases,indent=2,sort_keys=True)+'\n')
    blind=[{k:j[k] for k in ('request_id','source_id','passages','claim')} for j in cases]
    (BASE/'BLIND_CASES.json').write_text(json.dumps(blind,indent=2,sort_keys=True)+'\n')
    print('Constructed',len(cases),'prospective cases across',len(packets),'source sections.')
if __name__=='__main__':main()
