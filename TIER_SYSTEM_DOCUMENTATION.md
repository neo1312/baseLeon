# Client Tier Reward System Documentation

## Overview
This system automatically manages client wallet rewards based on their tier status (Gold, Silver, Bronze). Each tier has a minimum monthly sales requirement and a corresponding wallet reward percentage applied to purchases. **Only retail (menudeo) sales earn rewards. Wholesale (mayoreo) sales do not.**

## System Configuration

### Default Tiers
| Tier | Minimum Monthly Sales | Wallet Reward % |
|------|----------------------|-----------------|
| Gold | $15,000 | 3% |
| Silver | $5,000 | 1.5% |
| Bronze | $1,500 | 0.75% |
| Regular | < $1,500 | 0% (No Rewards) |

**Note:** All values can be edited in Django Admin under "Client Tiers"

## How It Works

### 1. Tier Calculation
- **Basis:** Last 30 days of client sales (rolling window) **+ current sale being processed**
- **Automatic:** Recalculated when each saleitem is created/updated
- **Current Sale Included:** The tier is calculated WITH the current sale amount
- **Daily Accumulation:** Multiple sales on the same day accumulate for tier calculation
- **Logic:**
  - If last 30 days + current sale ≥ $15,000 → Gold tier
  - If last 30 days + current sale ≥ $5,000 → Silver tier
  - If last 30 days + current sale ≥ $1,500 → Bronze tier
  - If last 30 days + current sale < $1,500 → Regular (No tier, no rewards)

### 2. Wallet Rewards
When a retail (menudeo) sale item is completed:
1. System calculates client's tier based on **last 30 days + current sale**
2. If client qualifies for a tier, reward percentage is applied to **current sale amount only**
3. Reward is added to client's `monedero` (wallet) field
4. If client doesn't reach Bronze minimum, NO rewards are applied (0%)

**Important:** Wholesale (mayoreo) sales **never** earn rewards, regardless of tier status.

**Example - Same Day Sales:**
- Client starts day with $0 last 30 days
- **Sale 1:** Makes an $800 retail sale
  - Total for tier: $0 + $800 = $800
  - Result: Below Bronze → No reward
  - Reward on $800: $0

- **Sale 2:** Makes a $1,000 retail sale (same day, few hours later)
  - Total for tier: $800 (from Sale 1 now in DB) + $1,000 = $1,800
  - Result: Bronze tier ($1,800 ≥ $1,500) ✓
  - Reward on $1,000: $1,000 × 0.75% = $7.50
  - Client's monedero increases by $7.50

- **Sale 3:** Makes a $5,000 retail sale (same day)
  - Total for tier: $1,800 (from Sales 1+2) + $5,000 = $6,800
  - Result: Silver tier ($6,800 ≥ $5,000) ✓
  - Reward on $5,000: $5,000 × 1.5% = $75
  - Client's monedero increases by $75

- **Sale 4:** Makes a $10,000 wholesale (mayoreo) sale (same day)
  - No tier recalculation for mayoreo
  - No reward applied
  - Monedero: unchanged

### 3. Sale Type Rules
- **menudeo (Retail):** Earns tier-based wallet rewards
- **mayoreo (Wholesale):** No rewards, no tier calculation applies

### 4. Client Status Display

