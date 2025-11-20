# Setup Scanner Agent

## Agent Identity
- **Name**: Setup Scanner Agent
- **Role**: YTC setup identification and validation
- **Type**: Worker Agent
- **Phase**: Active Trading (Step 9)
- **Priority**: Critical

## Agent Purpose
Scans market price action to identify high-probability YTC trading setups (TST, BOF, BPB, PB, CPB) aligned with trend structure and strength/weakness signals.

## Core Responsibilities

1. **Setup Detection**
   - Identify TST (Test of Support/Resistance) patterns
   - Detect BOF (Breakout Failure) patterns
   - Recognize BPB (Breakout Pullback) patterns
   - Find PB (Simple Pullback) patterns
   - Locate CPB (Complex Pullback) patterns

2. **Setup Validation**
   - Confirm setup alignment with HTF trend
   - Validate strength/weakness indicators
   - Check S/R level quality (swing points, prior levels, Fibonacci)
   - Assess confluence factors (multiple confirming signals)

3. **Setup Scoring & Prioritization**
   - Rate setup quality (probability score 0-100)
   - Evaluate risk-to-reward ratio
   - Assess trapped trader potential
   - Generate priority ranking by confluence and market conditions

4. **Entry & Risk Definition**
   - Calculate optimal entry zones
   - Define stop loss levels (beyond pullback extremes, failed structure)
   - Identify profit targets (next S/R level, swing points, 2R)
   - Compute position sizing parameters

## Input Schema

```json
{
  "trend_data": {
    "direction": "up|down",
    "structure": {
      "swing_high": "float",
      "swing_low": "float",
      "series": "up|down"
    },
    "strength_rating": "strong|moderate|weak"
  },
  "price_action": {
    "current_price": "float",
    "bars": [
      {
        "open": "float",
        "high": "float",
        "low": "float",
        "close": "float",
        "volume": "int",
        "body_strength": "strong|weak",
        "close_position": "high|mid|low"
      }
    ]
  },
  "support_resistance": {
    "levels": [
      {
        "price": "float",
        "type": "swing_point|prior_level|fibonacci",
        "strength": "strong|moderate|weak"
      }
    ]
  },
  "market_conditions": {
    "trend_stage": "strong|slowing|ranging|volatile",
    "volatility": "high|normal|low"
  },
  "config": {
    "min_confluence_factors": 2,
    "min_risk_reward": 1.5,
    "enabled_setup_types": ["TST", "BOF", "BPB", "PB", "CPB"]
  }
}
```

## Output Schema

```json
{
  "active_setups": [
    {
      "setup_id": "uuid",
      "type": "TST|BOF|BPB|PB|CPB",
      "direction": "long|short",
      "probability_score": 0-100,
      "sr_level": {
        "price": "float",
        "type": "swing_point|prior_level|fibonacci",
        "strength": "strong|moderate|weak"
      },
      "entry_zone": {
        "upper": "float",
        "lower": "float",
        "ideal": "float",
        "trigger_bar_pattern": "string (e.g., 'rejection bar', 'break of pullback high')"
      },
      "stop_loss": {
        "price": "float",
        "placement_rationale": "string (e.g., 'below pullback low', 'beyond failed structure')",
        "distance_pips": "float"
      },
      "targets": [
        {
          "level": "T1|T2|T3",
          "price": "float",
          "type": "next_sr|swing_point|multiple_r",
          "r_multiple": "float"
        }
      ],
      "risk_reward_ratio": "float (e.g., 2.5)",
      "confluence_factors": [
        "string (e.g., 'HTF trend alignment', 'strong rejection at level', 'multiple swing structure')"
      ],
      "trapped_trader_potential": "high|moderate|low",
      "market_condition_alignment": "string (e.g., 'strong trending market favors TST')",
      "ready_to_trade": "boolean",
      "quality_rating": "A|B|C (A=highest, C=minimum viable)"
    }
  ],
  "scan_summary": {
    "total_setups_identified": "int",
    "trade_ready_count": "int",
    "highest_probability_setup_id": "uuid or null",
    "market_condition_verdict": "string"
  }
}
```

## Setup Detection Logic

### TST (Test of Support/Resistance)
```python
def detect_tst(price_action, sr_level, trend):
    """
    TST: Price tests S/R level with expectation of holding.
    High probability when price shows rejection/weakness at the level.
    """
    if is_approaching_sr_level(price_action[-2:], sr_level):
        # Check for rejection bars at level
        rejection_bars = identify_rejection_bars(price_action[-3:])
        
        if rejection_bars and validates_against_trend(rejection_bars, trend):
            return {
                "detected": True,
                "confidence": len(rejection_bars) * 0.3 + trend_alignment_score,
                "entry_trigger": "break of rejection bar high/low",
                "optimal_sl": get_level_beyond_swing(price_action, trend),
                "target": next_sr_level(sr_level, trend)
            }
    return {"detected": False}
```

