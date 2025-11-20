# YTC Trading Method

## Overview

The YTC (Your Trading Coach) trading method is a **price action-based strategy** developed by Lance Beggs. It focuses on understanding market structure, identifying areas of strength and weakness, and trading in the direction of strength while fading weakness. The methodology emphasizes trading setups at key support and resistance (S/R) levels and within trends, aiming to capitalize on trapped traders and shifts in order flow.

## Core Principles

### 1. Market Structure Analysis
- Begin with analyzing market structure and identifying the likely future trend direction
- Monitor price action bar by bar to update the bias as new information emerges
- Identify key support/resistance levels where traders congregate
- Understand the flow of orders as traders make decisions at stress points

### 2. Expectancy Formula
The strategy is designed to achieve **positive expectancy** through:
- **High win percentage**: Maximizing winning trades relative to losing trades
- **Favorable win/loss ratio**: Larger average wins than average losses (R:R ratio)
- **Early entries**: Getting into positions before major moves
- **Setups designed for immediate price movement**: Identifying high-probability reversals
- **Active trade management**: Protecting profits and limiting losses

**Formula**: Expectancy = (Win% × Avg Win) - (Loss% × Avg Loss)

### 3. Order Flow and Stress Points
The approach identifies areas where traders experience stress and make trading decisions:
- **Trapped traders**: Traders forced to exit positions at a loss
- **Stress points**: Key S/R levels where traders congregate
- **Net order flow**: Direction of forced exits and market-moving trades
- **Optimal timing**: Act before or with these traders to profit from resultant order flow

### 4. Fading Weakness and Trapped Traders
- Trade against weakness to capture reversal order flow
- Capitalize on trapped traders who are forced to liquidate positions
- Identify where order flow is likely to reverse
- Look for setups where weakness precedes reversal

## Market Analysis Workflow

```
┌──────────────────────────┐
│  Identify Market Trend   │
│  (HTF Structure)         │
└────────────┬─────────────┘
             │
             ▼
┌──────────────────────────┐
│  Locate S/R Levels       │
│  (Swing Points, Prior    │
│   Session Levels, Pivot) │
└────────────┬─────────────┘
             │
             ▼
┌──────────────────────────┐
│  Identify Strength &     │
│  Weakness Areas          │
│  (Breakouts, Reversals)  │
└────────────┬─────────────┘
             │
             ▼
┌──────────────────────────┐
│  Scan for Setups         │
│  (TST, BOF, BPB, PB, CPB)│
└────────────┬─────────────┘
             │
             ▼
┌──────────────────────────┐
│  Validate Setup          │
│  (Confluence, Structure, │
│   Trade Management)      │
└────────────┬─────────────┘
             │
             ▼
┌──────────────────────────┐
│  Execute Trade           │
│  (Entry, SL, Targets)    │
└──────────────────────────┘
```

## Trading Setup Types

### 1. TST (Test of Support or Resistance)

**Definition**: Price tests a support or resistance level that is expected to hold.

**Characteristics**:
- Price approaches S/R level from the expected direction
- Shows weakness into the area (pullback bars, rejection)
- Traders entering late are likely trapped if price reverses
- High probability when price shows strong rejection at the level

**Setup Rules**:
- Identify key S/R level from higher timeframe analysis
- Wait for price to test the level
- Look for rejection/weakness into the level
- Entry typically at reversal bar or break of the swing low/high formed at S/R
- Stop loss: Below the swing low formed at S/R (or opposite for short)
- Target: Next S/R level or swing point in the direction of strength

**Example - Long TST**:
```
Uptrend established with support level at 2450
Price pulls back to test 2450
At 2450, price shows 2-3 rejection bars (bodies above, wicks below)
Enter on break above the rejection bar high
SL: Below the swing low of the test pattern
Target: Resistance at 2500 or next swing high
```

### 2. BOF (Breakout Failure)

**Definition**: Price breaches a support or resistance level but fails to sustain the breakout, leading to a reversal.

**Characteristics**:
- Initial breakout attracts breakout traders
- Insufficient follow-through indicates trapped traders
- Creates a failure pattern at the S/R level
- Often results in violent reversals as trapped traders exit

**Setup Rules**:
- Identify S/R level and initial breakout attempt
- Watch for failure to sustain (pullback back through level or weak momentum)
- Enter on reversal bar formation or close back through the level
- Stop loss: Beyond the failed breakout high/low
- Target: Opposite S/R level or swing point

**Example - Short BOF**:
```
Resistance at 2550 with downtrend structure
Price rallies above 2550 on high volume
Momentum fails within 5-10 bars (no continued up move)
Price pulls back to test 2550 from above
Enter short on close back below 2550
SL: Above the failed breakout high
Target: Previous support at 2500 or lower
```

