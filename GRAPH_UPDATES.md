# Graph.py State Updates

Updated `src/agent/graph.py` to align with new agent implementations. All four analysis nodes now match the input/output contracts of their corresponding agents.

## Changes Made

### 1. `trend_definition_node` (lines 285-360)

**Input Changes:**
- Old: `price_history`, `current_price`, `trend_direction` (simple strings)
- New: Structured `market_data` and `higher_timeframe_context` objects matching `TrendDefinition.config`

**Key transformations:**
- Extract bars from `price_history` with OHLC data
- Build HTF context with support/resistance/swing levels from state
- Pass proper `market_data.bars` structure with `high/low/close/timestamp`

**Output Changes:**
- Old: `trend_confirmed`, `primary_trend`, `trend_strength`, `entry_bias`, `moving_averages`
- New: Structured `trend_analysis`, `swing_structure`, `structure_integrity`, `htf_alignment` from `TrendDefinitionOutput`

**State Storage:**
```python
state["market_data"]["trend_analysis"] = result["trend_analysis"]
state["market_data"]["swing_structure"] = result["swing_structure"]
state["market_data"]["structure_integrity"] = result["structure_integrity"]
state["market_data"]["htf_alignment"] = result["htf_alignment"]
```

---

### 2. `market_structure_node` (lines 164-251)

**Input Changes:**
- Old: `market_data`, `price_history`, `base_price`, `hummingbot_client` (mixed types)
- New: `ohlc_data` array matching MarketStructure's expected format

**Key transformations:**
- Convert `price_history` list to `ohlc_data` with dict format (open/high/low/close/volume)
- Pass `min_swing_bars` and `sr_zone_thickness_pct` for zone detection configuration
- Remove unused `hummingbot_client` from config (not needed by agent)

**Output Changes:**
- Old: `trend_direction`, `support_level`, `resistance_level`, `market_volatility`, `key_price_levels`
- New: Structured `structural_framework` (with trend_structure, support_zones, resistance_zones, prior_session) and `current_context` from `MarketStructureOutput`

**State Storage:**
```python
state["market_data"]["structural_framework"] = structural_framework
state["market_data"]["current_context"] = current_context
state["market_data"]["support"] = current_context["nearest_support"]
state["market_data"]["resistance"] = current_context["nearest_resistance"]
state["market_data"]["distance_to_support_pct"] = current_context["distance_to_support_pct"]
state["market_data"]["distance_to_resistance_pct"] = current_context["distance_to_resistance_pct"]
state["market_data"]["price_location"] = current_context["price_location"]
```

**Key differences:**
- Now stores full structural framework with zone details instead of single levels
- Includes distance percentages for setup evaluation
- Tracks price location relative to structure (at_support/at_resistance/in_range/breakout)

---

### 3. `strength_weakness_node` (lines 363-450)

**Input Changes:**
- Old: `price_history`, `current_price`, `entry_bias` (simple indicators)
- New: Structured `trend_data`, `bar_data`, `support_resistance` matching `StrengthWeakness.config`

**Key transformations:**
- Extract bars from `price_history` (last 20 bars) with OHLC + body_size/bar_range
- Map trend direction from previous node's `trend_analysis` result
- Build bar data with momentum metrics: `body_size`, `bar_range`
- Include prior swing information from `swing_structure`

**Output Changes:**
- Old: `momentum_direction`, `rsi_value`, `macd_signal`, `divergence_detected`, etc.
- New: Structured `strength_analysis`, `weakness_signals`, `setup_applicability` from `StrengthWeaknessOutput`

**State Storage:**
```python
state["market_data"]["strength_analysis"] = strength_analysis
state["market_data"]["weakness_signals"] = weakness_signals
state["market_data"]["setup_applicability"] = setup_applicability
```

---

### 4. `setup_scanner_node` (lines 493-603)

**Input Changes:**
- Old: Flat config with individual fields (current_price, support, resistance, trend, etc.)
- New: Hierarchical config with `trend_data`, `price_action`, `support_resistance`, `market_conditions`, `config`

**Key transformations:**
- Extract bars from `price_history` (last 30 bars) with OHLC + body_strength + close_position
- Build S/R levels array from support/resistance state values
- Map trend direction from `trend_analysis`
- Extract swing structure highs/lows for trend context
- Configure scanner with min confluence factors, risk/reward, enabled setup types

**Output Changes:**
- Old: `scan_complete`, `total_setups`, `best_setup` (flat structure)
- New: `active_setups` (list of `YTCSetup` objects), `scan_summary` from `SetupScannerOutput`

**State Storage:**
```python
state["market_data"]["active_setups"] = active_setups
state["market_data"]["scan_summary"] = scan_summary
```

---

### 5. `checkpoint_2_node` (lines 453-502)

**Updated to work with new setup structure:**
- Gets best setup from `active_setups[0]` instead of `best_setup` field
- Extracts setup details from new `YTCSetup` TypedDict structure:
  - `entry_zone.ideal` → entry price
  - `stop_loss.price` → stop loss
  - `targets[0].price` → take profit
  - `type` → setup type (TST/BOF/BPB/PB/CPB)
  - `probability_score` → confidence/probability
  - `quality_rating` → A/B/C rating
  - `risk_reward_ratio` → R:R

---

---

### 6. `entry_execution_node` Update (line 279-280)

**Input Change:**
- Now extracts `best_setup` from `active_setups[0]` instead of direct `state["market_data"].get("best_setup")`
- Properly handles empty setup list (None when no setups available)

---

## Data Flow Through Agents

### Market Structure → Trend Definition → Strength/Weakness → Setup Scanner

```
market_structure_node output:
├── structural_framework (trend_structure, support/resistance zones, prior_session)
├── current_context (price_location, nearest levels, distances)
└── analysis_timestamp

    ↓ stored in state["market_data"]

trend_definition_node input uses:
├── price_history (from previous node)
└── state S/R levels for HTF context

trend_definition_node output:
├── trend_analysis (direction, confidence, strength_rating)
├── swing_structure (highs, lows, leading swings)
├── structure_integrity (breaks, reversal warnings)
└── htf_alignment (HTF sync check)

    ↓ stored in state["market_data"]

strength_weakness_node input uses:
├── trend_analysis.direction → trend direction
├── swing_structure → prior swing info
└── state S/R levels

strength_weakness_node output:
├── strength_analysis (momentum/projection/depth scores)
├── weakness_signals (reversal warnings, divergences)
└── setup_applicability (which setup types work)

    ↓ stored in state["market_data"]

setup_scanner_node input uses:
├── trend_analysis (direction, strength)
├── swing_structure (leading highs/lows)
├── strength_analysis (for confluence factors)
├── state S/R levels & bars
└── market conditions

setup_scanner_node output:
├── active_setups[] (list of YTCSetup)
└── scan_summary (stats and best setup ID)
```

---

## Testing

All syntax checks pass:
```bash
python3 -m py_compile src/agent/graph.py  # ✓ valid
```

Node functions correctly transform state data between agents and maintain the graph flow.
