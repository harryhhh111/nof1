"""
回测引擎

实现历史数据回测功能
"""

from typing import Dict, List, Optional, Any, Callable
from dataclasses import dataclass, field
from datetime import datetime, timedelta
import pandas as pd
import numpy as np
import json
import logging

from models.trading_decision import TradingDecision
from trading.paper_trader import PaperTrader
from risk_management.risk_manager import RiskManager

logger = logging.getLogger(__name__)


@dataclass
class BacktestConfig:
    """回测配置"""

    initial_balance: float = 100000.0
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
    symbols: List[str] = field(default_factory=lambda: ['BTCUSDT'])
    fee_rate: float = 0.001
    slippage: float = 0.0005
    max_position_size: float = 0.1
    max_leverage: float = 10.0


@dataclass
class TradeRecord:
    """交易记录"""

    timestamp: datetime
    symbol: str
    action: str
    price: float
    size: float
    pnl: float
    balance: float
    equity: float
    drawdown: float
    decision: Dict = field(default_factory=dict)


@dataclass
class PerformanceMetrics:
    """性能指标"""

    total_return: float
    annualized_return: float
    sharpe_ratio: float
    max_drawdown: float
    win_rate: float
    profit_factor: float
    total_trades: int
    avg_trade: float
    best_trade: float
    worst_trade: float
    volatility: float
    calmar_ratio: float

    def to_dict(self) -> Dict[str, float]:
        return {
            'total_return': self.total_return,
            'annualized_return': self.annualized_return,
            'sharpe_ratio': self.sharpe_ratio,
            'max_drawdown': self.max_drawdown,
            'win_rate': self.win_rate,
            'profit_factor': self.profit_factor,
            'total_trades': self.total_trades,
            'avg_trade': self.avg_trade,
            'best_trade': self.best_trade,
            'worst_trade': self.worst_trade,
            'volatility': self.volatility,
            'calmar_ratio': self.calmar_ratio
        }


