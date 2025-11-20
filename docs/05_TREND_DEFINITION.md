# Trend Definition Agent (Trading Timeframe)

## Agent Identity

- **Name**: Trend Definition Agent
- **Role**: Trading timeframe trend analysis and swing structure identification
- **Type**: Worker Agent
- **Phase**: Session Open (Step 7) + Continuous
- **Priority**: Critical

## Agent Purpose

Identifies trend direction and structure on the trading timeframe (15min) using YTC's precise swing analysis methodology. Establishes the foundation for all setup identification by determining whether market is in uptrend, downtrend, or sideways movement.

## Core Responsibilities

1. **Swing Highs and Lows Detection**
   - Identify significant swing highs (price higher on both sides)
   - Identify significant swing lows (price lower on both sides)
   - Track sequence of swings for trend determination
   - Distinguish between minor and significant swings
   - Update leading swing levels as new structure forms

2. **Trend Classification**
   - **Uptrend**: Series of higher highs (HH) and higher lows (HL)
   - **Downtrend**: Series of lower highs (LH) and lower lows (LL)
   - **Sideways**: Price movement within range without clear directional bias
   - Assign confidence score based on number of confirmed swings
   - Track trend inception timestamp

3. **Trend Integrity & Structure Monitoring**
   - Monitor for structure breaks (LL in uptrend, HH in downtrend)
   - Detect leading swing violations (potential reversal signals)
   - Track trend strength (strong vs weakening vs reversal)
   - Identify potential reversal warnings
   - Count structure breaks and reversal strength

4. **Higher Timeframe Context**
   - Reference HTF (30min/1H) support/resistance levels
   - Align trading timeframe trend with HTF bias
   - Identify when TF trends conflict with HTF structure
   - Use HTF levels as confluence for swing points

5. **Dynamic Bar-by-Bar Updates**
   - Monitor each new bar for trend changes
   - Adjust trend classification as new information emerges
   - Detect weakening trends before reversal
   - Update leading swings as structure evolves

## Trend Definition Methodology

### Swing Highs and Lows

**Swing High (SH)**:
- Price bar where the high is higher than the bars on both sides
- Represents resistance/potential turning point
- In uptrends: each SH should be higher than the previous SH
- In downtrends: each SH should be lower than the previous SH

**Swing Low (SL)**:
- Price bar where the low is lower than the bars on both sides
- Represents support/potential turning point
- In uptrends: each SL should be higher than the previous SL
- In downtrends: each SL should be lower than the previous SL

### Uptrend Definition

**Characteristics**:
- Series of Higher Highs (HH) - each swing high is above the previous swing high
- Series of Higher Lows (HL) - each swing low is above the previous swing low
- Price consistently making new highs
- Each pullback finds support at higher levels

**Structure Integrity**:
- Uptrend intact as long as HL pattern continues
- Uptrend weakens when a Lower Low (LL) forms (breaks HL pattern)
- Uptrend reverses when price breaks below the last significant Swing Low (leading swing)
- Strength rating: number of confirmed HH/HL pairs

**Example**:
```
SH (1000) → SL (950) → SH (1050) → SL (980) → SH (1100) → [Uptrend Intact]
HH        HL         HH        HL         HH
```

### Downtrend Definition

**Characteristics**:
- Series of Lower Highs (LH) - each swing high is below the previous swing high
- Series of Lower Lows (LL) - each swing low is below the previous swing low
- Price consistently making new lows
- Each bounce finds resistance at lower levels

**Structure Integrity**:
- Downtrend intact as long as LH pattern continues
- Downtrend weakens when a Higher High (HH) forms (breaks LH pattern)
- Downtrend reverses when price breaks above the last significant Swing High (leading swing)
- Strength rating: number of confirmed LH/LL pairs

**Example**:
```
SH (1000) → SL (950) → SH (950) → SL (920) → SH (920) → [Downtrend Intact]
LH        LL        LH        LL         LH
```

### Sideways/Range Trend

**Characteristics**:
- Price moves between defined support and resistance without clear directional bias
- Alternating highs and lows at similar levels
- No consistent pattern of HH/HL or LH/LL
- Potential for both upside and downside moves

**Detection**:
- Range width is narrow relative to recent volatility
- Swing highs cluster at similar prices
- Swing lows cluster at similar prices
- No clear break of previous structure in either direction