### 3. BPB (Breakout Pullback)

**Definition**: Price breaches a support or resistance level and holds, followed by a pullback before continuing in the breakout direction.

**Characteristics**:
- Initial breakout is sustained (opposite of BOF)
- Pullback occurs but doesn't retrace to the original level
- Indicates strength in the breakout direction
- Fewer trapped traders than TST (success filter)

**Setup Rules**:
- Identify S/R level and successful breakout (strong momentum)
- Wait for pullback but expect it to hold above/below the level
- Enter on resumption of move in breakout direction
- Stop loss: At or just beyond the S/R level
- Target: Next significant S/R or swing point in breakout direction

**Example - Long BPB**:
```
Support at 2450 with uptrend
Price breaks above 2550 resistance on strong volume
Pullback to around 2510 (not back to 2550)
Pullback holds above 2500 support area
Bounce from pullback low, resume uptrend
Enter long as price breaks above pullback high
SL: Below the pullback low
Target: 2600 or next resistance level
```

### 4. PB (Simple Pullback)

**Definition**: A single-leg pullback within a trend, offering an opportunity to trade in the direction of the trend.

**Characteristics**:
- One swing leg against the primary trend
- Represents an order flow balance point
- Lower probability than complex pullbacks
- Often precedes continuation of the larger trend

**Setup Rules**:
- Confirm primary trend direction (higher timeframe)
- Identify pullback leg (one swing low in uptrend, high in downtrend)
- Wait for reversal at pullback area
- Enter on move resuming trend direction
- Stop loss: Beyond pullback extreme
- Target: Previous swing high/low or next level

**Example - Long PB**:
```
Established uptrend with clear swing points
Price pulls back one leg (one lower swing low)
Pullback shows weakness but holds above key support
Price reverses and breaks above pullback high
Enter long on break above pullback high
SL: Below pullback low
Target: Previous swing high or higher
```

### 5. CPB (Complex Pullback)

**Definition**: A multi-swing or extended duration pullback within a trend, often providing a higher probability setup due to greater trapped trader order flow.

**Characteristics**:
- Multiple swing legs against the primary trend
- Extended pullback creates more trapped traders
- Higher probability due to accumulation of order flow
- More time for traders to enter on wrong side

**Setup Rules**:
- Confirm primary trend direction
- Identify multi-swing pullback pattern (2+ legs)
- Wait for structure completion and reversal
- Enter on move resuming main trend direction
- Stop loss: Beyond the pullback extreme
- Target: Previous swing or key S/R level

**Example - Long CPB**:
```
Strong uptrend established
Price creates 3-swing pullback (Lower high, lower low, lower high)
Multiple traders trapped shorting the pullback
Finally, price breaks structure and resumes up
Enter long on break above pullback structure high
SL: Below the lowest point of pullback pattern
Target: Previous swing high or resistance above
```

## Multiple Timeframe Analysis

YTC emphasizes analyzing market structure across timeframes:

### Hierarchy
1. **Higher Timeframe (HTF)** - 4H/Daily
   - Identify primary trend direction
   - Locate major S/R levels
   - Define overall structure

2. **Trading Timeframe** - 1H/30min
   - Identify setups within the HTF trend
   - Confirm entry signals
   - Validate S/R levels

3. **Action Timeframe** - 15min/5min
   - Fine-tune entry timing
   - Confirm bar-by-bar weakness/strength
   - Define exact entry levels

### Application
- **With trend**: Look for pullback setups in direction of HTF trend
- **Against trend**: Only trade with confluence of multiple confluence factors
- **Confirmation**: HTF setup + TF setup + Action TF confirmation = High probability

## Key S/R Level Types

### 1. Swing Points
- **Swing High**: Higher highs on both sides (resistance)
- **Swing Low**: Higher lows on both sides (support)
- Detected using multiple timeframe analysis
- Recent swings more relevant than older ones

### 2. Prior Session Levels
- **Prior Open/Close**: Previous session's open and close
- **Prior High/Low**: Highest and lowest of prior session
- Often act as support/resistance in subsequent sessions
- More relevant during London/US overlap sessions

### 3. Fibonacci Retracements
- **61.8%**: Most significant retracement level
- **50%**: Moderate retracement
- **38.2%**: Minor retracement
- Applied to recent swing extremes

### 4. Psychological Levels
- Round numbers (X000, X500)
- Previous significant structure
- Areas where clusters of trades enter

## Strength and Weakness Indicators

### Strength
- **Strong closes**: Bars closing near the high
- **Large body**: Significant move within the bar
- **Momentum bars**: Continuing in direction with volume
- **Break of structure**: Beyond prior swing points
- **Failed rejection**: Price doesn't reverse at S/R