class BacktestEngine:
    """
    回测引擎

    功能：
    - 历史数据回测
    - 策略性能评估
    - 交易记录分析
    - 可视化报告生成
    """

    def __init__(self, config: BacktestConfig):
        """
        初始化回测引擎

        Args:
            config: 回测配置
        """
        self.config = config
        self.paper_trader = PaperTrader(
            initial_balance=config.initial_balance,
            fee_rate=config.fee_rate
        )
        self.risk_manager = RiskManager(
            account_balance=config.initial_balance,
            max_position_size=config.max_position_size,
            max_leverage=config.max_leverage
        )

        # 回测结果
        self.trades: List[TradeRecord] = []
        self.equity_curve: List[Dict] = []
        self.returns: List[float] = []
        self.drawdowns: List[float] = []

        # 统计
        self.total_trades = 0
        self.winning_trades = 0
        self.losing_trades = 0

    def run_backtest(
        self,
        market_data: Dict[str, pd.DataFrame],
        strategy_func: Callable[[str, pd.DataFrame, Dict], TradingDecision]
    ) -> PerformanceMetrics:
        """
        运行回测

        Args:
            market_data: 市场数据 {symbol: DataFrame}
            strategy_func: 策略函数

        Returns:
            性能指标
        """
        logger.info(f"开始回测，初始资金: ${self.config.initial_balance:,.2f}")
        logger.info(f"回测期间: {self.config.start_date} - {self.config.end_date}")
        logger.info(f"交易对: {', '.join(self.config.symbols)}")

        # 遍历每个交易日
        for timestamp, market_snapshot in self._iterate_market_data(market_data):
            try:
                # 为每个交易对生成决策
                for symbol in self.config.symbols:
                    if symbol not in market_data:
                        continue

                    # 获取历史数据
                    hist_data = market_data[symbol].loc[:timestamp]

                    # 生成决策
                    decision = strategy_func(symbol, hist_data, market_snapshot)

                    if decision and decision.action != "HOLD":
                        # 执行决策
                        current_price = market_snapshot.get('close', 0)
                        if current_price > 0:
                            result = self.paper_trader.execute_decision(decision, current_price)

                            # 记录交易
                            if result['status'] == 'success':
                                self._record_trade(timestamp, symbol, decision, result, current_price)

                # 更新价格
                price_data = {symbol: market_snapshot.get('close', 0) for symbol in self.config.symbols}
                self.paper_trader.update_prices(price_data)

                # 记录权益曲线
                equity = self.paper_trader.get_portfolio_value(price_data)
                self._record_equity(timestamp, equity)

            except Exception as e:
                logger.error(f"回测执行错误 {timestamp}: {e}")

        # 计算性能指标
        metrics = self._calculate_performance_metrics()

        logger.info(f"回测完成!")
        logger.info(f"总交易次数: {metrics.total_trades}")
        logger.info(f"总回报: {metrics.total_return*100:.2f}%")
        logger.info(f"最大回撤: {metrics.max_drawdown*100:.2f}%")
        logger.info(f"夏普比率: {metrics.sharpe_ratio:.2f}")

        return metrics

    def _iterate_market_data(self, market_data: Dict[str, pd.DataFrame]):
        """
        遍历市场数据

        Args:
            market_data: 市场数据

        Yields:
            (timestamp, market_snapshot)
        """
        # 获取所有时间戳
        all_timestamps = set()
        for df in market_data.values():
            all_timestamps.update(df.index)

        all_timestamps = sorted(list(all_timestamps))

        # 过滤日期范围
        if self.config.start_date:
            all_timestamps = [ts for ts in all_timestamps if ts >= self.config.start_date]
        if self.config.end_date:
            all_timestamps = [ts for ts in all_timestamps if ts <= self.config.end_date]

        # 遍历每个时间点
        for timestamp in all_timestamps:
            market_snapshot = {}
            for symbol, df in market_data.items():
                if timestamp in df.index:
                    market_snapshot[symbol] = df.loc[timestamp].to_dict()

            if market_snapshot:  # 只返回有数据的时间点
                yield timestamp, market_snapshot

    def _record_trade(
        self,
        timestamp: datetime,
        symbol: str,
        decision: TradingDecision,
        result: Dict,
        price: float
    ):
        """
        记录交易

        Args:
            timestamp: 时间戳
            symbol: 交易对
            decision: 交易决策
            result: 执行结果
            price: 执行价格
        """
        # 计算PnL
        pnl = result.get('pnl', 0) if 'pnl' in result else 0

        # 记录交易
        trade = TradeRecord(
            timestamp=timestamp,
            symbol=symbol,
            action=decision.action,
            price=price,
            size=result.get('size', 0),
            pnl=pnl,
            balance=self.paper_trader.balance,
            equity=self.paper_trader.balance + pnl,
            drawdown=0,  # 稍后计算
            decision=decision.to_dict()
        )

        self.trades.append(trade)
        self.total_trades += 1

        if pnl > 0:
            self.winning_trades += 1
        elif pnl < 0:
            self.losing_trades += 1

    def _record_equity(self, timestamp: datetime, equity: float):
        """
        记录权益曲线

        Args:
            timestamp: 时间戳
            equity: 权益
        """
        self.equity_curve.append({
            'timestamp': timestamp,
            'equity': equity,
            'return': (equity - self.config.initial_balance) / self.config.initial_balance
        })

    def _calculate_performance_metrics(self) -> PerformanceMetrics:
        """
        计算性能指标

        Returns:
            性能指标
        """
        if not self.equity_curve:
            return PerformanceMetrics(
                total_return=0, annualized_return=0, sharpe_ratio=0, max_drawdown=0,
                win_rate=0, profit_factor=0, total_trades=0, avg_trade=0,
                best_trade=0, worst_trade=0, volatility=0, calmar_ratio=0
            )

        # 计算收益率
        equity_values = [e['equity'] for e in self.equity_curve]
        returns = np.diff(equity_values) / equity_values[:-1]

        # 总回报
        total_return = (equity_values[-1] - self.config.initial_balance) / self.config.initial_balance

        # 年化回报
        days = (self.equity_curve[-1]['timestamp'] - self.equity_curve[0]['timestamp']).days
        annualized_return = (1 + total_return) ** (365 / max(days, 1)) - 1

        # 夏普比率
        if len(returns) > 1 and np.std(returns) > 0:
            excess_returns = returns - 0.02 / 365  # 日化无风险利率
            sharpe_ratio = np.mean(excess_returns) / np.std(returns) * np.sqrt(365)
        else:
            sharpe_ratio = 0

        # 最大回撤
        peak = equity_values[0]
        max_dd = 0
        for value in equity_values:
            if value > peak:
                peak = value
            dd = (peak - value) / peak
            max_dd = max(max_dd, dd)

        # 胜率
        win_rate = self.winning_trades / max(self.total_trades, 1)

        # 盈亏比
        winning_pnls = [t.pnl for t in self.trades if t.pnl > 0]
        losing_pnls = [t.pnl for t in self.trades if t.pnl < 0]
        avg_win = np.mean(winning_pnls) if winning_pnls else 0
        avg_loss = abs(np.mean(losing_pnls)) if losing_pnls else 0
        profit_factor = (avg_win * len(winning_pnls)) / (avg_loss * len(losing_pnls)) if avg_loss > 0 else float('inf')

        # 平均交易
        avg_trade = np.mean([t.pnl for t in self.trades]) if self.trades else 0
        best_trade = max([t.pnl for t in self.trades]) if self.trades else 0
        worst_trade = min([t.pnl for t in self.trades]) if self.trades else 0

        # 波动率
        volatility = np.std(returns) * np.sqrt(365) if len(returns) > 1 else 0

        # 卡尔玛比率
        calmar_ratio = annualized_return / max(max_dd, 0.001)

        return PerformanceMetrics(
            total_return=total_return,
            annualized_return=annualized_return,
            sharpe_ratio=sharpe_ratio,
            max_drawdown=max_dd,
            win_rate=win_rate,
            profit_factor=profit_factor,
            total_trades=self.total_trades,
            avg_trade=avg_trade,
            best_trade=best_trade,
            worst_trade=worst_trade,
            volatility=volatility,
            calmar_ratio=calmar_ratio
        )

    def generate_report(self) -> Dict[str, Any]:
        """
        生成回测报告

        Returns:
            报告字典
        """
        metrics = self._calculate_performance_metrics()

        # 交易统计
        trade_stats = {
            'total_trades': self.total_trades,
            'winning_trades': self.winning_trades,
            'losing_trades': self.losing_trades,
            'win_rate': metrics.win_rate,
            'avg_trade': metrics.avg_trade,
            'best_trade': metrics.best_trade,
            'worst_trade': metrics.worst_trade
        }

        # 风险指标
        risk_stats = {
            'total_return': metrics.total_return,
            'annualized_return': metrics.annualized_return,
            'max_drawdown': metrics.max_drawdown,
            'sharpe_ratio': metrics.sharpe_ratio,
            'calmar_ratio': metrics.calmar_ratio,
            'volatility': metrics.volatility
        }

        return {
            'config': {
                'initial_balance': self.config.initial_balance,
                'start_date': self.config.start_date.isoformat() if self.config.start_date else None,
                'end_date': self.config.end_date.isoformat() if self.config.end_date else None,
                'symbols': self.config.symbols,
                'fee_rate': self.config.fee_rate
            },
            'performance': metrics.to_dict(),
            'trades': [t.__dict__ for t in self.trades],
            'equity_curve': self.equity_curve,
            'trade_statistics': trade_stats,
            'risk_statistics': risk_stats
        }

    def export_trades(self, file_path: str):
        """
        导出交易记录

        Args:
            file_path: 文件路径
        """
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump([t.__dict__ for t in self.trades], f, indent=2, default=str)

    def export_report(self, file_path: str):
        """
        导出回测报告

        Args:
            file_path: 文件路径
        """
        report = self.generate_report()
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(report, f, indent=2, default=str)

    def plot_equity_curve(self, save_path: Optional[str] = None):
        """
        绘制权益曲线

        Args:
            save_path: 保存路径（可选）
        """
        try:
            import matplotlib.pyplot as plt

            if not self.equity_curve:
                logger.warning("没有权益曲线数据")
                return

            df = pd.DataFrame(self.equity_curve)
            df.set_index('timestamp', inplace=True)

            fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(12, 8))

            # 权益曲线
            ax1.plot(df.index, df['equity'], label='权益')
            ax1.set_title('权益曲线')
            ax1.set_ylabel('权益 ($)')
            ax1.legend()
            ax1.grid(True)

            # 回撤
            equity = df['equity'].values
            peak = np.maximum.accumulate(equity)
            drawdown = (equity - peak) / peak * 100

            ax2.fill_between(df.index, drawdown, 0, color='red', alpha=0.3)
            ax2.set_title('回撤')
            ax2.set_ylabel('回撤 (%)')
            ax2.set_xlabel('时间')
            ax2.grid(True)

            plt.tight_layout()

            if save_path:
                plt.savefig(save_path, dpi=300, bbox_inches='tight')
                logger.info(f"图表已保存到 {save_path}")
            else:
                plt.show()

        except ImportError:
            logger.warning("未安装 matplotlib，无法绘制图表")