### Trend Strength Assessment

**Strong Trend**:
- 3+ confirmed swings in primary direction (HH/HL or LH/LL)
- Each swing represents larger move than previous
- Limited pullbacks against trend
- Volatility increasing in trend direction

**Weakening Trend**:
- Structure breaks starting to appear (LL in uptrend, HH in downtrend)
- Swing sizes decreasing
- Pullbacks becoming deeper relative to swings
- Price struggling to make new highs/lows

**Reversal Imminent**:
- Significant structure break confirmed (leading swing broken)
- Multiple failed attempts to continue trend
- Divergence between price and momentum
- Volume shifting direction

## Input Schema

```json
{
  "market_data": {
    "symbol": "string",
    "timeframe": "15min",
    "lookback_bars": 50,
    "bars": [
      {
        "timestamp": "ISO 8601",
        "open": "float",
        "high": "float",
        "low": "float",
        "close": "float",
        "volume": "int"
      }
    ]
  },
  "higher_timeframe_context": {
    "htf_timeframe": "30min",
    "htf_trend_direction": "up|down|sideways",
    "htf_resistance": "float",
    "htf_support": "float",
    "htf_swing_high": "float",
    "htf_swing_low": "float"
  }
}
```

## Output Schema

```json
{
  "trend_analysis": {
    "direction": "uptrend|downtrend|sideways",
    "confidence": "float 0-1",
    "strength_rating": "strong|moderate|weak|reversal_warning",
    "since_timestamp": "ISO 8601",
    "bar_count_in_trend": "integer"
  },
  "swing_structure": {
    "swing_highs": [
      {
        "price": "float",
        "timestamp": "ISO 8601",
        "bar_index": "integer",
        "is_leading": "boolean",
        "is_broken": "boolean"
      }
    ],
    "swing_lows": [
      {
        "price": "float",
        "timestamp": "ISO 8601",
        "bar_index": "integer",
        "is_leading": "boolean",
        "is_broken": "boolean"
      }
    ],
    "current_leading_swing_high": "float",
    "current_leading_swing_low": "float"
  },
  "structure_integrity": {
    "structure_intact": "boolean",
    "structure_breaks_detected": "integer",
    "reversal_warning": "boolean",
    "last_structure_break_timestamp": "ISO 8601 or null",
    "structure_break_description": "string (e.g., 'LL formed in uptrend')"
  },
  "hft_alignment": {
    "tf_trend_aligns_with_htf": "boolean",
    "alignment_description": "string (e.g., 'Trading TF uptrend aligned with HTF uptrend')",
    "potential_conflict": "string or null"
  }
}
```

## Trend Definition Algorithm

### Core Logic

```python
def define_trend(bars: list[Bar], htf_context: dict) -> TrendAnalysis:
    """
    Define trend using YTC swing analysis methodology.
    
    Steps:
    1. Identify all swing highs and lows
    2. Determine sequence pattern (HH/HL vs LH/LL vs Range)
    3. Assess trend strength (number of confirmed swings)
    4. Check for structure breaks (weakening/reversal)
    5. Validate against HTF bias
    """
    
    # Step 1: Identify swings
    swings = identify_swings(bars)
    
    # Step 2: Classify trend type
    if has_series_higher_highs_and_lows(swings):
        direction = "uptrend"
        confidence = len([s for s in swings if s.is_higher_high]) * 0.2
    elif has_series_lower_highs_and_lows(swings):
        direction = "downtrend"
        confidence = len([s for s in swings if s.is_lower_high]) * 0.2
    else:
        direction = "sideways"
        confidence = 0.5
    
    # Step 3: Assess trend strength
    structure_breaks = count_structure_breaks(swings, direction)
    reversal_warning = structure_breaks > 0 and check_leading_swing_breach(swings)
    
    if structure_breaks == 0:
        strength = "strong"
    elif structure_breaks == 1:
        strength = "weakening"
    else:
        strength = "reversal_warning" if reversal_warning else "weakening"
    
    # Step 4: Check HTF alignment
    tf_aligned_with_htf = check_alignment(direction, htf_context)
    
    return TrendAnalysis(
        direction=direction,
        confidence=min(1.0, confidence),
        strength_rating=strength,
        swings=swings,
        tf_aligned_with_htf=tf_aligned_with_htf
    )
```