### Weakness
- **Weak closes**: Bars closing near the low
- **Rejection bars**: Open strong, close weak (pin bars, reversals)
- **Slowing momentum**: Decreasing bar size
- **Pullback formation**: Moving against primary trend
- **Rejection at S/R**: Clear reversal at key level

## Order Flow Concepts

### Trapped Traders
- Long traders trapped when price falls below their entry
- Short traders trapped when price rises above their entry
- Forced exits create order flow that continues the move
- Higher number of trapped traders = Higher probability reversal

### Stress Points
- Price levels where trapped traders accumulate
- S/R levels, breakouts, failed setups
- Traders make emotional decisions at stress points
- Order flow accelerates at stress points

### Trade Flow Direction
- **Up**: More buying pressure (strength, breakouts)
- **Down**: More selling pressure (weakness, reversals)
- **Balanced**: Consolidation, no clear direction (avoid trading)

## Risk Management

### Position Sizing
- Fixed risk per trade (e.g., 2% of account)
- Calculate based on entry to stop loss distance
- Adjust for volatility

**Formula**: Position Size = (Risk $ / Risk per Unit) × Units

### Stop Loss Placement
- **Below pullback low** (long pullback setup)
- **Above pullback high** (short pullback setup)
- **Beyond failed structure** (breakout failure)
- **Below 20-period SMA** (alternative for trends)

### Profit Taking
- **Target 1**: At nearest S/R level
- **Target 2**: At next swing point or 2R profit
- **Trailing stop**: Once 1R profit locked in
- **Scale out**: Take partial profit, trail remainder

### Risk-to-Reward Ratio
- Minimum 1:1.5 (for high win% setups)
- Target 1:2 to 1:3 (for low win% setups)
- Higher R:R compensates for lower win percentage

## Market Conditions and Setup Selection

### Trending Market
- **Best setups**: TST, PB, CPB, BPB (in trend direction)
- **Avoid**: Setups against trend unless exceptional confluence
- **Focus**: Pull back entries within trend

### Slowing Trend
- **Best setups**: CPB (multiple swings = trapped traders)
- **Watch for**: Reversal pattern formations
- **Caution**: Reduces probability vs. strong trend

### Sideways/Range Market
- **Best setups**: TST at range boundaries
- **Avoid**: Breakout setups (high failure rate)
- **Focus**: Mean reversion from extremes

### Volatile Market
- **Adjust**: Larger stop losses, wider entry zones
- **Watch for**: Whipsaws at S/R levels
- **Opportunity**: Higher potential reward moves

## Implementation in LangGraph System

### Agent Workflow
```
1. Market Analysis Agent
   └─> Identify trend, S/R levels, structure

2. Strength & Weakness Agent
   └─> Evaluate trading conditions, trapped traders

3. Setup Scanner Agent
   └─> Identify TST, BOF, BPB, PB, CPB patterns
   └─> Query YTC Assistant for pattern validation

4. Entry Execution Agent
   └─> Confirm entry signals
   └─> Calculate stop loss and targets
   └─> Place entry order

5. Trade Management Agent
   └─> Monitor position
   └─> Manage stops
   └─> Execute take profit targets
```

### Setup Validation Checklist
- [ ] HTF trend confirmed (structure aligned)
- [ ] S/R level identified (swing point, prior level, or Fib)
- [ ] Setup type recognized (TST, BOF, BPB, PB, CPB)
- [ ] Strength/weakness confirmed (bar analysis)
- [ ] Confluence factors present (multiple signals)
- [ ] Risk-to-reward acceptable (≥ 1:1.5)
- [ ] Position size calculated
- [ ] Stop loss defined
- [ ] Targets identified

## Key Takeaways

1. **Price action first**: Rely on bar analysis, not indicators
2. **Structure matters**: Higher timeframe structure guides lower timeframe trades
3. **Trapped traders**: Identify where traders are forced to exit
4. **Order flow**: Act before or with the trapped trader order flow
5. **Setup types**: Master the 5 setups (TST, BOF, BPB, PB, CPB)
6. **Risk management**: Protect capital with proper stop losses and position sizing
7. **Confluence**: High probability comes from multiple confirming signals
8. **Discipline**: Follow the rules, avoid emotional trading

## References

- YTC Price Action Trader - Lance Beggs
- Price Action Breakdown - Laurentiu Damir
- The Art and Science of Technical Analysis - Adam Grimes

## Related Documentation

- [Market Structure Agent](./03_MARKET_STRUCTURE.md)
- [Trend Definition Agent](./02_TREND_DEFINITION.md)
- [Setup Scanner Agent](./07_SETUP_SCANNER.md)
- [YTC Trading Assistant](./YTC_ASSISTANT.md)
