I now have primary-source inspections for all candidates; nothing further to request. Note: this session exposes no file-write tool, so I could not create `handoff/RESERVE_DATA_SOURCE_DELEGATE.txt`; result is returned inline only (not simulated).

## Result: three candidates (all official pages inspected)

### 1. ORNL/OLCF Summit "Long Term Per-Component Power and Thermal Measurements" — best AI/HPC-GPU fit
- Official: https://doi.ccs.ornl.gov/dataset/086578e9-8a9f-56b1-a657-0ed8b7393deb (DOI 10.13139/OLCF/1861393); schema/companion README: https://github.com/at-aaims/summit_power_and_thermal_data
- Measured vs derived: README states values come from "out-of-band telemetry streams pushed… at a 1Hz data rate" from node BMCs (OpenBMC). Published files are **10‑s and 1‑min means of those 1 Hz sensor readings** (1 Hz raw is OLCF-internal). So: physically measured, time-averaged — not estimated/synthetic.
- Schema (parquet, Snappy): `timestamp`, `hostname`, `node_state`; node PSU input power `ps0_input_power`, `ps1_input_power` (W); CPU `p0_power`, `p1_power` (W); GPU `p0_gpu0..2_power`, `p1_gpu0..2_power` (W); GPU/CPU temps (°C). `hostname` encodes column/row/rack-slot → separately identified units, simultaneous timestamps.
- Coverage: Jan 2020, Aug 2020, Feb 2021, Aug 2021, Jan 2022 (five month-long windows); 4,626 hosts in the full-node snapshot.
- Sizes: full 10‑s set 492 GB; 1‑min set 120 GB; samples: `b_snapshot_10sec_24h.tar` 1.1 GB, `c_snapshot_1min_24h.tar` 1.9 GB, `a_fullperiod_10sec_100hosts.tar` 4.2 GB, `d_snapshot_1min_4626hosts_24h` 4.1 GB.
- Access: open download via ORNL Constellation (Globus link on DOI page); README says CC BY 4.0; **DOI page itself lists no license** (discrepancy to confirm). Acknowledgement text requested.
- Ownership limitation: single operator (DOE/OLCF). No tenant/job mapping in this package → any owner partition is **synthetic** under gate §4. AI-workload applicability: V100 GPU system, but workload mix not labeled; do not claim "AI data-center" load without further evidence.

### 2. CINECA M100 ExaData (Marconi100) — second GPU-cluster option, schema partly unverified
- Official: Zenodo records, e.g. dataset 1 https://zenodo.org/records/7588815 (CC BY 4.0, open); 12 monthly/bimonthly records + aggregated https://doi.org/10.5281/zenodo.7541722; repo https://gitlab.com/ecs-lab/exadata; paper open text https://pmc.ncbi.nlm.nih.gov/articles/PMC10193329/
- Measured vs derived: paper's `ipmi` plugin "collects all the sensor data provided by the OOB management interface (BMC)" (104 metrics); `logics` plugin collects room-level power consumption; stated aim "preserving original information 'as is'". Zenodo description lists "CPU power consumption" per node. **Exact power column names and W units were not confirmed** in the pages I inspected (the repo `documentation/` folder was not fetched).
- Interval: 20 s implied (paper: "reduced the sampling rate… from 20 seconds to 10 minutes"); not stated per plugin. Timestamps truncated to 1 s.
- Coverage 2020‑03‑09 to 2022‑09‑28; 980+ nodes; partitioned parquet `year_month/plugin/metric`. Monthly tars 210.8 MB (20‑04) to 7.6 GB.
- Ownership: single operator; job table exists but owner fields anonymized → synthetic partition only. Related PM100 (zenodo 10127767) is **job-level derived power — excluded** as not a raw simultaneous trace.

### 3. Low Carbon London smart-meter data — non-AI, clearly labeled model-method test only
- Official: https://data.london.gov.uk/dataset/smartmeter-energy-use-data-in-london-households (UK Power Networks; CC BY 4.0)
- Measured vs derived: smart-meter half-hourly **energy (kWh per half hour)**, i.e., metered interval energy; average kW = ×2 (derived conversion). 5,567 households with unique IDs, Nov 2011–Feb 2014, 30‑min interval. Files: single CSV zip 764.5 MB (~10 GB, ~167 M rows) or 168-file split 758.9 MB; 2013 ToU tariff file.
- Page does not list column headers (LCLid/DateTime/KWH-hh names are my inference, unverified). Households are genuinely separate owners, but residential demand ≠ AI load and no "firm capacity"/headroom semantics exist; use only to test the Gaussian-factor/tail/S‑G machinery.

### Not selected
- MIT SuperCloud v1 (https://dcc.mit.edu/data/, `s3://mit-supercloud-dataset/datacenter-challenge/202201/`, `--no-sign-request`, ~2 TB): has nvidia-smi GPU power (W) at 100 ms **per job**, not node-wide simultaneous; join to nodes required; no node/PSU power; v2 (Oct 2026) needs a DUA. Rejected for bounded intake.
- UCI ElectricityLoadDiagrams (370 clients, 15‑min kW, CC BY 4.0): weak provenance on meter origin; omitted.

### One best bounded intake candidate
ORNL Summit sample **`a_fullperiod_10sec_100hosts.tar` (4.2 GB)** — 100 separately identified hosts across all five months at 10 s, W units, measured BMC provenance; gives enough tail observations. If 4.2 GB exceeds the "no large download" bound, fall back to `b_snapshot_10sec_24h.tar` (1.1 GB), accepting that 24 h is too short for target-α tail assessment. (I did not download anything.)

### What remains missing
- No public dataset found with **real multi-owner** simultaneous AI/data-center power; all GPU-cluster traces are single-operator, so owner mapping stays synthetic.
- Summit: license on DOI page; whether sample hosts are randomly chosen (README says yes, selection rule not given); sample download instructions marked "TBD".
- M100: ipmi power metric names/units/interval must be read from the repo documentation or a small parquet partition before use.
- No evidence on firm capacity entitlements, curtailment rules, or sponsor valuation in any source — these remain modeling assumptions.
- Handoff file not written (no write tool in this session).

Sources: [ORNL dataset DOI page](https://doi.ccs.ornl.gov/dataset/086578e9-8a9f-56b1-a657-0ed8b7393deb), [Summit README](https://github.com/at-aaims/summit_power_and_thermal_data), [M100 Zenodo dataset 1](https://zenodo.org/records/7588815), [M100 paper (PMC)](https://pmc.ncbi.nlm.nih.gov/articles/PMC10193329/), [ExaData repo](https://gitlab.com/ecs-lab/exadata), [Low Carbon London](https://data.london.gov.uk/dataset/smartmeter-energy-use-data-in-london-households), [MIT DCC data page](https://dcc.mit.edu/data/), [MIT SuperCloud GitHub](https://github.com/MIT-AI-Accelerator/MIT-Supercloud-Dataset), [UCI ElectricityLoadDiagrams](https://archive.ics.uci.edu/dataset/321/electricityloaddiagrams20112014)
