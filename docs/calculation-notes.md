# Calculation limits and proposed changes

These changes are proposals, not edits verified in the shipped PBIX. Apply and check them in Power BI Desktop before treating them as implemented.

These are problems in the report as it stands, with the DAX to fix each one.

**1. Year-to-date resets in January, but the financial year starts in July.** `TOTALYTD` defaults to a calendar year, while the report's slicers and quarters use the Australian July–June financial year. So in August 2016 the report shows $22.4M year to date; the correct financial-year figure is $6.6M. The fix is to give the year-end date:

```dax
Revenue YTD = TOTALYTD([Revenue Measure], Dates[Date], "6/30")
```

**2. The price simulator can't show the trade-off it exists for.**
- Price and volume are separate sliders, and the volume response has to be guessed and set by hand. Nothing ties a price rise to lost sales.
- It shows revenue only. Costs don't change with price, so profit is what moves most.

A version that adds an elasticity parameter (how much volume falls for each 1% price rise) and reports profit:

```dax
Elasticity         = SELECTCOLUMNS(GENERATESERIES(-3, 0, 0.1), "Elasticity", [Value])   -- parameter table
Elasticity Value   = SELECTEDVALUE(Elasticity[Elasticity], -1)
Simulated units    = SUMX(Sales, Sales[Total Units] * POWER(1 + [Price Change % Value], [Elasticity Value]))
Simulated revenue  = SUMX(Sales, Sales[Sale Price] * (1 + [Price Change % Value])
                               * Sales[Total Units] * POWER(1 + [Price Change % Value], [Elasticity Value]))
Simulated profit   = SUMX(Sales, (Sales[Sale Price] * (1 + [Price Change % Value]) - Sales[Cost Price])
                               * Sales[Total Units] * POWER(1 + [Price Change % Value], [Elasticity Value]))
```

Worked on this data, a price rise helps profit far more than revenue, and how much depends on how customers respond:

| Price change | Customers' response (elasticity) | Revenue | Profit |
| --- | --- | ---: | ---: |
| +5% | none (0) | +5.0% | +11.8% |
| +5% | proportional (−1) | 0.0% | +6.4% |
| +5% | strong (−1.5) | −2.4% | +3.9% |
| +10% | none (0) | +10.0% | +23.5% |
| +10% | proportional (−1) | 0.0% | +12.3% |
| +10% | strong (−1.5) | −4.7% | +7.1% |

**3. The revenue target is arbitrary.** `Target Revenue` is last month's revenue plus 5%. Retail sales are seasonal, so for December or January that target says more about the calendar than about performance. Using the same month last year plus a growth rate is fairer, with the rate as a what-if parameter:

```dax
Target growth       = SELECTCOLUMNS(GENERATESERIES(0, 0.2, 0.01), "Target growth", [Value])   -- parameter table
Target Revenue      = [Revenue LY] * (1 + SELECTEDVALUE('Target growth'[Target growth], 0.05))
```

**4. Manager performance measures territory size, not performance.** Managers are ranked by total revenue, so a manager with more or bigger postcodes ranks higher regardless of how well the stores do. Revenue ranges from $5.6M to $0.7M across the 21 managers. Ranking on year-on-year growth or margin would compare them more fairly.