class SimpleStrategy:
    """
    简单策略示例

    基于移动平均线的简单策略
    """

    def __init__(self, short_window: int = 20, long_window: int = 50):
        self.short_window = short_window
        self.long_window = long_window

    def generate_signal(self, symbol: str, data: pd.DataFrame, market_snapshot: Dict) -> TradingDecision:
        """
        生成交易信号

        Args:
            symbol: 交易对
            data: 历史数据
            market_snapshot: 当前市场数据

        Returns:
            交易决策
        """
        if len(data) < self.long_window:
            return TradingDecision(
                action="HOLD",
                confidence=50,
                reasoning="数据不足",
                position_size=0,
                risk_level="MEDIUM",
                risk_score=50,
                model_source="strategy",
                timeframe="backtest"
            )

        # 计算移动平均
        short_ma = data['close'].rolling(self.short_window).mean().iloc[-1]
        long_ma = data['close'].rolling(self.long_window).mean().iloc[-1]

        current_price = market_snapshot.get('close', 0)

        # 生成信号
        if short_ma > long_ma:
            return TradingDecision(
                action="BUY",
                confidence=70,
                reasoning=f"短期均线({short_ma:.2f})上穿长期均线({long_ma:.2f})",
                entry_price=current_price,
                position_size=10,  # 10%
                risk_level="MEDIUM",
                risk_score=60,
                model_source="ma_strategy",
                timeframe="backtest"
            )
        elif short_ma < long_ma:
            return TradingDecision(
                action="SELL",
                confidence=70,
                reasoning=f"短期均线({short_ma:.2f})下穿长期均线({long_ma:.2f})",
                entry_price=current_price,
                position_size=10,
                risk_level="MEDIUM",
                risk_score=60,
                model_source="ma_strategy",
                timeframe="backtest"
            )
        else:
            return TradingDecision(
                action="HOLD",
                confidence=50,
                reasoning="均线无交叉信号",
                position_size=0,
                risk_level="MEDIUM",
                risk_score=50,
                model_source="ma_strategy",
                timeframe="backtest"
            )
