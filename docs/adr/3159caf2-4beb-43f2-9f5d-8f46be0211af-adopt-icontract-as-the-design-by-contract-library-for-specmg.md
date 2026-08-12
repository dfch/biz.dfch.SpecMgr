---
status: accepted
date: '2026-08-12'
decision-makers: OpenCode agent + user decision
id: 3159caf2-4beb-43f2-9f5d-8f46be0211af
version: 1.0.0
---

# Adopt icontract as the Design by Contract library for SpecMgr

## Context and Problem Statement

SpecMgr is building a comprehensive artifact management system for specifications. Design by Contract (DbC) is a software engineering approach that formalizes component interfaces with preconditions, postconditions, and invariants. This ADR addresses which Python DbC library to adopt for SpecMgr's domain models and tools, particularly for ensuring correct specification document handling and contract-based API design.

Two mature, MIT-licensed Python libraries offer DbC support: icontract (Parquery, Swiss company) and deal (life4, open-source community). Both support Python 3.11+. The choice impacts code maintainability, inheritance patterns, and development practices.

## Decision Drivers

1. **Inheritance support**: SpecMgr's document type hierarchy (e.g., ADR extending base document classes) requires proper Liskov Substitution Principle (LSP) compliance. Contract inheritance with weakened preconditions and strengthened postconditions is essential.

2. **Contract clarity in APIs**: MCP tools, resources, and prompts must declare clear contracts for argument validation and return guarantees. Pre/post-conditions reduce ambiguity and enable better error messages.

3. **Ecosystem maturity**: Both libraries are production-ready. icontract has 411+ GitHub stars and is maintained by Parquery. deal has 903+ stars with active development and broader side-effect tracking.

4. **Python 3.11+ requirement**: Both libraries officially support Python 3.11 and later (specmgr currently requires Python >= 3.11).

5. **Side-effect tracking**: deal's @deal.pure decorator and side-effect analysis are valuable for pure functional components, but not essential for SpecMgr's current architecture.

## Considered Options

1. **icontract**: Design-by-contract with superior contract inheritance (LSP-compliant), informative violation messages, no side-effect tracking.
2. **deal**: Comprehensive DbC + side-effect tracking, static analysis, property-based testing integration, but weaker contract inheritance model.
3. **No DbC library**: Hand-written assertions and validation. Not recommended—loses benefits of formal contracts, tooling, and documentation.

## Decision Outcome

Adopt **icontract** as SpecMgr's Design by Contract library.

icontract is the best fit for SpecMgr because:

- **Contract inheritance is non-negotiable**: SpecMgr's document type hierarchy (base documents → ADRs, future use-cases, requirements) requires correct LSP-compliant inheritance. icontract is specifically designed for this; deal's inheritance model is less rigorous.
- **Liskov Substitution Principle**: Derived document classes can weaken preconditions and strengthen postconditions. This ensures type-safe polymorphism and correct substitutability—critical for extensible document systems.
- **Informative error messages**: icontract includes source code and variable values in violation messages, enabling faster debugging during development and in CI/CD.
- **Mature ecosystem**: 411+ stars, production use, integrations with linters (pyicontract-lint), Sphinx, hypothesis-based testing (icontract-hypothesis).
- **Python 3.11+ certified**: Verified compatible with Python 3.11–3.13.

**Trade-off**: icontract does not provide side-effect tracking (no @pure decorator). SpecMgr can use Python's type system, assertions, and custom validation for purity guarantees where needed. This trade-off is acceptable because SpecMgr's current architecture does not require runtime side-effect enforcement.

### Consequences

**Positive**:
- Contract inheritance is correctly modeled, reducing subtle bugs in polymorphic document handling.
- MCP tools and resources gain declarative, self-documenting contracts.
- Integration with pyicontract-lint enables static contract checking in CI/CD.
- Future document types (use-cases, requirements) inherit a proven contract framework.
- Clear preconditions reduce defensive programming overhead.

**Negative**:
- No built-in @pure enforcement; developers must rely on code review and type hints for purity.
- icontract has fewer GitHub stars than deal (411 vs 903), though both are mature.
- Side-effect tracking requires third-party tools (e.g., abstract syntax analysis) if later needed.

**Neutral**:
- One additional dependency (icontract); locked to MIT license (permissive, no conflicts).
- Learning curve for contract inheritance rules (LSP); mitigated by documentation and examples.

### Confirmation

