import pytest
from decimal import Decimal
from orderbook import Order, MarketOrder, OrderBook, OrderSide, OrderStatus

@pytest.fixture
def book():
    return OrderBook()

def test_add_limit_bid_no_match(book):
    order = Order(side=OrderSide.BID, price=Decimal("50.00"), original_quantity=100)
    book.add_limit_order(order)
    assert book.best_bid() == Decimal("50.00"), "best bid should be 50.00"
    assert book.best_ask() is None, "best ask should be none"
    assert order.order_id in book.orders
    assert order.side == OrderSide.BID
    assert order.remaining_quantity == 100

def test_add_limit_bid_with_match(book):
    bid_order = Order(side=OrderSide.BID, price=Decimal("50.00"), original_quantity=100)
    book.add_limit_order(bid_order)
    ask_order = Order(side=OrderSide.ASK, price=Decimal("50.00"), original_quantity=100)
    book.add_limit_order(ask_order)
    assert book.best_bid() is None, "best bid should be none"
    assert book.best_ask() is None, "best ask should be none"
    assert len(book.orders) == 0, "length of orders should be 0"
    assert bid_order.status == OrderStatus.FILLED
    assert ask_order.status == OrderStatus.FILLED

def test_limit_bid_partially_filled(book):
    bid_order = Order(side=OrderSide.BID, price=Decimal("50.00"), original_quantity=100)
    book.add_limit_order(bid_order)
    ask_order = Order(side=OrderSide.ASK, price=Decimal("50.00"), original_quantity=60)
    book.add_limit_order(ask_order)
    assert bid_order.remaining_quantity == 40
    assert bid_order.status == OrderStatus.PARTIALLY_FILLED
    assert ask_order.remaining_quantity == 0
    assert ask_order.status == OrderStatus.FILLED
    assert len(book.orders) == 1
    assert len(book.asks) == 0
    
def test_limit_bid_cancel(book):
    bid_order = Order(side=OrderSide.BID, price=Decimal("50.00"), original_quantity=100)
    book.add_limit_order(bid_order)
    book.cancel_order(bid_order.order_id)
    assert bid_order.status == OrderStatus.CANCELLED
    assert bid_order.order_id not in book.orders    

def test_market_bid_sweep(book):
    ask_order = Order(side=OrderSide.ASK, price=Decimal("50.00"), original_quantity=60)
    book.add_limit_order(ask_order)
    market_bid_order = MarketOrder(side=OrderSide.BID, original_quantity=60)
    book.add_market_order(market_bid_order)
    assert ask_order.remaining_quantity == 0
    assert ask_order.status == OrderStatus.FILLED
    assert market_bid_order.status == OrderStatus.FILLED
    assert len(book.orders) == 0, "orders should be empty"
    assert len(book.asks) == 0, "asks should be empty"

def test_market_bid_sweep_multiple(book):
    ask_order1 = Order(side=OrderSide.ASK, price=Decimal("50.00"), original_quantity=60)
    book.add_limit_order(ask_order1)
    ask_order2 = Order(side=OrderSide.ASK, price=Decimal("50.00"), original_quantity=60)
    book.add_limit_order(ask_order2)
    ask_order3 = Order(side=OrderSide.ASK, price=Decimal("50.00"), original_quantity=60)
    book.add_limit_order(ask_order3)
    market_bid_order = MarketOrder(side=OrderSide.BID, original_quantity=180)
    book.add_market_order(market_bid_order)
    assert ask_order1.remaining_quantity == 0
    assert ask_order1.status == OrderStatus.FILLED
    assert ask_order2.remaining_quantity == 0
    assert ask_order2.status == OrderStatus.FILLED
    assert ask_order3.remaining_quantity == 0
    assert ask_order3.status == OrderStatus.FILLED
    assert market_bid_order.status == OrderStatus.FILLED
    assert len(book.orders) == 0, "orders should be empty"
    assert len(book.asks) == 0, "asks should be empty"

def test_price_priority(book):
    bid_order1 = Order(side=OrderSide.BID, price=Decimal("50.00"), original_quantity=100)
    book.add_limit_order(bid_order1)
    bid_order2 = Order(side=OrderSide.BID, price=Decimal("55.00"), original_quantity=100)
    book.add_limit_order(bid_order2)
    ask_order1 = Order(side=OrderSide.ASK, price=Decimal("50.00"), original_quantity=100)
    book.add_limit_order(ask_order1)
    assert bid_order2.status == OrderStatus.FILLED
    assert book.best_bid() == Decimal("50.00")
    assert len(book.bids) == 1

def test_best_bid(book):
    bid_order1 = Order(side=OrderSide.BID, price=Decimal("50.00"), original_quantity=100)
    book.add_limit_order(bid_order1)
    bid_order2 = Order(side=OrderSide.BID, price=Decimal("55.00"), original_quantity=100)
    book.add_limit_order(bid_order2)
    assert book.best_bid() == Decimal("55.00")
    book.cancel_order(bid_order2.order_id)
    assert book.best_bid() == Decimal("50.00")
    
def test_cancel_nonexistant_order(book):
    assert book.cancel_order("fakeorder") == False

def test_market_order_empty_book(book):
    market_bid_order = MarketOrder(side=OrderSide.BID, original_quantity=60)
    book.add_market_order(market_bid_order)
    assert len(book.orders) == 0

def test_display(book):
    bid_order1 = Order(side=OrderSide.BID, price=Decimal("49.00"), original_quantity=100)
    bid_order2 = Order(side=OrderSide.BID, price=Decimal("50.00"), original_quantity=200)
    ask_order1 = Order(side=OrderSide.ASK, price=Decimal("51.00"), original_quantity=150)
    ask_order2 = Order(side=OrderSide.ASK, price=Decimal("52.00"), original_quantity=75)
    book.add_limit_order(bid_order1)
    book.add_limit_order(bid_order2)
    book.add_limit_order(ask_order1)
    book.add_limit_order(ask_order2)
    
    output = str(book)
    
    assert "51.00" in output
    assert "52.00" in output
    assert "49.00" in output
    assert "50.00" in output
    assert "150" in output
    assert "75" in output
    assert "100" in output
    assert "200" in output
    assert "ASKS" in output
    assert "BIDS" in output
    assert output.index("52.00") < output.index("51.00")
    assert output.index("50.00") < output.index("49.00")