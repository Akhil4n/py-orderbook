# py-orderbook

A high-performance order book implementation in Python with price-time priority matching. Available as an official PyPI package.

## Installation
```bash
pip install akhil4n-orderbook
```

## Features
- Price-time priority matching engine
- Limit and market order support
- Order cancellation
- Trade log with aggressor tracking
- 124k+ matched orders/second throughput

## Usage
```python
from orderbook import OrderBook, Order, MarketOrder, OrderSide
from decimal import Decimal

book = OrderBook()

# Add a limit order
bid = Order(side=OrderSide.BID, price=Decimal("50.00"), original_quantity=100)
book.add_limit_order(bid)

# Add a matching ask
ask = Order(side=OrderSide.ASK, price=Decimal("50.00"), original_quantity=100)
book.add_limit_order(ask)

# Add a market order
market_order = MarketOrder(side=OrderSide.BID, original_quantity=50)
book.add_market_order(market_order)

# Cancel an order
book.cancel_order(bid.order_id)

# Display the book
print(book)

# View trade log
book.print_trade_log()
```

## Running Tests
```bash
git clone https://github.com/Akhil4n/py-orderbook.git
cd py-orderbook
python -m venv venv
venv\Scripts\activate  # Mac/Linux: source venv/bin/activate
pip install -r requirements-dev.txt
pytest test_orderbook.py -v
```

## Performance
```
Simple inserts:     ~416k orders/second
Matched pairs:      ~124k orders/second
Mixed actions:      ~114k orders/second
```

## Project Structure
```
py-orderbook/
├── orderbook.py        # Core implementation
├── test_orderbook.py   # Unit tests
├── stress_test.py      # Performance benchmarks
├── pyproject.toml      # Package configuration
└── requirements.txt    # Dependencies
```
