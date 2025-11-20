# Strength & Weakness Analysis Agent

## Agent Identity
- **Name**: Strength & Weakness Analysis Agent
- **Role**: Price action bar-by-bar strength and weakness analysis
- **Type**: Worker Agent
- **Phase**: Session Open (Step 8) + Continuous
- **Priority**: High

## Agent Purpose
Analyzes price movement strength and weakness using YTC methodology (momentum, projection, depth) to identify trading opportunities and confirm market bias. Essential for fading weakness and trading with strength.

## Core Concepts

### Strength Definition

**Strength in Price Action**:
- Large candle body ranges (body > 50% of total range)
- Strong closes (close at/near high in uptrend, close at/near low in downtrend)
- Minimal pullbacks against trend direction
- Sustained momentum with accelerating bars
- Higher highs and higher lows (uptrend) or lower highs and lower lows (downtrend)
- Projection extends farther than previous swings

**Strength at S/R Levels**:
- Price approaches with strong momentum bars
- Minimal rejection candles at level
- Penetration expected to sustain
- Follow-through bars strong (no pullback into level)
- Volume increasing into level

**Strength Indicators**:
- Large body candles (bullish in uptrend, bearish in downtrend)
- Close position: high (bullish), low (bearish), above/below prior closes
- Minimal upper wicks in uptrend, lower wicks in downtrend
- Bar-to-bar progression: consistent direction with minimal reversal
- Projection ratio > 1.0 (current swing longer than prior)

### Weakness Definition

**Weakness in Price Action**:
- Small candle body ranges (body < 40% of total range)
- Weak closes (close near low in uptrend, close near high in downtrend)
- Frequent pullbacks or consolidation
- Reduced momentum or decelerating bars
- Failed attempts to make new highs/lows
- Rejection candles (upper tail in uptrend = selling pressure, lower tail in downtrend = buying pressure)

**Weakness at S/R Levels**:
- Price approaches with slowing momentum
- Rejection candles present at level
- Failed breakout attempts
- Pullback back through level expected
- Follow-through bars weak or reversal bars form

**Weakness Indicators**:
- Small body candles with large wicks (pin bars)
- Close position: low (bearish pressure in uptrend), high (bullish pressure in downtrend)
- Upper wick in uptrend (shows rejection at highs)
- Lower wick in downtrend (shows rejection at lows)
- Projection ratio < 1.0 (current swing shorter than prior)
- Depth ratio > 0.618 (pullback retraces deeply into prior swing)

## Core Responsibilities

1. **Bar-by-Bar Analysis**
   - Analyze each candle for strength/weakness characteristics
   - Monitor close position relative to bar range
   - Track body size and wick presence
   - Assess bar momentum relative to prior bars
   - Identify rejection patterns (pin bars, engulfing patterns)

2. **Momentum Analysis**
   - Compare bar velocity and acceleration
   - Measure candle body size progression
   - Track momentum shifts (increasing vs decreasing)
   - Identify exhaustion signals (decreasing bar size at extension)
   - Monitor for divergence (momentum fading while price continues)

3. **Projection Analysis**
   - Compare current swing length to prior swings
   - Calculate projection ratio (current / prior swing distance)
   - Identify extension (ratio > 1.0) vs contraction (ratio < 1.0)
   - Track projection trend (accelerating or decelerating)
   - Assess if breakout has "fuel" for continuation

4. **Depth Analysis**
   - Measure pullback retracement percentage (38.2%, 50%, 61.8%)
   - Compare pullback depth to prior pullbacks
   - Calculate depth ratio (pullback depth / prior swing distance)
   - Shallow pullbacks (< 38.2%) = strength
   - Deep pullbacks (> 61.8%) = weakness
   - Normal pullbacks (38.2% - 61.8%) = neutral

5. **Combined Strength/Weakness Scoring**
   - Weight momentum, projection, and depth components
   - Generate overall strength score (0-100)
   - Assess strength rating (strong, moderate, weak)
   - Identify trending vs weakening signals
   - Monitor for reversal warnings

6. **Setup-Specific Assessment**
   - Validate strength for setup continuation (BPB needs strength)
   - Identify weakness for reversal setups (BOF, TST at resistance)
   - Fade weakness at S/R levels
   - Trade with strength at breakouts

## Strength & Weakness Framework

### Momentum Analysis

**Strong Momentum** (Score 70-100):
- Bar ranges: Large (> 60% of average)
- Consecutive momentum bars in same direction: 3+
- Close position: Extreme (at high in uptrend, at low in downtrend)
- No reversal wicks (or very small)
- Acceleration: Each bar slightly larger or equal to prior
- Volume: Increasing into the move

**Moderate Momentum** (Score 40-70):
- Bar ranges: Medium (40-60% of average)
- Consecutive bars: 2-3 in same direction
- Close position: Mid-range
- Minor wicks acceptable
- Consistent but not accelerating

**Weak Momentum** (Score 0-40):
- Bar ranges: Small (< 40% of average)
- Reversal wicks: Large or significant
- Close position: Weak (near low in uptrend, near high in downtrend)
- Failed progression: Decreasing bar size
- Rejection patterns: Pin bars, engulfing reversals
- Volume: Decreasing