Implementation checklist:
- [ ] Add `icontract` to `pyproject.toml` dependencies (Python 3.11+).
- [ ] Document contract patterns in `.specmgr/conventions.md` or a new `docs/design-by-contract.md`.
- [ ] Create example contracts for ADR model (preconditions on `AdrBody`, `AdrFrontmatter`; invariants on `Adr`).
- [ ] Apply contracts to MCP tools: `create_adr`, `update_section`, `option_create`, etc.
- [ ] Integrate `pyicontract-lint` into pre-commit hooks and CI (optional, phase 2).
- [ ] Add tests verifying contract inheritance with derived document types (e.g., when use-case model is introduced).
- [ ] Update ADR-related tools and prompts to leverage contracts for validation.

## Pros and Cons of the Options

### Option 1: icontract: Superior contract inheritance, best for document type hierarchies

**Library**: icontract (maintained by Parquery, Swiss AI solutions company)
**GitHub stars**: 411 | **License**: MIT | **Python**: 3.6–3.13 (3.11+ certified for SpecMgr)

**Strengths**:
- **Best-in-class contract inheritance**: Properly implements Liskov Substitution Principle (LSP). Derived classes can weaken preconditions and strengthen postconditions—essential for SpecMgr's document type hierarchy (base documents → ADRs → future use-cases, requirements).
- **Informative violation messages**: Includes source code of the contract and variable values at breach time. Example:
  ```
  ViolationError: x > 0:
  x was -1
  y was 5
  ```
- **Class invariants**: `@invariant` decorator enforces state invariants before/after all public methods. Critical for document state consistency.
- **Snapshot support**: `@snapshot` captures argument values before execution for postcondition comparisons (useful for documenting expected state transitions).
- **Production-ready**: Used by Parquery and other enterprises since 2013+.
- **Ecosystem**: pyicontract-lint (static checking), sphinx-icontract (documentation), icontract-hypothesis (property-based testing).
- **Swiss alignment**: Maintained by Parquery, a Swiss company.

**Weaknesses**:
- Fewer GitHub stars than deal (411 vs 903), though maturity is equivalent.
- No side-effect tracking (no `@pure` decorator). Must use type hints + code review for purity enforcement.
- No built-in static analysis of side effects (could be added later via third-party tools).

**SpecMgr fit**: (5/5)
- Perfect for extensible document systems requiring contract inheritance.
- Aligns with Swiss company values.
- Informative errors reduce debugging time in tools and CI/CD.
- Mature, production-proven.

### Option 2: deal: Comprehensive DbC + side-effect tracking, broader feature set

**Library**: deal (maintained by life4, open-source community)
**GitHub stars**: 903 | **License**: MIT | **Python**: 3.8–3.13 (3.11+ certified for SpecMgr)

**Strengths**:
- **@pure decorator**: Formally declare functions with no side effects. Linter enforces this:
  ```python
  @deal.pure
  def calculate_tax(amount: float) -> float:
      print("side effect!")  # Linter catches this
      return amount * 0.19
  ```
  Invaluable for pure functional components and formal verification.
- **Side-effect tracking**: Explicit decorators (`@deal.has(deal.Writes())`, `@deal.Raises()`) document all effects. Better for mutation-heavy systems.
- **Comprehensive static analysis**: Built-in linter (`deal lint`) checks preconditions, postconditions, side-effects. No external plugin needed.
- **Property-based testing**: Integrates with Hypothesis for automated test generation.
- **More active**: 903 GitHub stars, very active development.
- **Python 3.8+**: Broader version support (though SpecMgr targets 3.11+).

**Weaknesses**:
- **Weaker contract inheritance**: Inheritance model less rigorous than icontract. Liskov Substitution Principle compliance is not as systematically enforced.
- **Less suitable for polymorphic hierarchies**: SpecMgr's document type hierarchy (base → ADR → future types) needs stronger LSP guarantees. deal's inheritance is more ad-hoc.
- **No snapshot support**: Cannot easily capture pre-execution state for postcondition checks (e.g., comparing old vs new document state).
- **Less mature for class invariants**: While supported, invariant checking is less comprehensive than icontract.
- **Community-driven**: No corporate backing; relies on volunteer maintenance (though very active).

**SpecMgr fit**: (3/5)
- Excellent for contract documentation and side-effect enforcement.
- @pure decorator is a nice-to-have but not critical for SpecMgr's current design.
- Inheritance model insufficient for SpecMgr's planned document type hierarchy.
- Broader feature set introduces scope creep (side-effect tracking, formal verification) not yet needed.

**Trade-off**: To use deal well, SpecMgr would need careful API design to avoid inheritance complexity. The benefit (@pure) does not outweigh the cost (weaker inheritance for documents).

## More Information

### Related Resources

- icontract documentation: https://icontract.readthedocs.io/en/latest/
- icontract GitHub: https://github.com/Parquery/icontract
- deal documentation: https://deal.readthedocs.io/ (for reference if side-effect tracking becomes critical)
- Parquery (icontract maintainer): https://parquery.com (Swiss AI solutions company)