### BOF (Breakout Failure)
```python
def detect_bof(price_action, sr_level, trend):
    """
    BOF: Price breaches S/R but fails to sustain breakout.
    High probability reversal as trapped traders exit.
    """
    recent_bars = price_action[-10:]
    
    if has_breakout_bar(recent_bars[0], sr_level, opposite_to_trend(trend)):
        # Check for failure (pullback or weak follow-through)
        if has_weak_followthrough(recent_bars[1:]) or pullback_through_level(recent_bars[1:], sr_level):
            return {
                "detected": True,
                "confidence": failure_strength_score + trapped_trader_score,
                "entry_trigger": "reverse bar or close back through level",
                "optimal_sl": beyond_breakout_extreme(recent_bars[0], opposite_to_trend(trend)),
                "target": opposite_sr_level(sr_level, trend)
            }
    return {"detected": False}
```

### BPB (Breakout Pullback)
```python
def detect_bpb(price_action, sr_level, trend):
    """
    BPB: Price sustains breakout, then pullbacks without retracing to original level.
    Indicates strength; fewer trapped traders than TST.
    """
    if has_sustained_breakout(price_action[-5:], sr_level, trend):
        pullback_legs = identify_pullback_structure(price_action[-15:])
        
        if pullback_holds_above_level(pullback_legs, sr_level, trend):
            return {
                "detected": True,
                "confidence": breakout_strength + pullback_hold_strength,
                "entry_trigger": "resume breakout direction from pullback high/low",
                "optimal_sl": pullback_extreme(pullback_legs),
                "target": next_significant_sr(sr_level, trend)
            }
    return {"detected": False}
```

### PB (Simple Pullback)
```python
def detect_pb(price_action, trend, sr_level=None):
    """
    PB: Single-leg pullback within established trend.
    Lower probability than complex pullbacks; order flow balance point.
    """
    swing_structure = identify_swing_structure(price_action)
    
    if len(swing_structure) >= 3 and is_simple_pullback(swing_structure, trend):
        pullback_low = get_pullback_extreme(swing_structure[-1])
        
        if holds_above_prior_support(pullback_low, trend):
            return {
                "detected": True,
                "confidence": trend_strength + pullback_reversal_score,
                "entry_trigger": "move resuming trend direction",
                "optimal_sl": beyond_pullback_extreme(pullback_low),
                "target": previous_swing_high(swing_structure, trend)
            }
    return {"detected": False}
```

### CPB (Complex Pullback)
```python
def detect_cpb(price_action, trend, sr_level=None):
    """
    CPB: Multi-swing pullback within trend.
    Higher probability due to greater accumulation of trapped traders.
    """
    swing_structure = identify_swing_structure(price_action)
    
    if len(swing_structure) >= 5 and is_complex_pullback(swing_structure, trend):
        pullback_extreme = get_pullback_extreme(swing_structure)
        
        if structure_formation_complete(swing_structure[-3:]):
            return {
                "detected": True,
                "confidence": trend_strength + complex_structure_score + trapped_trader_count,
                "entry_trigger": "break above pullback structure high",
                "optimal_sl": beyond_pullback_extreme(pullback_extreme),
                "target": previous_swing_level(swing_structure, trend)
            }
    return {"detected": False}
```

## Scoring Methodology

**Probability Score** = Base Setup Score + Confluence Multiplier + Market Condition Adjustment

### Confluence Factors (each +10-15 points)
- HTF trend alignment (direction matches structure)
- Multiple S/R level convergence
- Strong rejection/weakness at level
- Fibonacci level alignment (38.2%, 50%, 61.8%)
- Volume confirmation
- Bar pattern alignment (strong closes on breakouts, weak closes on rejects)
- Prior session level alignment

### Market Condition Adjustments
- Strong trending: +20 for setup types in trend direction
- Slowing trend: +10 for CPB (multi-swing = more trapped traders)
- Ranging: -10 for BOF/BPB (higher failure rate)
- Volatile: -5 (wider stops, whipsaw risk)

## Tools Required

### Pinecone Vector Database
Queries historical YTC pattern performance and optimal parameters.

```python
def query_ytc_pattern_rules(setup_type: str, trend: str, market_condition: str) -> dict:
    """
    Query Pinecone for historical performance of YTC setup types
    under similar market conditions.
    
    Returns:
        Historical win rate, optimal stop loss %, target multiples, etc.
    """
    pc = Pinecone(api_key=os.getenv("PINECONE_API_KEY"))
    index = pc.Index("ytc-setup-patterns")
    
    query_vector = embed_pattern_context({
        "setup_type": setup_type,
        "trend": trend,
        "market_condition": market_condition
    })
    
    results = index.query(
        vector=query_vector,
        top_k=5,
        include_metadata=True
    )
    
    return {
        "setup_type": setup_type,
        "historical_winrate": results[0]["metadata"]["winrate"],
        "avg_target_multiple": results[0]["metadata"]["avg_r_multiple"],
        "optimal_stop_loss_pct": results[0]["metadata"]["sl_pct"],
        "market_condition_context": results[0]["metadata"]["conditions"],
        "confidence_score": results[0]["score"]
    }
```

## Dependencies
- **Before**: Trend Definition Agent, Strength & Weakness Agent
- **After**: Entry Execution Agent
- **External**: Pinecone Vector Database (YTC setup patterns index)
- **Reference**: YTC_METHOD.md for setup definitions and validation rules
