# ABC Analysis Implementation

## Overview

ABC analysis is a inventory categorization technique that divides products into three groups based on their revenue contribution:

- **Category A** - Most valuable products (typically 20% of products generate 80% of revenue)
- **Category B** - Moderately valuable products
- **Category C** - Least valuable products

This implementation analyzes Wildberries order data to categorize products and help optimize inventory management.

---

## How It Works

### Step 1: Filter Orders

```python
filtered_orders = [
    order for order in orders 
    if not (exclude_cancelled and order.is_cancel)
]
```

**Purpose:** Remove cancelled orders from analysis to ensure accurate revenue calculations.

**Input:** List of all orders  
**Output:** List of valid (non-cancelled) orders

---

### Step 2: Aggregate by Product

```python
for order in filtered_orders:
    item = aggregated[order.nm_id]
    item["orders_count"] += 1
    item["revenue"] += order.price_with_disc
```

**Purpose:** Group orders by product and calculate metrics for each product.

**What we track:**
- Total number of orders per product
- Total revenue per product

**Example:**

```
Product: "Blue T-Shirt" (nm_id=123)
├─ Orders: 5
└─ Revenue: ₽2,500 × 5 = ₽12,500

Product: "Sneakers" (nm_id=456)
├─ Orders: 2
└─ Revenue: ₽5,000 × 2 = ₽10,000
```

---

### Step 3: Calculate Total Revenue

```python
total_revenue = sum(item["revenue"] for item in aggregated.values())
```

**Purpose:** Get the baseline for percentage calculations.

**Example:** ₽12,500 + ₽10,000 + ... = ₽100,000 (total revenue)

---

### Step 4: Sort by Revenue (Descending)

```python
sorted_items = sorted(
    aggregated.items(),
    key=lambda x: x[1]["revenue"],
    reverse=True
)
```

**Purpose:** Order products from highest to lowest revenue to apply the Pareto principle.

**Example:**

```
1. Nike Sneakers    → ₽25,000
2. Blue T-Shirt     → ₽12,500
3. Socks            → ₽5,000
4. Hat              → ₽2,500
```

---

### Step 5: Assign ABC Categories

```python
for nm_id, data in sorted_items:
    revenue_share = (data["revenue"] / total_revenue) * 100
    cumulative_share += revenue_share
    
    if cumulative_share <= threshold_a:
        category = "A"
    elif cumulative_share <= threshold_b:
        category = "B"
    else:
        category = "C"
```

**Purpose:** Categorize each product based on cumulative revenue contribution.

**Logic:**
- While cumulative share ≤ 80% → **Category A** (top performers)
- When cumulative share > 80% and ≤ 95% → **Category B** (moderate performers)
- When cumulative share > 95% → **Category C** (low performers)

**Detailed Example:**

Given: `threshold_a=80%`, `threshold_b=95%`, `total_revenue=₽100,000`

| Product | Revenue | Share | Cumulative | Category |
|---------|---------|-------|------------|----------|
| Nike Sneakers | ₽25,000 | 25% | 25% | **A** |
| Jeans | ₽20,000 | 20% | 45% | **A** |
| T-Shirt | ₽15,000 | 15% | 60% | **A** |
| Hoodie | ₽10,000 | 10% | 70% | **A** |
| Jacket | ₽8,000 | 8% | 78% | **A** |
| Hat | ₽5,000 | 5% | 83% | **B** ← crossed 80% |
| Socks | ₽7,000 | 7% | 90% | **B** |
| Gloves | ₽4,000 | 4% | 94% | **B** |
| Scarf | ₽3,000 | 3% | 97% | **C** ← crossed 95% |
| Belt | ₽3,000 | 3% | 100% | **C** |

---

### Step 6: Build Result

```python
result.append(ABCItem(
    supplier_article=data["supplier_article"],
    nm_id=nm_id,
    category=category,
    orders_count=data["orders_count"],
    revenue=round(data["revenue"], 2),
    revenue_share=round(revenue_share, 2),
    cumulative_share=round(cumulative_share, 2),
))
```

**Purpose:** Create structured output with complete product information.

---

## Output Format

The function returns a list of `ABCItem` objects, each containing:

```python
ABCItem(
    supplier_article="ABC-123",      # Product SKU
    nm_id=12345678,                  # Wildberries product ID
    barcode="1234567890123",         # Product barcode
    subject="T-Shirts",              # Product category
    brand="Nike",                    # Brand name
    category="A",                    # ABC category (A/B/C)
    orders_count=150,                # Total number of orders
    revenue=45000.00,                # Total revenue in rubles
    revenue_share=15.50,             # Percentage of total revenue
    cumulative_share=35.25           # Cumulative revenue percentage
)
```

---

## Configuration Parameters

### `threshold_a` (default: 80.0)
Cumulative revenue threshold for Category A in percent.  
Products contributing up to this threshold are marked as 'A'.

### `threshold_b` (default: 95.0)
Cumulative revenue threshold for Category B in percent.  
Products between `threshold_a` and `threshold_b` are marked as 'B'.  
Products above `threshold_b` are marked as 'C'.

### `exclude_cancelled` (default: True)
Whether to exclude cancelled orders from analysis.  
Filters out orders where `is_cancel=True`.

---

## Business Value

### Category A (High Priority)
- **Action:** Always keep in stock
- **Reason:** These products generate the majority of revenue
- **Strategy:** Focus marketing and promotions on these items

### Category B (Medium Priority)
- **Action:** Monitor regularly
- **Reason:** Moderate contribution to revenue
- **Strategy:** Maintain balanced inventory levels

### Category C (Low Priority)
- **Action:** Consider reducing stock or discontinuing
- **Reason:** Minimal revenue contribution
- **Strategy:** Avoid overstocking, may consider promotions or clearance

---

## Usage Example

```python
from src.wb.services.abc_analytics import calculate_abc_analysis
from src.wb.schemas import DateRangeRequest

# Fetch orders
orders = await client.orders.get_orders(
    date=DateRangeRequest(date="2024-01-15")
)

# Perform ABC analysis
abc_results = await calculate_abc_analysis(
    orders=orders,
    threshold_a=80.0,
    threshold_b=95.0,
    exclude_cancelled=True
)

# Process results
for item in abc_results:
    print(f"{item.brand} {item.subject} - Category {item.category}")
    print(f"  Revenue: ₽{item.revenue:,.2f} ({item.revenue_share}%)")
```

---

## Edge Cases

- **Empty order list:** Returns empty list `[]`
- **All orders cancelled:** Returns empty list `[]` (if `exclude_cancelled=True`)
- **Zero total revenue:** Returns empty list `[]`
- **Single product:** Assigned to Category A with 100% cumulative share

---

## Technical Notes

- Products are aggregated by `nm_id` (Wildberries product identifier)
- Revenue calculated using `price_with_disc` field (price after discount)
- All percentage values rounded to 2 decimal places
- Results sorted by revenue in descending order
- Category assignment based on sorted cumulative revenue contribution