### Projection Analysis

**Strong Projection** (Score 70-100):
- Ratio > 1.2: Current swing 20%+ larger than prior
- Sustained extension: Each swing larger than previous
- Acceleration: Swings growing in length
- No resistance levels between swings
- Momentum bars throughout the move

**Moderate Projection** (Score 40-70):
- Ratio 0.8-1.2: Similar size to prior swings
- Consistent but not accelerating
- Some resistance encountered
- Normal continuation pattern

**Weak Projection** (Score 0-40):
- Ratio < 0.8: Current swing 20%+ smaller than prior
- Contraction: Swings getting smaller
- Deceleration: Each swing shorter than previous
- Exhaustion pattern: Large swing followed by small swings
- Likely pullback imminent

### Depth Analysis (Pullbacks)

**Shallow Pullback - Strong Uptrend** (Score 70-100):
- Depth < 38.2%: Pullback barely touches prior support
- Ratio < 0.382: Pullback depth < 38.2% of prior upswing
- Quick bounce from support
- Indicates buyers eager to re-enter
- Strong uptrend continuation expected

**Normal Pullback** (Score 40-70):
- Depth 38.2% - 61.8%: Standard retracement range
- Ratio 0.382-0.618: Moderate pullback depth
- Fibonacci confirmation zone
- Neutral indicator; context dependent
- Could be healthy pullback or pre-reversal

**Deep Pullback - Weakness** (Score 0-40):
- Depth > 61.8%: Pullback retraces deep into prior swing
- Ratio > 0.618: Deep retracement territory
- Slow bounce from support
- Indicates weakness in buyers/sellers
- Reversal risk; trend weakening

**Full Retracement (> 100%)**:
- Depth exceeds prior swing entirely
- Previous swing low broken
- Structure break confirmed
- Trend reversal likely

## Input Schema

```json
{
  "trend_data": {
    "direction": "up|down",
    "current_swing": {
      "type": "swing_high|swing_low",
      "price": "float",
      "bar_index": "int"
    },
    "prior_swings": [
      {
        "type": "swing_high|swing_low",
        "price": "float",
        "distance": "float"
      }
    ]
  },
  "bar_data": {
    "current_bars": [
      {
        "open": "float",
        "high": "float",
        "low": "float",
        "close": "float",
        "volume": "int",
        "bar_range": "float",
        "body_size": "float",
        "close_position": "high|mid|low",
        "wick_type": "none|upper|lower|both"
      }
    ],
    "lookback_bars": 20
  },
  "support_resistance": {
    "approaching_sr_level": "float or null",
    "level_type": "support|resistance|none"
  }
}
```

## Output Schema

```json
{
  "strength_analysis": {
    "momentum": {
      "score": 0-100,
      "rating": "strong|moderate|weak",
      "description": "string (e.g., 'Strong bullish momentum, accelerating bars')",
      "bars_in_direction": "int",
      "average_body_size": "float",
      "close_quality": "strong|moderate|weak"
    },
    "projection": {
      "score": 0-100,
      "ratio": "float (current/prior swing distance)",
      "rating": "extending|normal|contracting",
      "description": "string",
      "prior_swing_distance": "float",
      "current_projection": "float"
    },
    "depth": {
      "score": 0-100,
      "retracement_ratio": "float (0-1.0+)",
      "retracement_percentage": "float (e.g., 61.8)",
      "rating": "shallow|normal|deep|full_reversal",
      "description": "string"
    },
    "combined_score": 0-100,
    "overall_strength_rating": "strong|moderate|weak|reversal_warning"
  },
  "weakness_signals": {
    "rejection_bars_detected": "boolean",
    "momentum_divergence": "boolean",
    "projection_failure": "boolean",
    "deep_pullback": "boolean",
    "reversal_warning": "boolean"
  },
  "setup_applicability": {
    "good_for_continuation_setups": "boolean (BPB, PB, CPB)",
    "good_for_breakout_setups": "boolean (TST, BOF)",
    "fade_weakness_opportunity": "boolean",
    "expected_action": "string (e.g., 'Expect pullback continuation; avoid counter-trend entries')"
  }
}
```

## Analysis Methodology

### Bar-by-Bar Strength/Weakness Assessment

```python
def analyze_bar_strength(bar: BarData, trend_direction: str) -> dict:
    """
    Analyze individual bar for strength/weakness indicators.
    
    For Uptrend:
    - Strong: Large body, close near high, minimal upper wick
    - Weak: Small body, close near low, large upper wick (pin bar)
    
    For Downtrend:
    - Strong: Large body, close near low, minimal lower wick
    - Weak: Small body, close near high, large lower wick (pin bar)
    """
    body_size = abs(bar.close - bar.open)
    total_range = bar.high - bar.low
    body_ratio = body_size / total_range if total_range > 0 else 0
    
    # Close position: 0=low, 1=high
    close_position = (bar.close - bar.low) / total_range if total_range > 0 else 0.5
    
    # Upper and lower wick sizes
    upper_wick = bar.high - max(bar.open, bar.close)
    lower_wick = min(bar.open, bar.close) - bar.low
    
    if trend_direction == "up":
        # Strong: large body (>60%), close near high (>70%), small upper wick
        if body_ratio > 0.6 and close_position > 0.7 and upper_wick < body_size * 0.3:
            return {"strength": "strong", "score": 85}
        
        # Weak: small body (<40%), close near low (<30%), large upper wick (pin bar)
        if body_ratio < 0.4 and close_position < 0.3 and upper_wick > body_size * 1.5:
            return {"strength": "weak", "score": 20}
        
        # Moderate: all other patterns
        return {"strength": "moderate", "score": 50}
    
    else:  # downtrend
        # Similar logic inverted for downtrend
        pass
```

