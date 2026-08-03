// Focused exhaustive census for seven-player eta-dual supports with at least
// three target-floor levels.  The two-level separator theorem eliminates all
// other supports for exact games.  We test the unresolved sharp-dimension
// splits (|S|,|P|)=(4,3),(5,2) and compute the normalized coefficient mass on
// carrier columns P union C.  Mass at least one directly certifies eta>=gamma.

#include <algorithm>
#include <array>
#include <cstdint>
#include <cstdlib>
#include <fstream>
#include <iostream>
#include <numeric>
#include <set>
#include <sstream>
#include <string>
#include <tuple>
#include <utility>
#include <vector>

namespace {

constexpr int N = 7;
constexpr int FULL = (1 << N) - 1;
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

bool balancing_weights(const Support& support, Weights* answer) {
  const int k = static_cast<int>(support.size());
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
    if (kernel[0] < 0)
      for (auto& value : kernel) value = -value;
    if (!std::all_of(kernel.begin(), kernel.end(),
                     [](long long value) { return value > 0; }))
      continue;
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
    *answer = std::move(kernel);
    return true;
  }
  return false;
}

struct Shape {
  int s_size = 0;
  long long supports_checked = 0;
  long long three_level_supports = 0;
  long long supports_below_unit_carrier_mass = 0;
  long long minimum_numerator = -1;
  long long minimum_denominator = 1;
  Support minimum_support;
  Weights minimum_weights;
  std::set<std::string> below_unit_orbits;
};

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

std::string canonical_key(const Support& support, const Weights& weights,
                          int s_size) {
  const auto group = group_permutations(s_size);
  std::string best;
  bool first = true;
  for (const auto& permutation : group) {
    std::vector<std::pair<int, long long>> terms;
    for (size_t i = 0; i < support.size(); ++i)
      terms.push_back({permute_mask(support[i], permutation), weights[i]});
    std::sort(terms.begin(), terms.end());
    std::ostringstream encoded;
    for (const auto& [mask, weight] : terms)
      encoded << mask << ':' << weight << ',';
    const std::string key = encoded.str();
    if (first || key < best) {
      first = false;
      best = key;
    }
  }
  return best;
}

std::pair<Support, Weights> decode(const std::string& key) {
  Support support;
  Weights weights;
  size_t start = 0;
  while (start < key.size()) {
    const size_t colon = key.find(':', start);
    const size_t comma = key.find(',', colon);
    support.push_back(std::stoi(key.substr(start, colon - start)));
    weights.push_back(std::stoll(key.substr(colon + 1, comma - colon - 1)));
    start = comma + 1;
  }
  return {support, weights};
}

void visit(const Support& support, int singleton_count, int target, int outside,
           Shape* shape) {
  ++shape->supports_checked;
  Weights weights;
  if (!balancing_weights(support, &weights)) return;
  std::set<long long> floor_levels{0};
  for (int index = 1; index <= singleton_count; ++index)
    floor_levels.insert(weights[index]);
  if (floor_levels.size() < 3) return;
  ++shape->three_level_supports;

  const long long target_weight = weights[0];
  long long carrier_numerator = 0;
  for (size_t index = 1 + singleton_count; index < support.size(); ++index) {
    const int mask = support[index];
    if ((mask & outside) == outside) {
      const int inside = mask & target;
      if (inside != 0 && inside != target) carrier_numerator += weights[index];
    }
  }
  if (carrier_numerator < target_weight) {
    ++shape->supports_below_unit_carrier_mass;
    shape->below_unit_orbits.insert(
        canonical_key(support, weights, shape->s_size));
  }
  if (shape->minimum_numerator < 0 ||
      carrier_numerator * shape->minimum_denominator <
          shape->minimum_numerator * target_weight) {
    shape->minimum_numerator = carrier_numerator;
    shape->minimum_denominator = target_weight;
    shape->minimum_support = support;
    shape->minimum_weights = weights;
  }
}

void combinations(const std::vector<int>& candidates, int need, int next,
                  int singleton_count, int target, int outside,
                  Support* support, Shape* shape) {
  if (need == 0) {
    visit(*support, singleton_count, target, outside, shape);
    return;
  }
  const int last = static_cast<int>(candidates.size()) - need;
  for (int index = next; index <= last; ++index) {
    support->push_back(candidates[index]);
    combinations(candidates, need - 1, index + 1, singleton_count, target,
                 outside, support, shape);
    support->pop_back();
  }
}

