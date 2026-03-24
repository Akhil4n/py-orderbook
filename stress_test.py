import cProfile
from decimal import Decimal
from orderbook import Order, MarketOrder, OrderBook, OrderSide, OrderStatus
import random
import time

def test_throughput():
    book = OrderBook()
    orders = [
        Order(side=OrderSide.BID, price=Decimal("50.00"), original_quantity=100)
        for _ in range(10000)
    ]
    
    start = time.perf_counter()
    for order in orders:
        book.add_limit_order(order)
    end = time.perf_counter()
    
    print(f"10,000 orders in {end - start:.3f}s")
    print(f"{10000 / (end - start):.0f} orders/second")

def test_matching_throughput():
    book = OrderBook()
    
    start = time.perf_counter()
    for i in range(10000):
        bid = Order(side=OrderSide.BID, price=Decimal("50.00"), original_quantity=100)
        ask = Order(side=OrderSide.ASK, price=Decimal("50.00"), original_quantity=100)
        book.add_limit_order(bid)
        book.add_limit_order(ask)
    end = time.perf_counter()
    
    print(f"10,000 matched pairs in {end - start:.3f}s")
    print(f"{20000 / (end - start):.0f} orders/second")

def test_realistic_throughput():
    random.seed(42)
    book = OrderBook()
    
    start = time.perf_counter()
    for _ in range(10000):
        action = random.choice(["limit", "market", "cancel"])
        side = random.choice([OrderSide.BID, OrderSide.ASK])
        price = Decimal(str(random.randint(45, 55)))
        
        if action == "limit":
            order = Order(side=side, price=price, original_quantity=random.randint(1, 100))
            book.add_limit_order(order)
        elif action == "market":
            order = MarketOrder(side=side, original_quantity=random.randint(1, 100))
            book.add_market_order(order)
        elif action == "cancel" and book.orders:
            order_id = random.choice(list(book.orders.keys()))
            book.cancel_order(order_id)
    end = time.perf_counter()
    
    print(f"10,000 mixed actions in {end - start:.3f}s")
    print(f"{10000 / (end - start):.0f} actions/second")

if __name__ == "__main__":
    test_throughput()
    test_matching_throughput()
    test_realistic_throughput()
