# Sector-extension transfer and the triangle-containing case

This checkpoint supplies an exact full-core transfer that adds equal-sized sectors with all new incident pair values zero. It is a theorem under the active allowed-graph convention: permitted matrices may be zero. It is not asserted under a requirement that every permitted edge carry positive values.

[The proof](ZERO_SECTOR_TRANSFER.md) shows that every added sector is paid uniformly at every core point, gives the entire extended core, preserves every original player's ideal exactly, and maps the whole first optimal face. For a source target pinned at positive first floor tau, adding sectors from k to K scales its full-leximin payoff by k/K.

Applied to the existing three-sector family, this gives **c(G)=0 for every fixed graph G containing a triangle**. The resulting K-sector family has K(3q+1) players, pair entries in {0,1,2}, integral worth6q+1, positive full-core floor1/[K(q+1)], and target ideal1.

For connected four-vertex allowed graphs:

| Graph | Current result |
|---|---|
| Path P4 | c=1/4 by the all-tree theorem |
| Star K1,3 | c=1/4 by the all-tree theorem |
| Triangle with a pendant vertex (paw) | c=0 by this transfer |
| K4 minus one edge (diamond) | c=0 by this transfer |
| K4 | c=0 by this transfer |
| Four-cycle C4 | 0<=c<=5/44; positive-versus-zero remains open |

The classification of connected four-vertex graphs was exhaustively checked through all64 labeled edge subsets:16 connected trees,19 triangle-containing graphs, and3 labeled four-cycles. The general graph goal remains active, and the four-sector milestone is incomplete until C4 is resolved.

## Replay

Run `bash build.sh` with Python3.10 or later. It checks126,290 exact lifted full-team cover inequalities in seven cases with K=4,5,6 and q=1..4, verifies source certificates, and enumerates the four-vertex graphs. With z3-solver5.1.0.0 installed, `COOPGT_PYTHON=/absolute/path/to/python bash build.sh --smt` adds15 exact raw-core queries. They check both directions of the full-core description, the first-floor upper bound, whole-face target pinning, and ideal bound in three selected cases.

The conventional proof supplies the universal statements; finite checks are corroboration. The copied source generator and source-family proof are unchanged, with hashes recorded in PROVENANCE.json. Generated JSON files are overwritten on replay. The existing source family also has earlier independent audits outside this checkpoint.

## Remaining scope

No subdivision or contraction transfer has been proved. Adding a required sector is not adding dummy players: it changes the productive teams and, in these lifted examples, gives all added players a positive first-floor payoff. No novelty, human specialist approval, purchase or outreach is claimed. See [source status](SOURCE_STATUS.md) and [review disposition](REVIEW_RESPONSE.md).
