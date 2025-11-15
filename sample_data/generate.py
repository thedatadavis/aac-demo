"""
Mock Data Generator for AaC Prototype
Generates upstream source data simulating production database (usage) and billing system (Stripe)
"""

import json
import csv
from datetime import datetime, timedelta
from faker import Faker
import random

fake = Faker()
Faker.seed(42)  # For reproducibility
random.seed(42)

# Configuration
OUTPUT_DIR = "."
BASE_DATE = datetime(2024, 11, 1)

def generate_customers():
    """Generate 3 distinct customers"""
    customers = [
        {
            "customer_id": "cust_001",
            "name": fake.company(),
            "email": fake.company_email(),
            "created_at": BASE_DATE.isoformat(),
            "tier": "free"
        },
        {
            "customer_id": "cust_002",
            "name": fake.company(),
            "email": fake.company_email(),
            "created_at": BASE_DATE.isoformat(),
            "tier": "payg"
        },
        {
            "customer_id": "cust_003",
            "name": fake.company(),
            "email": fake.company_email(),
            "created_at": BASE_DATE.isoformat(),
            "tier": "prepaid"
        }
    ]
    
    with open(f"{OUTPUT_DIR}/customers.json", "w") as f:
        json.dump(customers, f, indent=2)
    
    print(f"✓ Generated {len(customers)} customers")
    return customers

def generate_products():
    """Generate 3 products"""
    products = [
        {
            "product_id": "prod_001",
            "name": "Product Analytics",
            "description": "Track and analyze user behavior and product metrics",
            "unit": "event"
        },
        {
            "product_id": "prod_002",
            "name": "Session Replay",
            "description": "Record and replay user sessions for debugging",
            "unit": "session"
        },
        {
            "product_id": "prod_003",
            "name": "Feature Flags",
            "description": "Control feature rollouts and A/B testing",
            "unit": "flag_evaluation"
        }
    ]
    
    with open(f"{OUTPUT_DIR}/products.json", "w") as f:
        json.dump(products, f, indent=2)
    
    print(f"✓ Generated {len(products)} products")
    return products

def generate_contracts(customers, products):
    """Generate contracts with different billing scenarios
    Customer 3 has a single multi-product contract"""
    contracts = [
        {
            "contract_id": "cont_001",
            "customer_id": "cust_001",
            "product_id": "prod_002",  # Session Replay
            "contract_type": "free_tier",
            "start_date": BASE_DATE.isoformat(),
            "end_date": (BASE_DATE + timedelta(days=365)).isoformat(),
            "pricing": {
                "model": "free_tier",
                "free_units": 1000000,
                "overage_rate": 0.0
            }
        },
        {
            "contract_id": "cont_002",
            "customer_id": "cust_002",
            "product_id": "prod_001",  # Product Analytics
            "contract_type": "pay_as_you_go",
            "start_date": BASE_DATE.isoformat(),
            "end_date": (BASE_DATE + timedelta(days=365)).isoformat(),
            "pricing": {
                "model": "payg_with_free_tier",
                "free_units": 1000000,
                "rate_per_unit": 0.0005
            }
        },
        {
            "contract_id": "cont_003",
            "customer_id": "cust_003",
            "contract_type": "enterprise_multi_product",
            "start_date": BASE_DATE.isoformat(),
            "end_date": (BASE_DATE + timedelta(days=365)).isoformat(),
            "components": [
                {
                    "product_id": "prod_001",  # Product Analytics
                    "pricing": {
                        "model": "prepaid_with_free_tier",
                        "free_units": 1000000,
                        "upfront_payment": 1000.00,
                        "included_units": 5000000,
                        "rate_per_unit": 0.0002,
                        "overage_rate": 0.00025
                    }
                },
                {
                    "product_id": "prod_002",  # Session Replay
                    "pricing": {
                        "model": "payg_with_free_tier",
                        "free_units": 1000000,
                        "rate_per_unit": 0.0008
                    }
                },
                {
                    "product_id": "prod_003",  # Feature Flags
                    "pricing": {
                        "model": "payg_with_free_tier",
                        "free_units": 1000000,
                        "rate_per_unit": 0.00008
                    }
                }
            ]
        }
    ]
    
    with open(f"{OUTPUT_DIR}/contracts.json", "w") as f:
        json.dump(contracts, f, indent=2)
    
    print(f"✓ Generated {len(contracts)} contracts")
    return contracts

