// Exhaustive census of the relevant six-player eta-dual vertices.
//
// After deleting the dominated columns lambda_S and lambda_{i}, i in S,
// adjoining the fixed column 1_S to an eta-dual vertex gives a minimal
// balanced collection containing S.  Conversely, normalize any such
// collection so the coefficient of S is one; its remaining coefficients,
// with target singletons interpreted as floor variables, give an eta-dual
// vertex.  A minimal balanced collection on six players has at most six
// coalitions, so direct support enumeration is finite and inexpensive in C++.

#include <algorithm>
#include <array>
#include <cstdint>
#include <cstdlib>
#include <fstream>
#include <iostream>
#include <map>
#include <numeric>
#include <set>
#include <sstream>
#include <string>
#include <utility>
#include <vector>

namespace {

constexpr int N = 6;
using Support = std::vector<int>;
using Weights = std::vector<long long>;

long long determinant(std::vector<std::vector<long long>> a) {
  const int n = static_cast<int>(a.size());
  if (n == 0) return 1;
  long long sign = 1;
  long long previous = 1;
  for (int pivot = 0; pivot + 1 < n; ++pivot) {
    int swap = pivot;
    while (swap < n && a[swap][pivot] == 0) ++swap;
    if (swap == n) return 0;
    if (swap != pivot) {
      std::swap(a[swap], a[pivot]);
      sign = -sign;
    }
    const long long value = a[pivot][pivot];
    for (int row = pivot + 1; row < n; ++row) {
      for (int column = pivot + 1; column < n; ++column) {
        const long long numerator =
            a[row][column] * value - a[row][pivot] * a[pivot][column];
        if (numerator % previous != 0) std::abort();
        a[row][column] = numerator / previous;
      }
      a[row][pivot] = 0;
    }
    previous = value;
  }
  return sign * a[n - 1][n - 1];
}

void row_subsets(int need, int next, std::vector<int>* current,
                 std::vector<std::vector<int>>* result) {
  if (static_cast<int>(current->size()) == need) {
    result->push_back(*current);
    return;
  }
  for (int row = next; row < N - 1; ++row) {
    current->push_back(row);
    row_subsets(need, row + 1, current, result);
    current->pop_back();
  }
}

bool balancing_weights(const Support& support, Weights* answer,
                       long long* degree) {
  const int k = static_cast<int>(support.size());
  if (k < 2 || k > N) return false;
  std::array<std::array<int, N>, N - 1> differences{};
  for (int row = 0; row < N - 1; ++row) {
    for (int column = 0; column < k; ++column) {
      const int mask = support[column];
      differences[row][column] = ((mask >> (row + 1)) & 1) - (mask & 1);
    }
  }

  std::vector<std::vector<int>> subsets;
  std::vector<int> current;
  row_subsets(k - 1, 0, &current, &subsets);
  for (const auto& rows : subsets) {
    Weights kernel(k, 0);
    bool nonzero = false;
    for (int omitted = 0; omitted < k; ++omitted) {
      std::vector<std::vector<long long>> square(
          k - 1, std::vector<long long>(k - 1));
      for (int i = 0; i < k - 1; ++i) {
        int out = 0;
        for (int column = 0; column < k; ++column) {
          if (column == omitted) continue;
          square[i][out++] = differences[rows[i]][column];
        }
      }
      kernel[omitted] = (omitted % 2 ? -1 : 1) * determinant(square);
      nonzero = nonzero || kernel[omitted] != 0;
    }
    if (!nonzero) continue;
    if (kernel[0] < 0) {
      for (auto& value : kernel) value = -value;
    }
    if (!std::all_of(kernel.begin(), kernel.end(),
                     [](long long value) { return value > 0; })) {
      continue;
    }
    bool valid = true;
    for (int row = 0; row < N - 1 && valid; ++row) {
      long long total = 0;
      for (int column = 0; column < k; ++column)
        total += differences[row][column] * kernel[column];
      valid = total == 0;
    }
    if (!valid) continue;
    long long divisor = 0;
    for (long long value : kernel) divisor = std::gcd(divisor, value);
    for (auto& value : kernel) value /= divisor;
    long long common = 0;
    for (int column = 0; column < k; ++column)
      if (support[column] & 1) common += kernel[column];
    if (common <= 0) std::abort();
    *answer = std::move(kernel);
    *degree = common;
    return true;
  }
  return false;
}

std::vector<std::array<int, N>> group_permutations(int s_size) {
  std::vector<int> inside(s_size), outside(N - s_size);
  std::iota(inside.begin(), inside.end(), 0);
  std::iota(outside.begin(), outside.end(), s_size);
  std::vector<std::array<int, N>> result;
  do {
    do {
      std::array<int, N> permutation{};
      for (int i = 0; i < s_size; ++i) permutation[i] = inside[i];
      for (int i = s_size; i < N; ++i)
        permutation[i] = outside[i - s_size];
      result.push_back(permutation);
    } while (std::next_permutation(outside.begin(), outside.end()));
    std::iota(outside.begin(), outside.end(), s_size);
  } while (std::next_permutation(inside.begin(), inside.end()));
  return result;
}

int permute_mask(int mask, const std::array<int, N>& permutation) {
  int result = 0;
  for (int old = 0; old < N; ++old)
    if ((mask >> old) & 1) result |= 1 << permutation[old];
  return result;
}

std::string encode(const Support& support, const Weights& weights,
                   const std::array<int, N>& permutation) {
  std::vector<std::pair<int, long long>> terms;
  for (size_t i = 0; i < support.size(); ++i)
    terms.push_back({permute_mask(support[i], permutation), weights[i]});
  std::sort(terms.begin(), terms.end());
  std::ostringstream out;
  for (const auto& [mask, weight] : terms) out << mask << ':' << weight << ',';
  return out.str();
}

std::string canonical_key(const Support& support, const Weights& weights,
                          const std::vector<std::array<int, N>>& group) {
  std::string best;
  bool first = true;
  for (const auto& permutation : group) {
    std::string key = encode(support, weights, permutation);
    if (first || key < best) {
      first = false;
      best = std::move(key);
    }
  }
  return best;
}

std::pair<Support, Weights> decode(const std::string& key) {
  Support support;
  Weights weights;
  size_t start = 0;
  while (start < key.size()) {
    size_t colon = key.find(':', start);
    size_t comma = key.find(',', colon);
    support.push_back(std::stoi(key.substr(start, colon - start)));
    weights.push_back(std::stoll(key.substr(colon + 1, comma - colon - 1)));
    start = comma + 1;
  }
  return {support, weights};
}

std::string fraction(long long numerator, long long denominator) {
  long long divisor = std::gcd(std::llabs(numerator), std::llabs(denominator));
  numerator /= divisor;
  denominator /= divisor;
  if (denominator == 1) return std::to_string(numerator);
  return std::to_string(numerator) + "/" + std::to_string(denominator);
}

struct Census {
  int s_size;
  long long supports_checked = 0;
  long long raw_collections = 0;
  std::map<int, long long> raw_by_size;
  std::set<std::string> orbits;
};

void visit_support(const Support& support, int target, Census* census,
                   const std::vector<std::array<int, N>>& group) {
  ++census->supports_checked;
  int covered = 0;
  for (int coalition : support) covered |= coalition;
  if (covered != (1 << N) - 1) return;
  Weights weights;
  long long degree = 0;
  if (!balancing_weights(support, &weights, &degree)) return;
  auto position = std::find(support.begin(), support.end(), target);
  if (position == support.end()) std::abort();
  ++census->raw_collections;
  ++census->raw_by_size[static_cast<int>(support.size())];
  census->orbits.insert(canonical_key(support, weights, group));
}

void enumerate_combinations(const std::vector<int>& candidates, int need,
                            int next, int target, Support* support,
                            Census* census,
                            const std::vector<std::array<int, N>>& group) {
  if (need == 0) {
    visit_support(*support, target, census, group);
    return;
  }
  const int last = static_cast<int>(candidates.size()) - need;
  for (int index = next; index <= last; ++index) {
    support->push_back(candidates[index]);
    enumerate_combinations(candidates, need - 1, index + 1, target, support,
                           census, group);
    support->pop_back();
  }
}

Census run_census(int s_size) {
  Census census{};
  census.s_size = s_size;
  const int target = (1 << s_size) - 1;
  std::vector<int> candidates;
  for (int coalition = 1; coalition < (1 << N) - 1; ++coalition)
    if (coalition != target) candidates.push_back(coalition);
  const auto group = group_permutations(s_size);
  for (int size = 2; size <= N; ++size) {
    Support support{target};
    enumerate_combinations(candidates, size - 1, 0, target, &support, &census,
                           group);
    std::cerr << "S=" << s_size << " size=" << size
              << " checked=" << census.supports_checked
              << " raw=" << census.raw_collections
              << " orbits=" << census.orbits.size() << '\n';
  }
  return census;
}

void emit_census(std::ostream& out, const Census& census) {
  const int target = (1 << census.s_size) - 1;
  out << "{\n"
      << "  \"S_size\": " << census.s_size << ",\n"
      << "  \"P_size\": " << N - census.s_size << ",\n"
      << "  \"supports_checked\": " << census.supports_checked << ",\n"
      << "  \"raw_minimal_balanced_collections\": "
      << census.raw_collections << ",\n"
      << "  \"orbit_count\": " << census.orbits.size() << ",\n"
      << "  \"raw_count_by_support_size\": {";
  bool first = true;
  for (const auto& [size, count] : census.raw_by_size) {
    if (!first) out << ',';
    first = false;
    out << "\n    \"" << size << "\": " << count;
  }
  out << "\n  },\n  \"orbits\": [\n";
  int orbit_index = 0;
  for (const auto& key : census.orbits) {
    auto [support, weights] = decode(key);
    auto target_position = std::find(support.begin(), support.end(), target);
    if (target_position == support.end()) std::abort();
    const long long target_weight = weights[target_position - support.begin()];
    long long degree = 0;
    for (size_t i = 0; i < support.size(); ++i)
      if (support[i] & 1) degree += weights[i];
    out << "    {\"orbit_index\": " << orbit_index++
        << ", \"degree\": \"" << fraction(degree, target_weight)
        << "\", \"rho\": \"" << fraction(degree - target_weight, target_weight)
        << "\", \"balanced_support\": [";
    for (size_t i = 0; i < support.size(); ++i) {
      if (i) out << ',';
      out << "{\"mask\": " << support[i] << ", \"weight\": \""
          << fraction(weights[i], target_weight) << "\"}";
    }
    out << "]}";
    if (orbit_index != static_cast<int>(census.orbits.size())) out << ',';
    out << '\n';
  }
  out << "  ]\n}";
}

}  // namespace

int main(int argc, char** argv) {
  if (argc != 2) {
    std::cerr << "usage: enumerate_n6_eta_dual_vertices OUTPUT.json\n";
    return 2;
  }
  Census three = run_census(3);
  Census four = run_census(4);
  std::ofstream out(argv[1]);
  out << "{\n"
      << "  \"status\": \"complete exact minimal-balanced census for n=6 eta-dual vertices\",\n"
      << "  \"n\": 6,\n"
      << "  \"shapes\": [\n";
  emit_census(out, three);
  out << ",\n";
  emit_census(out, four);
  out << "\n  ]\n}\n";
}
