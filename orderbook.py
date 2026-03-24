from collections import OrderedDict
from dataclasses import dataclass, field
from decimal import Decimal
from enum import Enum
from sortedcontainers import SortedDict
from typing import Optional

class OrderSide(Enum):
    BID = 0
    ASK = 1

class OrderStatus(Enum):
    OPEN = 0
    PARTIALLY_FILLED = 1
    FILLED = 2
    CANCELLED = 3

_order_counter = 0

def _next_id():
    global _order_counter
    _order_counter += 1
    return str(_order_counter)

# this class is for default limit orders, use MarketOrder for market order objects
@dataclass
class Order:
    side: OrderSide
    price: Decimal
    original_quantity: int
    remaining_quantity: int = field(default=0, init=False)
    order_id: str = field(default_factory=_next_id, init=False)
    status: OrderStatus = field(default=OrderStatus.OPEN, init=False)

    def __post_init__(self):
        self.remaining_quantity = self.original_quantity

@dataclass
class MarketOrder(Order):
    price: Optional[Decimal] = field(default=None, init=False)

class PriceLevel:
    def __init__(self, price: Decimal, side: OrderSide):
        self.price = price
        self.queue = OrderedDict()
        self.total_quantity = 0
        self.side = side

    def add_order(self, order: Order) -> None:
        self.queue[order.order_id] = order
        self.total_quantity += order.remaining_quantity

    def remove_order(self, order_id: str) -> bool:
        if order_id in self.queue:
            item = self.queue[order_id]
            self.total_quantity -= item.remaining_quantity
            del self.queue[order_id]
            return True
        return False

    def peek(self) -> Order:
        if self.queue:
            return next(iter(self.queue.values()))
        return None

    def pop(self) -> Order:
        if self.queue:
            item_id, item = self.queue.popitem(last=False)
            self.total_quantity -= item.remaining_quantity
            return item
        return None

class OrderBook:
    def __init__(self):
        self.bids = SortedDict(lambda x:-x) # price -> PriceLevel, sorted low to high
        self.asks = SortedDict() # price -> PriceLevel, sorted high to low
        self.orders = {} # order_id -> (PriceLevel, Order)
        self._best_bid = None
        self._best_ask = None
    
    # Price-Time priority matching algorithm
    def _match(self, order: Order):
        opposite_side = self.asks if order.side == OrderSide.BID else self.bids
        best_fn = self.best_ask if order.side == OrderSide.BID else self.best_bid
        
        best = best_fn()
        price_level = opposite_side[best]
        
        while price_level.queue and order.remaining_quantity > 0:
            curr = price_level.peek()
            if curr.remaining_quantity > order.remaining_quantity:
                order.status = OrderStatus.FILLED
                curr.status = OrderStatus.PARTIALLY_FILLED
                curr.remaining_quantity -= order.remaining_quantity
                order.remaining_quantity = 0
            elif curr.remaining_quantity == order.remaining_quantity:
                order.status = OrderStatus.FILLED
                curr.status = OrderStatus.FILLED
                curr.remaining_quantity = order.remaining_quantity = 0
                del self.orders[curr.order_id]
                price_level.pop()
            else:
                order.status = OrderStatus.PARTIALLY_FILLED
                curr.status = OrderStatus.FILLED
                order.remaining_quantity -= curr.remaining_quantity
                curr.remaining_quantity = 0
                del self.orders[curr.order_id]
                price_level.pop()

        if not price_level.queue:
            del opposite_side[best]
            if order.side == OrderSide.BID:
                self._best_ask = next(iter(self.asks.keys())) if self.asks else None
            else:
                self._best_bid = next(iter(self.bids.keys())) if self.bids else None

    def _update_limit_order(self, order: Order):
        if order.remaining_quantity > 0:
            side_dict = self.bids if order.side == OrderSide.BID else self.asks
            if order.price in side_dict:
                side_dict[order.price].add_order(order)
                self.orders[order.order_id] = (side_dict[order.price], order)
            else:
                new_price_level = PriceLevel(order.price, order.side)
                new_price_level.add_order(order)
                side_dict[order.price] = new_price_level
                self.orders[order.order_id] = (new_price_level, order)
                if order.side == OrderSide.BID:
                    if self._best_bid is None or order.price > self._best_bid:
                        self._best_bid = order.price
                else:
                    if self._best_ask is None or order.price < self._best_ask:
                        self._best_ask = order.price

    def add_limit_order(self, order: Order) -> None:
        # todo: add error handling if non Order object passed in
        price = order.price
        if order.side == OrderSide.BID:
            while self.asks and price >= self.best_ask() and order.remaining_quantity > 0:
                self._match(order)
        else:
            while self.bids and price <= self.best_bid() and order.remaining_quantity > 0:
                self._match(order)

        self._update_limit_order(order)

    def add_market_order(self, order: MarketOrder) -> None:  
        if order.side == OrderSide.BID:
            while self.asks and order.remaining_quantity > 0:
                self._match(order)
        else:
            while self.bids and order.remaining_quantity > 0:
                self._match(order)

        if order.remaining_quantity > 0:
            order.status = OrderStatus.PARTIALLY_FILLED

    def cancel_order(self, order_id: str) -> bool:
        if order_id in self.orders:
            order = self.orders[order_id][1]
            order.status = OrderStatus.CANCELLED
            if order.side == OrderSide.BID:
                self.bids[order.price].remove_order(order.order_id)
                if self.bids[order.price].total_quantity == 0:
                    del self.bids[order.price]
                    if order.price == self._best_bid:
                        self._best_bid = next(iter(self.bids.keys())) if self.bids else None
            else:
                self.asks[order.price].remove_order(order.order_id)
                if self.asks[order.price].total_quantity == 0:
                    del self.asks[order.price]
                    if order.price == self._best_ask:
                        self._best_ask = next(iter(self.asks.keys())) if self.asks else None
            del self.orders[order.order_id]
            return True
        return False

    def best_bid(self) -> Decimal:
        return self._best_bid

    def best_ask(self) -> Decimal:
        return self._best_ask

    def __str__(self):
        lines = []
        lines.append("===== ORDER BOOK =====\n")
        lines.append("ASKS\n")
        for k, v in reversed(self.asks.items()):
            lines.append(f"{k}  {v.total_quantity}\n")
        
        lines.append("---------------------\n")

        for k, v in self.bids.items():
            lines.append(f"{k}  {v.total_quantity}\n")
        lines.append("BIDS\n")
        lines.append("======================")

        return "".join(lines)