In Django Admin, clients display:
- **Tier/Last 30 Days Sales:** Shows current tier and total sales amount (includes today's sales)
- **Client Status:** "Active Tier Member" or "Regular Customer"
- **Monedero:** Current wallet balance (accumulated rewards)

## Admin Interface

### 1. Client List Page
Shows each client with:
- Name, Type, Phone
- **Monedero:** Current wallet balance
- **Tier / Last 30 Days Sales:** e.g., "Gold ($18,500)"
- **Client Status:** "Active Tier Member" or "Regular Customer"

### 2. Client Detail Page
Displays:
- Client information (read-only monedero)
- Current tier and status
- Wallet balance and tier info

### 3. Client Tier Configuration Page
Manage the tiers:
- **Tier Name:** Gold, Silver, Bronze
- **Minimum Monthly Sales:** Configurable threshold
- **Wallet Reward Percentage:** Configurable percentage

*Changes to tier settings apply immediately to all future sales*

### 4. Client Tier Status Page
Monitor client status:
- List all clients with their tiers
- Shows: Client name, Tier, Wallet balance, Last 30 days sales, Last calculated time
- Filter by tier or calculation date
- Search by client name or ID

## Management Commands

### Initialize Tiers
```bash
python manage.py initialize_tiers
```
- Creates default tiers (Gold, Silver, Bronze)
- Creates tier status records for all existing clients
- Run once after initial setup

### Recalculate All Tiers
```bash
python manage.py recalculate_tiers
```
- Recalculates all client tiers based on last 30 days
- Shows which clients changed tiers
- Use periodically or after system updates
- Safe to run anytime (non-destructive)

## Data Models

### ClientTier
Defines each tier configuration:
- `name`: Tier identifier (gold, silver, bronze)
- `min_monthly_sales`: Minimum sales to achieve tier
- `wallet_percentage`: Reward percentage for this tier

### ClientTierStatus
Tracks each client's current tier status:
- `client`: One-to-one relationship with Client
- `tier`: Current assigned tier (ForeignKey to ClientTier)
- `last_30_days_sales`: Calculated total from last 30 days (updated each sale)
- `last_calculated`: When tier was last updated

## Client Model Updates
The existing `Client` model's `monedero` field now accumulates wallet rewards based on tier levels from each purchase.

## Important Notes

1. **Menudeo vs Mayoreo:** Only retail (menudeo) sales earn rewards. Wholesale (mayoreo) sales are excluded.
2. **Current Sale Included:** Tier is calculated WITH the current sale amount, so a client can jump tiers on a single sale.
3. **Same Day Accumulation:** Multiple sales on the same day accumulate towards tier threshold.
4. **Regular Clients ("mostrador"):** Default client that doesn't accumulate rewards.
5. **Sporadic Clients:** Won't reach tier minimum if purchases are too sparse - no rewards applied.
6. **Tier Changes:** Effective immediately - can change up or down based on last 30 days + current sale.
7. **Manual Adjustments:** Tier status can be manually set in admin if needed.
8. **Rolling 30 Days:** Uses a true 30-day window, not calendar month.
9. **Reward Calculation:** Rewards calculated on sale total AFTER all margins and pricing logic applied.

## Example Workflow - 30 Day Rolling Window

```
Day 1: Client has $0 sales
  - Makes $2,000 retail sale
  - Tier: Bronze ($2,000 ≥ $1,500)
  - Reward: $2,000 × 0.75% = $15
  - Monedero: $15

Day 5: Client has $2,000 last 30 days
  - Makes $5,000 retail sale  
  - Total for tier: $2,000 + $5,000 = $7,000
  - Tier: Silver ($7,000 ≥ $5,000)
  - Reward: $5,000 × 1.5% = $75
  - Monedero: $15 + $75 = $90

Day 10: Client has $7,000 last 30 days
  - Makes $8,000 retail sale
  - Total for tier: $7,000 + $8,000 = $15,000
  - Tier: Gold ($15,000 ≥ $15,000)
  - Reward: $8,000 × 3% = $240
  - Monedero: $90 + $240 = $330

Day 35: Day 1 sale ($2,000) exits 30-day window
  - Client has ~$13,000 in last 30 days (without Day 1 sale)
  - Tier: Silver (still ≥ $5,000)
  - Any new sale uses Silver percentage (1.5%)

Day 36: Day 5 sale ($5,000) exits 30-day window
  - Client has ~$8,000 in last 30 days (without Days 1 & 5)
  - Tier: Silver (still ≥ $5,000)
```

## Future Enhancements
- Automated tier recalculation via scheduled task (celery beats)
- Tier history and tracking
- Custom reward percentages per client
- Bulk tier management tools
- Tier-based discount promotions
- Mayoreo volume bonuses (separate from menudeo tiers)
- Reward expiration/usage tracking
