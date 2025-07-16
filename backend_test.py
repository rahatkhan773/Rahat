#!/usr/bin/env python3
"""
Backend API Testing for RK Industry E-commerce Application
Tests all backend endpoints including authentication, products, cart, and orders
"""

import requests
import json
import sys
from datetime import datetime

# Backend URL from frontend/.env
BACKEND_URL = "https://56720222-ab3f-49ab-be1f-addda39de24a.preview.emergentagent.com/api"

class BackendTester:
    def __init__(self):
        self.base_url = BACKEND_URL
        self.session = requests.Session()
        self.auth_token = None
        self.test_user_email = "john.doe@example.com"
        self.test_user_password = "securepassword123"
        self.test_results = []
        
    def log_test(self, test_name, success, message, details=None):
        """Log test results"""
        result = {
            "test": test_name,
            "success": success,
            "message": message,
            "timestamp": datetime.now().isoformat(),
            "details": details
        }
        self.test_results.append(result)
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"{status}: {test_name} - {message}")
        if details and not success:
            print(f"   Details: {details}")
    
    def test_root_endpoint(self):
        """Test the root API endpoint"""
        try:
            response = self.session.get(f"{self.base_url}/")
            if response.status_code == 200:
                data = response.json()
                if "RK Industry API" in data.get("message", ""):
                    self.log_test("Root Endpoint", True, "API root endpoint accessible")
                    return True
                else:
                    self.log_test("Root Endpoint", False, "Unexpected response message", data)
                    return False
            else:
                self.log_test("Root Endpoint", False, f"HTTP {response.status_code}", response.text)
                return False
        except Exception as e:
            self.log_test("Root Endpoint", False, f"Connection error: {str(e)}")
            return False
    
    def test_sample_products_initialization(self):
        """Test sample products initialization endpoint"""
        try:
            response = self.session.post(f"{self.base_url}/init-products")
            if response.status_code == 200:
                data = response.json()
                message = data.get("message", "")
                if "initialized" in message or "already initialized" in message:
                    self.log_test("Sample Products Init", True, f"Products initialization: {message}")
                    return True
                else:
                    self.log_test("Sample Products Init", False, "Unexpected response", data)
                    return False
            else:
                self.log_test("Sample Products Init", False, f"HTTP {response.status_code}", response.text)
                return False
        except Exception as e:
            self.log_test("Sample Products Init", False, f"Request error: {str(e)}")
            return False
    
    def test_user_registration(self):
        """Test user registration endpoint"""
        user_data = {
            "email": self.test_user_email,
            "password": self.test_user_password,
            "full_name": "John Doe",
            "phone": "+1234567890",
            "address": "123 Test Street, Test City, TC 12345"
        }
        
        try:
            response = self.session.post(f"{self.base_url}/register", json=user_data)
            if response.status_code == 200:
                data = response.json()
                if data.get("email") == self.test_user_email and "id" in data:
                    self.log_test("User Registration", True, "User registered successfully")
                    return True
                else:
                    self.log_test("User Registration", False, "Invalid response structure", data)
                    return False
            elif response.status_code == 400 and "already registered" in response.text:
                self.log_test("User Registration", True, "User already exists (expected for repeat tests)")
                return True
            else:
                self.log_test("User Registration", False, f"HTTP {response.status_code}", response.text)
                return False
        except Exception as e:
            self.log_test("User Registration", False, f"Request error: {str(e)}")
            return False
    
    def test_user_login(self):
        """Test user login and JWT token generation"""
        login_data = {
            "email": self.test_user_email,
            "password": self.test_user_password
        }
        
        try:
            response = self.session.post(f"{self.base_url}/login", json=login_data)
            if response.status_code == 200:
                data = response.json()
                if "access_token" in data and data.get("token_type") == "bearer":
                    self.auth_token = data["access_token"]
                    self.session.headers.update({"Authorization": f"Bearer {self.auth_token}"})
                    self.log_test("User Login", True, "Login successful, JWT token received")
                    return True
                else:
                    self.log_test("User Login", False, "Invalid token response", data)
                    return False
            else:
                self.log_test("User Login", False, f"HTTP {response.status_code}", response.text)
                return False
        except Exception as e:
            self.log_test("User Login", False, f"Request error: {str(e)}")
            return False
    
    def test_get_current_user(self):
        """Test getting current user info with JWT token"""
        if not self.auth_token:
            self.log_test("Get Current User", False, "No auth token available")
            return False
            
        try:
            response = self.session.get(f"{self.base_url}/me")
            if response.status_code == 200:
                data = response.json()
                if data.get("email") == self.test_user_email and "id" in data:
                    self.log_test("Get Current User", True, "User info retrieved successfully")
                    return True
                else:
                    self.log_test("Get Current User", False, "Invalid user data", data)
                    return False
            else:
                self.log_test("Get Current User", False, f"HTTP {response.status_code}", response.text)
                return False
        except Exception as e:
            self.log_test("Get Current User", False, f"Request error: {str(e)}")
            return False
    
    def test_get_products(self):
        """Test getting all products"""
        try:
            response = self.session.get(f"{self.base_url}/products")
            if response.status_code == 200:
                data = response.json()
                if isinstance(data, list) and len(data) >= 6:
                    # Check if we have expected categories
                    categories = set(product.get("category") for product in data)
                    expected_categories = {"clothing", "electronics", "accessories"}
                    if expected_categories.issubset(categories):
                        self.log_test("Get Products", True, f"Retrieved {len(data)} products with expected categories")
                        return True, data
                    else:
                        self.log_test("Get Products", False, f"Missing expected categories. Found: {categories}")
                        return False, data
                else:
                    self.log_test("Get Products", False, f"Expected at least 6 products, got {len(data) if isinstance(data, list) else 'non-list'}")
                    return False, data
            else:
                self.log_test("Get Products", False, f"HTTP {response.status_code}", response.text)
                return False, None
        except Exception as e:
            self.log_test("Get Products", False, f"Request error: {str(e)}")
            return False, None
    
    def test_get_products_by_category(self):
        """Test product filtering by category"""
        categories_to_test = ["clothing", "electronics", "accessories"]
        
        for category in categories_to_test:
            try:
                response = self.session.get(f"{self.base_url}/products?category={category}")
                if response.status_code == 200:
                    data = response.json()
                    if isinstance(data, list):
                        # Check if all products belong to the requested category
                        if all(product.get("category") == category for product in data):
                            self.log_test(f"Get Products - {category}", True, f"Retrieved {len(data)} {category} products")
                        else:
                            self.log_test(f"Get Products - {category}", False, "Some products don't match category filter")
                    else:
                        self.log_test(f"Get Products - {category}", False, "Response is not a list")
                else:
                    self.log_test(f"Get Products - {category}", False, f"HTTP {response.status_code}")
            except Exception as e:
                self.log_test(f"Get Products - {category}", False, f"Request error: {str(e)}")
    
    def test_shopping_cart_operations(self, products):
        """Test shopping cart add, get, and remove operations"""
        if not self.auth_token:
            self.log_test("Shopping Cart", False, "No auth token available")
            return False
            
        if not products or len(products) == 0:
            self.log_test("Shopping Cart", False, "No products available for cart testing")
            return False
        
        test_product = products[0]  # Use first product for testing
        
        # Test adding item to cart
        try:
            cart_item = {
                "product_id": test_product["id"],
                "quantity": 2
            }
            response = self.session.post(f"{self.base_url}/cart", json=cart_item)
            if response.status_code == 200:
                data = response.json()
                if data.get("product_id") == test_product["id"] and data.get("quantity") == 2:
                    self.log_test("Add to Cart", True, "Item added to cart successfully")
                    cart_item_id = data.get("id")
                else:
                    self.log_test("Add to Cart", False, "Invalid cart item response", data)
                    return False
            else:
                self.log_test("Add to Cart", False, f"HTTP {response.status_code}", response.text)
                return False
        except Exception as e:
            self.log_test("Add to Cart", False, f"Request error: {str(e)}")
            return False
        
        # Test getting cart contents
        try:
            response = self.session.get(f"{self.base_url}/cart")
            if response.status_code == 200:
                data = response.json()
                if isinstance(data, list) and len(data) > 0:
                    cart_item = data[0]
                    if "product" in cart_item and cart_item.get("quantity") == 2:
                        self.log_test("Get Cart", True, f"Cart retrieved with {len(data)} items")
                        cart_item_id = cart_item.get("id")
                    else:
                        self.log_test("Get Cart", False, "Invalid cart structure", data)
                        return False
                else:
                    self.log_test("Get Cart", False, "Empty cart or invalid response")
                    return False
            else:
                self.log_test("Get Cart", False, f"HTTP {response.status_code}", response.text)
                return False
        except Exception as e:
            self.log_test("Get Cart", False, f"Request error: {str(e)}")
            return False
        
        # Test removing item from cart
        try:
            response = self.session.delete(f"{self.base_url}/cart/{cart_item_id}")
            if response.status_code == 200:
                data = response.json()
                if "removed" in data.get("message", "").lower():
                    self.log_test("Remove from Cart", True, "Item removed from cart successfully")
                    return True
                else:
                    self.log_test("Remove from Cart", False, "Unexpected response", data)
                    return False
            else:
                self.log_test("Remove from Cart", False, f"HTTP {response.status_code}", response.text)
                return False
        except Exception as e:
            self.log_test("Remove from Cart", False, f"Request error: {str(e)}")
            return False
    
    def test_order_management(self, products):
        """Test order creation and retrieval"""
        if not self.auth_token:
            self.log_test("Order Management", False, "No auth token available")
            return False
            
        if not products or len(products) == 0:
            self.log_test("Order Management", False, "No products available for order testing")
            return False
        
        # Create test order
        test_product = products[0]
        order_data = {
            "items": [
                {
                    "product_id": test_product["id"],
                    "product_name": test_product["name"],
                    "quantity": 1,
                    "price": test_product["price"]
                }
            ],
            "total_amount": test_product["price"],
            "payment_method": "Bkash",
            "shipping_address": "123 Test Street, Test City, TC 12345"
        }
        
        try:
            response = self.session.post(f"{self.base_url}/orders", json=order_data)
            if response.status_code == 200:
                data = response.json()
                if "id" in data and data.get("total_amount") == test_product["price"]:
                    self.log_test("Create Order", True, "Order created successfully")
                    order_id = data.get("id")
                else:
                    self.log_test("Create Order", False, "Invalid order response", data)
                    return False
            else:
                self.log_test("Create Order", False, f"HTTP {response.status_code}", response.text)
                return False
        except Exception as e:
            self.log_test("Create Order", False, f"Request error: {str(e)}")
            return False
        
        # Test getting order history
        try:
            response = self.session.get(f"{self.base_url}/orders")
            if response.status_code == 200:
                data = response.json()
                if isinstance(data, list) and len(data) > 0:
                    order = data[0]  # Most recent order
                    if order.get("id") == order_id:
                        self.log_test("Get Orders", True, f"Order history retrieved with {len(data)} orders")
                        return True
                    else:
                        self.log_test("Get Orders", False, "Order not found in history")
                        return False
                else:
                    self.log_test("Get Orders", False, "No orders found or invalid response")
                    return False
            else:
                self.log_test("Get Orders", False, f"HTTP {response.status_code}", response.text)
                return False
        except Exception as e:
            self.log_test("Get Orders", False, f"Request error: {str(e)}")
            return False
    
    def run_all_tests(self):
        """Run all backend tests in sequence"""
        print("=" * 60)
        print("RK Industry Backend API Testing")
        print("=" * 60)
        
        # Test 1: Root endpoint
        if not self.test_root_endpoint():
            print("❌ Critical: API not accessible. Stopping tests.")
            return False
        
        # Test 2: Initialize sample products
        self.test_sample_products_initialization()
        
        # Test 3: User registration
        self.test_user_registration()
        
        # Test 4: User login
        if not self.test_user_login():
            print("❌ Critical: Authentication failed. Skipping authenticated tests.")
            return False
        
        # Test 5: Get current user info
        self.test_get_current_user()
        
        # Test 6: Product management
        success, products = self.test_get_products()
        if success:
            self.test_get_products_by_category()
        
        # Test 7: Shopping cart operations (requires auth and products)
        if products:
            self.test_shopping_cart_operations(products)
        
        # Test 8: Order management (requires auth and products)
        if products:
            self.test_order_management(products)
        
        # Print summary
        print("\n" + "=" * 60)
        print("TEST SUMMARY")
        print("=" * 60)
        
        passed = sum(1 for result in self.test_results if result["success"])
        total = len(self.test_results)
        
        print(f"Total Tests: {total}")
        print(f"Passed: {passed}")
        print(f"Failed: {total - passed}")
        print(f"Success Rate: {(passed/total)*100:.1f}%")
        
        if total - passed > 0:
            print("\nFailed Tests:")
            for result in self.test_results:
                if not result["success"]:
                    print(f"  - {result['test']}: {result['message']}")
        
        return passed == total

if __name__ == "__main__":
    tester = BackendTester()
    success = tester.run_all_tests()
    sys.exit(0 if success else 1)