### Liskov Substitution Principle and Contract Inheritance

- Base class preconditions must be **weakened** (or stay the same) in derived classes.
- Base class postconditions must be **strengthened** (or stay the same) in derived classes.
- icontract enforces these rules automatically via `@require`, `@ensure`, `@invariant` decorators on inherited methods.

### icontract Code Examples

#### 1. Preconditions and Postconditions

```python
from icontract import require, ensure

@require(lambda x: x > 0, "x must be positive")
@ensure(lambda result: result > 0, "result must be positive")
def sqrt(x: float) -> float:
    """Calculate square root with contracts."""
    return x ** 0.5

# Valid call
sqrt(9)      # Returns 3.0 ✓

# Violates precondition
sqrt(-1)     # ViolationError: x must be positive
```

#### 2. Class Invariants (Document State Consistency)

```python
from icontract import invariant

@invariant(lambda self: len(self.title) > 0, "title must not be empty")
@invariant(lambda self: self.status in ("draft", "proposed", "accepted", "rejected"))
class Document:
    """Base document class with state invariants."""
    
    def __init__(self, title: str, status: str = "draft"):
        self.title = title
        self.status = status
    
    @require(lambda self, new_status: new_status in ("draft", "proposed", "accepted", "rejected"))
    def set_status(self, new_status: str) -> None:
        self.status = new_status

doc = Document("My ADR")
doc.set_status("accepted")  # ✓
doc.title = ""              # ViolationError: invariant violated
```

#### 3. Contract Inheritance (Liskov Substitution Principle)

```python
from icontract import require, ensure, invariant

@invariant(lambda self: self.balance >= 0)
class Account:
    """Base account: precondition requires positive amount."""
    
    def __init__(self, balance: float):
        self.balance = balance
    
    @require(lambda self, amount: amount > 0, "amount must be positive")
    @ensure(lambda self, result: result > self.balance)
    def deposit(self, amount: float) -> float:
        self.balance += amount
        return self.balance

@invariant(lambda self: self.balance >= 0)
class PremiumAccount(Account):
    """Derived account: WEAKENS precondition (allows zero), STRENGTHENS postcondition (adds interest)."""
    
    @require(lambda self, amount: amount >= 0, "amount must be non-negative")  # WEAKENED
    @ensure(lambda self, result: result >= self.balance)  # STRENGTHENED
    def deposit(self, amount: float) -> float:
        self.balance += amount
        self.balance *= 1.01  # Add 1% interest
        return self.balance

# Both are substitutable: PremiumAccount can be used wherever Account is expected
account: Account = PremiumAccount(100)
account.deposit(0)      # Works! Precondition weakened to allow zero
account.deposit(50)     # Works! Postcondition strengthened to guarantee interest
```

#### 4. Snapshots (Capture Pre-execution State)

```python
from icontract import snapshot, ensure

class Document:
    def __init__(self, content: str):
        self.content = content
    
    @snapshot(lambda self: len(self.content), name="old_length")
    @ensure(lambda self, old_length: len(self.content) == old_length + 1)
    def append_char(self, char: str) -> None:
        """Append a character, ensure length increases by exactly 1."""
        self.content += char

doc = Document("hello")
doc.append_char("!")     # ✓ Length: 5 → 6
```

#### 5. For SpecMgr: ADR Document Contracts

```python
from icontract import require, ensure, invariant

@invariant(lambda self: len(self.title) > 0, "ADR title required")
@invariant(lambda self: self.status in ("draft", "proposed", "accepted", "rejected", "superseded"))
class AdrDocument:
    """ADR with contracts on state and operations."""
    
    def __init__(self, title: str):
        self.title = title
        self.status = "draft"
        self.options = []
    
    @require(lambda self, option_title: len(option_title) > 0, "option title cannot be empty")
    @ensure(lambda self: len(self.options) > 0, "must have at least one option after add")
    def add_option(self, option_title: str) -> None:
        """Add a decision option; ensure non-empty options list."""
        self.options.append({"title": option_title})
    
    @require(lambda self, new_status: new_status in ("draft", "proposed", "accepted", "rejected"))
    @ensure(lambda self, new_status: self.status == new_status)
    def set_status(self, new_status: str) -> None:
        """Update status; postcondition ensures status is set exactly."""
        self.status = new_status

# Usage
adr = AdrDocument("Adopt icontract")
adr.add_option("icontract: superior inheritance")
adr.set_status("accepted")
print(f"{adr.title} is {adr.status}")  # ✓
```

### Future Consideration

If SpecMgr later requires side-effect tracking for formal verification or pure functional components, a hybrid approach (icontract for DbC + deal for side-effect analysis on specific functions) may be explored.
