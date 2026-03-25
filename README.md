# py-orderbook

A high-performance order book implementation in Python.

## Features
- Price-time priority matching engine
- Limit and market order support
- Order cancellation
- 124k+ matched orders/second throughput

## Installation & Setup
```bash
git clone https://github.com/Akhil4n/py-orderbook.git
cd py-orderbook
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

## Usage
```python
from orderbook import OrderBook, Order, MarketOrder, OrderSide
from decimal import Decimal

book = OrderBook()

# Add a limit order
order = Order(side=OrderSide.BID, price=Decimal("50.00"), original_quantity=100)
book.add_limit_order(order)

# Add a market order
market_order = MarketOrder(side=OrderSide.ASK, original_quantity=50)
book.add_market_order(market_order)

print(book) # displays current bids and asks
```

## Running Tests
```bash
pytest test_orderbook.py -v
```

## Project Structure
```
py-orderbook/
├── orderbook.py        # Core order book implementation
├── test_orderbook.py   # Unit tests
├── stress_test.py      # Performance benchmarks
└── requirements.txt
```