def generate_usage_events(customers, products):
    """Generate 175 mock usage events across all customers (25 for cust_001, 50 for cust_002, 100 for cust_003)
    Customer 3 uses all three products and exceeds prepaid credit on Product Analytics"""
    
    events = []
    event_id = 1
    
    # Distribution strategy:
    # Customer 1 (Free): 25 events = 800K sessions (under 1M free tier)
    # Customer 2 (PAYG): 50 events = 4M events (will generate $2,000 in charges)
    # Customer 3 (Multi-product): 100 events total
    #   - Product Analytics: 6M events (exceeds 5M prepaid by 1M)
    #   - Session Replay: 2.4M sessions
    #   - Feature Flags: 1.6M evaluations
    
    # Customer 1: 25 events, Session Replay
    for i in range(25):
        event_date = BASE_DATE + timedelta(
            days=random.randint(1, 30),
            hours=random.randint(0, 23),
            minutes=random.randint(0, 59)
        )
        events.append({
            "event_id": f"evt_{event_id:06d}",
            "customer_id": "cust_001",
            "product_id": "prod_002",  # Session Replay
            "event_count": 32000,  # 25 * 32K = 800K sessions
            "timestamp": event_date.isoformat(),
            "metadata": {
                "source": "production_api",
                "version": "1.0"
            }
        })
        event_id += 1
    
    # Customer 2: 50 events, Product Analytics
    for i in range(50):
        event_date = BASE_DATE + timedelta(
            days=random.randint(1, 30),
            hours=random.randint(0, 23),
            minutes=random.randint(0, 59)
        )
        events.append({
            "event_id": f"evt_{event_id:06d}",
            "customer_id": "cust_002",
            "product_id": "prod_001",  # Product Analytics
            "event_count": 80000,  # 50 * 80K = 4M events
            "timestamp": event_date.isoformat(),
            "metadata": {
                "source": "production_api",
                "version": "1.0"
            }
        })
        event_id += 1
    
    # Customer 3: 100 events across all three products
    # 50 events for Product Analytics (4M events total, to reach 6M with prepaid overage)
    for i in range(50):
        event_date = BASE_DATE + timedelta(
            days=random.randint(1, 30),
            hours=random.randint(0, 23),
            minutes=random.randint(0, 59)
        )
        events.append({
            "event_id": f"evt_{event_id:06d}",
            "customer_id": "cust_003",
            "product_id": "prod_001",  # Product Analytics
            "event_count": 120000,  # 50 * 120K = 6M total
            "timestamp": event_date.isoformat(),
            "metadata": {
                "source": "production_api",
                "version": "1.0"
            }
        })
        event_id += 1
    
    # 30 events for Session Replay (2.4M sessions)
    for i in range(30):
        event_date = BASE_DATE + timedelta(
            days=random.randint(1, 30),
            hours=random.randint(0, 23),
            minutes=random.randint(0, 59)
        )
        events.append({
            "event_id": f"evt_{event_id:06d}",
            "customer_id": "cust_003",
            "product_id": "prod_002",  # Session Replay
            "event_count": 80000,  # 30 * 80K = 2.4M sessions
            "timestamp": event_date.isoformat(),
            "metadata": {
                "source": "production_api",
                "version": "1.0"
            }
        })
        event_id += 1
    
    # 20 events for Feature Flags (1.6M evaluations)
    for i in range(20):
        event_date = BASE_DATE + timedelta(
            days=random.randint(1, 30),
            hours=random.randint(0, 23),
            minutes=random.randint(0, 59)
        )
        events.append({
            "event_id": f"evt_{event_id:06d}",
            "customer_id": "cust_003",
            "product_id": "prod_003",  # Feature Flags
            "event_count": 80000,  # 20 * 80K = 1.6M evaluations
            "timestamp": event_date.isoformat(),
            "metadata": {
                "source": "production_api",
                "version": "1.0"
            }
        })
        event_id += 1
    
    # Sort by timestamp
    events.sort(key=lambda x: x["timestamp"])
    
    with open(f"{OUTPUT_DIR}/usage_events.json", "w") as f:
        json.dump(events, f, indent=2)
    
    # Calculate totals for verification
    totals = {}
    for event in events:
        key = (event["customer_id"], event["product_id"])
        totals[key] = totals.get(key, 0) + event["event_count"]
    
    print(f"✓ Generated {len(events)} usage events")
    print(f"  Usage totals by customer and product:")
    for (cust_id, prod_id), total in sorted(totals.items()):
        print(f"    {cust_id} - {prod_id}: {total:,} units")
    
    return events

