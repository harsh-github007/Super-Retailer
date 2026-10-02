# Super Retailer: Power BI Sales Report

A five-page Power BI report on the sales of two Australian clothing chains, **Ready Wear** and **Bellings**, from January 2016 to August 2017. It covers revenue, profit and margin by time, category, state and store manager, plus a what-if simulator for price and volume changes. It is built on a public practice dataset, **SuperRetailerData**.

The report is [`Super Retailer Report.pbix`](Super%20Retailer%20Report.pbix). Opening it needs [Power BI Desktop](https://powerbi.microsoft.com/desktop/), which runs on Windows. On a Mac, upload it to the Power BI web service, or use a Windows virtual machine.

## Open and edit in Power BI

1. Download and open [`Super Retailer Report.pbix`](Super%20Retailer%20Report.pbix) in Power BI Desktop.
2. Use the report tabs, slicers and what-if parameters to explore the five pages.
3. To reuse the report palette, select **View → Themes → Browse for themes** and choose [`retail-theme.json`](retail-theme.json).
4. Export the report using **File → Export → Export to PDF** when you want a static preview.

The report uses an ivory and green theme. Its model and calculations are unchanged by the styling update. The PBIX archive passes integrity checks; native rendering remains unverified until it is opened in Power BI Desktop.

A native PDF and page screenshots are needed for a visual preview. No reconstructed chart is presented as a Power BI screenshot.

## Key figures

All figures below were recalculated from the data inside the report.

| | |
| --- | --- |
| Revenue, Jan 2016 – Aug 2017 | **$60.8M** |
| Profit | **$25.9M** (42.5% margin) |
| Only complete financial year (Jul 2016 – Jun 2017) | $36.3M revenue, $15.6M profit |
| Growth, Jan–Aug 2017 vs Jan–Aug 2016 | **+16.3%** revenue |

- **Ready Wear is the bigger chain:** 71% of revenue, though at a slightly lower margin than Bellings (41.9% vs 43.9%).
- **Menswear leads**, with 20% of revenue. Groceries (27%) and Home (34%) earn the thinnest margins, well below every clothing category (40–49%).
- **New South Wales brings in 37% of revenue**, Victoria 24% and Queensland 20%.

## Report pages

| Page | What it shows |
| --- | --- |
| **Overall summary** | Revenue, profit and margin cards; revenue against target over time; revenue and profit by financial quarter; revenue by chain; units by category; a map of revenue by state; slicers for financial year and state |
| **Date-wise analysis** | Monthly revenue against target, year-to-date revenue and year-on-year change |
| **Category deep dive** | Every category plotted by revenue against margin, sized by units, with a play axis that steps through the quarters |
| **Manager performance** | Revenue by manager, with suburb drill-down |
| **Price simulation** | Independent price and volume what-if sliders |

## Data model

The data comes from one Excel workbook with five sheets, loaded with Power Query. There are about 81,000 monthly sales rows, each with a chain, postcode, category, units, sale price and cost price.

```
Sales (fact) ──Postcode──> Regions   (state, suburb)
             ──Postcode──> Managers  (store manager)
             ──Category──> Buyers    (category buyer)
             ──Date──────> Dates     (month, Australian financial year Jul–Jun, FY quarter)
```

**Calculated columns** on `Sales`:
- `Revenue = Sale Price × Total Units`
- `Profit = (Sale Price − Cost Price) × Total Units`

**Measures:**

```dax
Revenue Measure    = SUMX(Sales, Sales[Total Units] * Sales[Sale Price])
Profit Measure     = SUMX(Sales, (Sales[Sale Price] - Sales[Cost Price]) * Sales[Total Units])
Margin %           = SUM(Sales[Profit]) / SUM(Sales[Revenue])
Avg Sale Price     = SUM(Sales[Revenue]) / SUM(Sales[Total Units])
Target Revenue     = CALCULATE([Revenue Measure], PREVIOUSMONTH(Dates[Date])) * 1.05
Revenue variance   = IF(ISBLANK([Target Revenue]), BLANK(), [Revenue Measure] - [Target Revenue])
Revenue YTD        = TOTALYTD([Revenue Measure], Dates[Date])
Revenue LY         = CALCULATE([Revenue Measure], SAMEPERIODLASTYEAR(Dates[Date]))
YoY revenue change = IF(ISBLANK([Revenue LY]), BLANK(), [Revenue Measure] / [Revenue LY] - 1)
Simulated revenue  = SUMX(Sales, Sales[Sale Price] * (1 + [Price Change % Value])
                               * Sales[Total Units] * (1 + [Units Change % Value]))
```

The simulator's sliders are what-if parameter tables made with `GENERATESERIES`: −20% to +20% in 1% steps for price, and −40% to +40% in 2% steps for units.

## Calculation limits

The current YTD measure resets in January, although the report uses a July–June financial year. Price and volume are independent assumptions in the simulator, and the revenue target is prior-month revenue plus 5%. Manager revenue totals reflect territory size as well as performance. [Calculation notes](docs/calculation-notes.md) explain these limits and show proposed DAX changes.

## Data source

The queries read `SuperRetailerData` from a local Excel file. To refresh the report with your own copy, go to *Transform data → Data source settings → Change source* in Power BI Desktop.
