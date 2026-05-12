"""
Simple test script to verify dashboard endpoints.
Run this after starting the API server.
"""

import asyncio
import httpx
import time

async def test_dashboard_endpoints():
    """Test all dashboard endpoints and measure performance."""
    
    base_url = "http://localhost:8000"
    
    async with httpx.AsyncClient() as client:
        print("🚀 Testing Dashboard API Endpoints\n")
        
        # Test individual endpoints
        individual_endpoints = [
            "/dashboard/customers/count",
            "/dashboard/orders/count", 
            "/dashboard/products/count",
            "/dashboard/employees/count",
            "/dashboard/offices/count",
            "/dashboard/payments/count",
            "/dashboard/orderdetails/count",
            "/dashboard/productlines/count"
        ]
        
        print("📊 Testing Individual Count Endpoints:")
        individual_start = time.time()
        
        for endpoint in individual_endpoints:
            try:
                start = time.time()
                response = await client.get(f"{base_url}{endpoint}")
                end = time.time()
                
                if response.status_code == 200:
                    data = response.json()
                    print(f"  ✅ {endpoint}: {data['count']} records ({end-start:.3f}s)")
                else:
                    print(f"  ❌ {endpoint}: Status {response.status_code}")
            except Exception as e:
                print(f"  ❌ {endpoint}: Error - {e}")
        
        individual_time = time.time() - individual_start
        print(f"\n⏱️  Individual endpoints total time: {individual_time:.3f}s\n")
        
        # Test concurrent endpoint
        print("🔄 Testing Concurrent Overall Counts Endpoint:")
        concurrent_start = time.time()
        
        try:
            response = await client.get(f"{base_url}/dashboard/overall_counts")
            concurrent_time = time.time() - concurrent_start
            
            if response.status_code == 200:
                data = response.json()
                print(f"  ✅ Overall counts retrieved in {concurrent_time:.3f}s:")
                print(f"     Customers: {data['customers']}")
                print(f"     Orders: {data['orders']}")
                print(f"     Products: {data['products']}")
                print(f"     Employees: {data['employees']}")
                print(f"     Offices: {data['offices']}")
                print(f"     Payments: {data['payments']}")
                print(f"     Order Details: {data['orderdetails']}")
                print(f"     Product Lines: {data['productlines']}")
            else:
                print(f"  ❌ Overall counts: Status {response.status_code}")
        except Exception as e:
            print(f"  ❌ Overall counts: Error - {e}")
        
        print(f"\n⚡ Performance Comparison:")
        print(f"  Individual endpoints: {individual_time:.3f}s")
        print(f"  Concurrent endpoint: {concurrent_time:.3f}s")
        
        if concurrent_time < individual_time:
            speedup = individual_time / concurrent_time
            print(f"  🚀 Concurrent approach is {speedup:.1f}x faster!")
        else:
            print(f"  ⚠️  Concurrent approach was slower ({concurrent_time - individual_time:.3f}s)")

if __name__ == "__main__":
    print("Starting Dashboard API Test...")
    print("Make sure the API server is running on http://localhost:8000\n")
    
    try:
        asyncio.run(test_dashboard_endpoints())
    except KeyboardInterrupt:
        print("\n\n🛑 Test interrupted by user")
    except Exception as e:
        print(f"\n\n❌ Test failed: {e}")