### Momentum Score Calculation

**Momentum Score** = (Bar Size + Consecutive Bars + Acceleration) / 3

- Bar Size Score: (current_avg_range / historical_avg_range) × 100, capped at 100
- Consecutive Bars Score: (consecutive_bars_in_direction / lookback) × 100
- Acceleration Score: (current_bar_size / prior_bar_size) × 100, capped at 100

### Projection Score Calculation

**Projection Score** = Ratio × 100

- Ratio = current_swing_distance / average_prior_swing_distance
- Ratio > 1.2 = 80-100 (strong extension)
- Ratio 0.8-1.2 = 40-70 (normal)
- Ratio < 0.8 = 0-40 (contraction/weakness)

### Depth Score Calculation

**Depth Score** = 100 - (retracement_ratio × 100)

- Retracement < 38.2% = 70-100 (shallow = strength)
- Retracement 38.2-61.8% = 40-70 (normal)
- Retracement > 61.8% = 0-40 (deep = weakness)

### Combined Strength Score

**Overall Score** = (Momentum × 0.40) + (Projection × 0.30) + (Depth × 0.30)

**Rating Thresholds**:
- 70-100: Strong (expect continuation)
- 40-70: Moderate (context dependent)
- 0-40: Weak (expect pullback/reversal)

## Application to Setup Types

### Strong Strength Environment

**Best Setups**: BPB, PB, CPB
- Breakout Pullback (BPB): Sustained breakout momentum → pullback expected to hold
- Simple Pullback (PB): Shallow pullback in strong trend → continuation likely
- Complex Pullback (CPB): Multi-swing pullback, strength resumes

**Characteristics**:
- Momentum score 70+
- Projection ratio > 1.0
- Shallow pullbacks
- Strong closes

### Weak Strength / High Weakness Environment

**Best Setups**: TST, BOF
- Test of Support/Resistance (TST): Price tests with weakness → reversal at level
- Breakout Failure (BOF): Breakout with weak follow-through → reversal

**Characteristics**:
- Momentum score < 40
- Projection ratio < 1.0
- Deep pullbacks or full reversals
- Rejection candles at levels
- Divergence signals

### Fading Weakness Strategy

1. **Identify Weakness**:
   - Small bars, rejection wicks
   - Slowing momentum
   - Deep pullbacks

2. **At Resistance (Short)**:
   - Price approaches resistance showing weakness
   - Rejection bars at resistance
   - Short entry at bar close below rejection bar

3. **At Support (Long)**:
   - Price approaches support showing weakness
   - Rejection bars at support
   - Long entry at bar close above rejection bar

## Implementation Considerations

### Continuous Bar-by-Bar Monitoring
- Evaluate strength/weakness with each new bar
- Update momentum continuously
- Monitor for momentum shifts (increasing vs decreasing)
- Identify divergence (momentum fading while price continues)

### Context-Dependent Analysis
- Strong strength in uptrend = buy pullbacks
- Strong weakness at resistance = sell
- Weak strength in trend = potential reversal warning
- Strength breaking new highs = continuation likely

### Confluence Factors
- Multiple bars of strong momentum = higher confidence
- Projection extending AND momentum strong = very bullish
- Weak momentum + deep pullback = reversal likely
- HTF strength alignment = additional confluence

### Risk Management
- Reduce position size in weak strength environments
- Use tighter stops during weakening trends
- Scale into strong moves
- Exit early if strength fades unexpectedly

## Dependencies

- **Before**: Trend Definition Agent (trend direction and swings)
- **After**: Setup Scanner Agent (validates setups with strength/weakness)
- **Reference**: YTC_METHOD.md for core principles

## Key Implementation Notes

1. **Close Position is Critical**: Where price closes relative to the bar range tells the real story of supply/demand
2. **Wick Analysis**: Upper wick in uptrend = selling pressure; lower wick in downtrend = buying pressure
3. **Momentum Acceleration**: Each slightly larger bar = strength; decreasing sizes = exhaustion
4. **Projection Trends**: If swings are getting smaller, reversal risk increases
5. **Depth Ratios**: Shallow pullbacks + strong momentum = very high probability continuation
6. **Rejection Pattern**: Pin bars at S/R levels are high-confidence reversal signals
7. **Bar-to-Bar Flow**: Track how consecutive bars relate (higher highs/lows vs reversal wicks)
