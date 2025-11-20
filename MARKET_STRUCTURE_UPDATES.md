# Market Structure Agent Updates

## Summary

Updated `src/agent/agents/market_structure.py` to detect trend using YTC's swing analysis methodology as documented in `docs/05_TREND_DEFINITION.md`.

## Previous Implementation

The original `_analyze_trend_structure()` method used talib SMA (Simple Moving Average):
- Calculated 10-period and 25-period SMAs
- Classified trend based on price-to-MA relationship
- Simple but not aligned with YTC swing analysis approach

```python
# OLD: SMA-based trend detection
if current > short_ma_current > medium_ma_current:
    return TrendDirection.UPTREND
elif current < short_ma_current < medium_ma_current:
    return TrendDirection.DOWNTREND
else:
    return TrendDirection.SIDEWAYS
```

## New Implementation

Now uses **YTC swing pattern analysis** following the methodology from `05_TREND_DEFINITION.md`:

### Trend Classification Logic

**Uptrend (HH + HL)**:
- Recent swing high > prior swing high
- Recent swing low > prior swing low
- Series of higher highs and higher lows

**Downtrend (LH + LL)**:
- Recent swing high < prior swing high
- Recent swing low < prior swing low
- Series of lower highs and lower lows

**Sideways**:
- No clear pattern matching HH/HL or LH/LL
- Insufficient swing data for classification

### Algorithm

```python
def _analyze_trend_structure(closes, highs, lows):
    """
    1. Detect swing highs and lows using scipy.signal.argrelextrema
    2. Extract last 2 swing highs and last 2 swing lows
    3. Compare most recent swing to prior swing:
       - HH + HL pattern → Uptrend
       - LH + LL pattern → Downtrend
       - Other → Sideways
    """
```

### Key Changes

1. **Swing-based analysis**: Now uses the same swing detection (`_detect_swing_points`) already used elsewhere in the agent
2. **YTC-aligned**: Follows the exact methodology from `05_TREND_DEFINITION.md` for consistency across agents
3. **Flexible input**: Accepts optional `highs` and `lows` parameters, extracting from OHLC if not provided
4. **Minimum requirements**: Requires at least 2 swing highs and 2 swing lows for classification

### Code Changes

**Updated method signature**:
```python
def _analyze_trend_structure(
    self, closes: list[float], 
    highs: list[float] = None, 
    lows: list[float] = None
) -> TrendDirection:
```

**Removed**:
- talib SMA calculations
- Price-to-MA comparisons

**Added**:
- Swing detection using `_detect_swing_points()`
- HH/HL pattern detection for uptrends
- LH/LL pattern detection for downtrends
- Explicit pattern matching logic

## Impact on Market Structure Analysis

### Structural Framework Output

The `structural_framework` now contains:
- `trend_structure`: Based on YTC swing patterns instead of moving averages
- `resistance_zones` and `support_zones`: Unchanged, still based on swing points
- More aligned with YTC's trading methodology

### Consistency

This update ensures consistency across the trading system:
1. **Market Structure Agent**: Uses swing-based trend detection
2. **Trend Definition Agent**: Performs detailed swing analysis
3. Both agents now follow the same YTC swing analysis approach

## Testing

Syntax validation passes:
```bash
python3 -m py_compile src/agent/agents/market_structure.py  # ✓ valid
```

## YTC Methodology Reference

From `05_TREND_DEFINITION.md`:

**Uptrend Definition**:
- Series of Higher Highs (HH)
- Series of Higher Lows (HL)
- Each pullback finds support at higher levels

**Downtrend Definition**:
- Series of Lower Highs (LH)
- Series of Lower Lows (LL)
- Each bounce finds resistance at lower levels

**Sideways**:
- Price moves between defined support and resistance
- No consistent HH/HL or LH/LL pattern
- Alternating highs and lows at similar levels

## Migration Notes

The change is backward compatible for downstream nodes:
- Output structure remains unchanged (`MarketStructureOutput`)
- `structural_framework.trend_structure` is still a `TrendDirection` enum
- Graph nodes using this agent don't need updates
- Actual trend classification may differ from SMA-based approach (expected and correct)

## Dependencies

- `scipy.signal.argrelextrema`: For swing point detection
- `numpy`: For array operations
- talib: Removed from trend detection (still used in `calculate_indicators()`)