def generate_cash_receipts():
    """Generate 2 mock cash receipts from Stripe for Customer 2 and Customer 3"""
    
    receipts = [
        {
            "receipt_id": "ch_stripe_001",
            "customer_id": "cust_002",
            "amount": 2000.00,
            "currency": "USD",
            "payment_date": (BASE_DATE + timedelta(days=31)).strftime("%Y-%m-%d"),
            "payment_method": "card",
            "stripe_charge_id": "ch_3ABC123XYZ",
            "description": "Product Analytics - November usage",
            "status": "succeeded"
        },
        {
            "receipt_id": "ch_stripe_002",
            "customer_id": "cust_003",
            "amount": 1000.00,
            "currency": "USD",
            "payment_date": BASE_DATE.strftime("%Y-%m-%d"),
            "payment_method": "card",
            "stripe_charge_id": "ch_3DEF456ABC",
            "description": "Multi-product Bundle - Prepaid Credits",
            "status": "succeeded"
        }
    ]
    
    # Write to CSV
    with open(f"{OUTPUT_DIR}/cash_receipts.csv", "w", newline="") as f:
        fieldnames = ["receipt_id", "customer_id", "amount", "currency", 
                     "payment_date", "payment_method", "stripe_charge_id", 
                     "description", "status"]
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(receipts)
    
    print(f"✓ Generated {len(receipts)} cash receipts")
    return receipts

def main():
    """Generate all mock data files"""
    print("\n" + "="*60)
    print("Mock Data Generator for AaC Prototype")
    print("="*60 + "\n")
    
    customers = generate_customers()
    products = generate_products()
    contracts = generate_contracts(customers, products)
    events = generate_usage_events(customers, products)
    receipts = generate_cash_receipts()
    
    print("\n" + "="*60)
    print("✓ All mock data files generated successfully!")
    print("="*60)
    print("\nFiles created:")
    print("  • customers.json")
    print("  • products.json")
    print("  • contracts.json")
    print("  • usage_events.json")
    print("  • cash_receipts.csv")
    print("\nBilling Scenario Summary:")
    print("  • Customer 1: Free tier Session Replay (800K/1M sessions - stays under limit, $0)")
    print("  • Customer 2: PAYG Product Analytics with 1M free tier")
    print("    - Usage: 4M events (1M free + 3M billable @ $0.0005 = $1,500)")
    print("  • Customer 3: Enterprise multi-product bundle with discounted rates")
    print("    - Product Analytics: 6M events (1M free + 5M prepaid + 0 overage)")
    print("    - Session Replay: 2.4M sessions (1M free + 1.4M @ $0.0008 = $1,120)")
    print("    - Feature Flags: 1.6M evals (1M free + 600K @ $0.00008 = $48)")
    print("    - Total for Customer 3: $1,168 + $1,000 prepaid = $2,168")
    print()

if __name__ == "__main__":
    main()
