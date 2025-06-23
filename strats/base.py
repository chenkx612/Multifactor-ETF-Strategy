import backtrader as bt

class BaseStrategy(bt.Strategy):
    params = (
        ('printlog', False),
    )

    def buy(self, data=None, size=None, **kwargs):
        """重写buy, 只能买入整百股"""
        if size < 100:
            return
        size = size // 100 * 100
        return super().buy(data=data, size=size, **kwargs) 

    def sell(self, data=None, size=None, **kwargs):
        """重写sell, 只能卖出整百股"""
        if size < 100:
            return
        size = size // 100 * 100
        return super().sell(data=data, size=size, **kwargs) 

    def log(self, txt, dt=None, doprint=False):
        if self.params.printlog or doprint:
            dt = dt or self.datas[0].datetime.date(0)
            print(f'{dt.isoformat()}, {txt}')

    def notify_order(self, order):
        # 订单完成日志
        if order.status == order.Completed:
            cash = self.broker.getcash()
            value = self.broker.getvalue()
            if order.isbuy():
                self.log(
                    f'买入完成, 代码: {order.data._name}, '
                    f'数量: {order.executed.size}, 价格: {order.executed.price:.3f}, ' 
                    f'佣金: {order.executed.comm:.2f}, '
                    f'现金: {cash:.2f}, 账户价值: {value:.2f}'
                )
            elif order.issell():
                self.log(
                    f'卖出完成, 代码: {order.data._name}, '
                    f'数量: {order.executed.size}, 价格: {order.executed.price:.3f}, ' 
                    f'佣金: {order.executed.comm:.2f}, '
                    f'现金: {cash:.2f}, 账户价值: {value:.2f}'
                ) 
       
        # 订单失败日志
        elif order.status in [order.Canceled, order.Margin, order.Rejected]:
            self.log(f'订单失败, 代码: {order.data._name}, : {order.getstatusname()}')