Shape classify(int s_size) {
  Shape shape;
  shape.s_size = s_size;
  const int target = (1 << s_size) - 1;
  const int outside = FULL ^ target;
  std::vector<int> candidates;
  for (int coalition = 1; coalition < FULL; ++coalition) {
    const bool target_singleton =
        (coalition & target) && !(coalition & (coalition - 1));
    if (coalition != target && !target_singleton) candidates.push_back(coalition);
  }
  for (int q = 2; q < s_size; ++q) {
    const int max_nonfloor = N - 1 - q;
    for (int l = 1; l <= max_nonfloor; ++l) {
      Support support{target};
      for (int player = 0; player < q; ++player) support.push_back(1 << player);
      combinations(candidates, l, 0, q, target, outside, &support, &shape);
      std::cerr << "S=" << s_size << " q=" << q << " l=" << l
                << " checked=" << shape.supports_checked
                << " three-level=" << shape.three_level_supports
                << " below-one=" << shape.supports_below_unit_carrier_mass
                << '\n';
    }
  }
  return shape;
}

std::string fraction(long long numerator, long long denominator) {
  const long long divisor = std::gcd(std::llabs(numerator), denominator);
  numerator /= divisor;
  denominator /= divisor;
  if (denominator == 1) return std::to_string(numerator);
  return std::to_string(numerator) + "/" + std::to_string(denominator);
}

void emit_shape(std::ostream& out, const Shape& shape) {
  const int target = (1 << shape.s_size) - 1;
  const int outside = FULL ^ target;
  out << "    {\n"
      << "      \"S_size\": " << shape.s_size << ",\n"
      << "      \"P_size\": " << N - shape.s_size << ",\n"
      << "      \"focused_supports_checked\": " << shape.supports_checked << ",\n"
      << "      \"three_level_supports_with_canonical_singletons\": "
      << shape.three_level_supports << ",\n"
      << "      \"minimum_carrier_mass\": \""
      << fraction(shape.minimum_numerator, shape.minimum_denominator) << "\",\n"
      << "      \"supports_below_unit_carrier_mass\": "
      << shape.supports_below_unit_carrier_mass << ",\n"
      << "      \"below_unit_symmetry_orbits\": "
      << shape.below_unit_orbits.size() << ",\n"
      << "      \"orbits\": [\n";
  int orbit_index = 0;
  for (const auto& key : shape.below_unit_orbits) {
    auto [support, weights] = decode(key);
    const auto target_position = std::find(support.begin(), support.end(), target);
    if (target_position == support.end()) std::abort();
    const long long target_weight = weights[target_position - support.begin()];
    long long carrier_numerator = 0;
    out << "        {\"orbit_index\": " << orbit_index++
        << ", \"balanced_support\": [";
    for (size_t index = 0; index < support.size(); ++index) {
      if (index) out << ',';
      out << "{\"mask\": " << support[index] << ", \"weight\": \""
          << fraction(weights[index], target_weight) << "\"}";
      const int inside = support[index] & target;
      if ((support[index] & outside) == outside && inside && inside != target)
        carrier_numerator += weights[index];
    }
    out << "], \"carrier_mass\": \""
        << fraction(carrier_numerator, target_weight) << "\"}";
    if (orbit_index != static_cast<int>(shape.below_unit_orbits.size())) out << ',';
    out << '\n';
  }
  out << "      ]\n"
      << "    }";
}

}  // namespace

int main(int argc, char** argv) {
  if (argc != 2) {
    std::cerr << "usage: enumerate_n7_three_level_eta_duals OUTPUT.json\n";
    return 2;
  }
  const Shape four = classify(4);
  const Shape five = classify(5);
  std::ofstream out(argv[1]);
  out << "{\n"
      << "  \"status\": \"complete focused census of n=7 three-level eta-dual supports\",\n"
      << "  \"criterion\": \"normalized carrier-column mass at least one directly implies eta>=gamma\",\n"
      << "  \"shapes\": [\n";
  emit_shape(out, four);
  out << ",\n";
  emit_shape(out, five);
  out << "\n  ]\n}\n";
  std::cout << "S=4 min="
            << fraction(four.minimum_numerator, four.minimum_denominator)
            << " below-one=" << four.supports_below_unit_carrier_mass << '\n'
            << "S=5 min="
            << fraction(five.minimum_numerator, five.minimum_denominator)
            << " below-one=" << five.supports_below_unit_carrier_mass << '\n';
  return 0;
}