### Swing Identification

```python
def identify_swings(bars: list[Bar]) -> list[Swing]:
    """
    Identify swing highs and lows.
    
    A swing high requires: bar high > left bar high AND bar high > right bar high
    A swing low requires: bar low < left bar low AND bar low < right bar low
    """
    swings = []
    
    for i in range(1, len(bars) - 1):
        current = bars[i]
        prev = bars[i - 1]
        next_bar = bars[i + 1]
        
        # Swing high
        if current.high > prev.high and current.high > next_bar.high:
            swings.append(Swing(
                type="swing_high",
                price=current.high,
                timestamp=current.timestamp,
                bar_index=i
            ))
        
        # Swing low
        elif current.low < prev.low and current.low < next_bar.low:
            swings.append(Swing(
                type="swing_low",
                price=current.low,
                timestamp=current.timestamp,
                bar_index=i
            ))
    
    return swings
```

### Structure Break Detection

```python
def detect_structure_breaks(swings: list[Swing], trend: str) -> int:
    """
    Detect structure breaks:
    - In uptrend: check for Lower Low (LL) - breaks HL pattern
    - In downtrend: check for Higher High (HH) - breaks LH pattern
    """
    breaks = 0
    
    if trend == "uptrend":
        # Look for decreasing swing lows (LL)
        swing_lows = [s for s in swings if s.type == "swing_low"]
        for i in range(1, len(swing_lows)):
            if swing_lows[i].price < swing_lows[i-1].price:
                breaks += 1
    
    elif trend == "downtrend":
        # Look for increasing swing highs (HH)
        swing_highs = [s for s in swings if s.type == "swing_high"]
        for i in range(1, len(swing_highs)):
            if swing_highs[i].price > swing_highs[i-1].price:
                breaks += 1
    
    return breaks
```

## Implementation Considerations

### Bar-by-Bar Analysis
- Monitor each new bar for swing formation
- Update trend classification immediately when new swings form
- Adjust leading swing levels as structure evolves
- Track when leading swings are threatened (near break level)

### Multiple Timeframe Alignment
- Identify HTF trend (30min or 1H)
- Compare trading timeframe trend with HTF
- Setups in direction of HTF trend have higher probability
- Flag when TF trend conflicts with HTF (potential reversal zone)

### Dynamic Adjustments
- If trend definition is unclear, default to recent price action bias
- Adjust trend as new information emerges
- Monitor for transition from one trend to another
- Document when trend changes (for review and learning)

### Confluence Factors
- Strong trend = 3+ confirmed swings in same direction
- HTF alignment = higher probability
- Strength/weakness indicators = confirmation
- Volume alignment = additional confluence

## Application to Setup Selection

Based on trend definition, optimal setup types vary:

### In Strong Uptrend
- **Best**: PB (pullback in trend), CPB (complex pullback), BPB (breakout pullback)
- **Avoid**: BOF setups (less probability against trend)
- Confluence: HTF also uptrend, rejection at support

### In Strong Downtrend
- **Best**: PB short, CPB short, BPB short
- **Avoid**: BOF setups (less probability against trend)
- Confluence: HTF also downtrend, rejection at resistance

### In Weakening Trend
- **Good**: CPB (multi-swing = more trapped traders)
- **Watch**: Structure breaks indicate potential reversal
- **Caution**: Reduce position sizing, tighter stops

### In Sideways Market
- **Best**: TST at range boundaries, mean reversion
- **Avoid**: BOF/BPB (high failure rate in ranges)
- **Opportunity**: Both long and short setups valid

## Dependencies

- **Before**: Market Structure Agent (HTF context)
- **After**: Strength & Weakness Agent (validate bar patterns at swings)
- **Continuous**: Updates with each new bar
- **Reference**: YTC_METHOD.md for core principles

## Key Implementation Notes

1. **Leading Swings**: Track the most recent swing high/low in each direction - these are critical levels for trend breaks
2. **Structure Integrity**: Maintain count of structure breaks (LL in uptrend, HH in downtrend) as early warning
3. **Confidence Scoring**: Base on number of confirmed swings (each adds ~0.2 to confidence, max 1.0)
4. **Reversal Warnings**: Trigger when leading swing is broken AND structure has multiple breaks
5. **HTF Context**: Always reference higher timeframe to avoid trading against major structure
