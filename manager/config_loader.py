"""
配置加载器

从配置文件加载交易员配置，创建Trader实例
"""

import os
import logging
from typing import List, Dict, Any, Optional
from models.trader import Trader
from llm_clients.llm_factory import LLMClientFactory
from config.traders_config import (
    get_traders_config,
    get_llm_models_config,
    get_system_config,
    validate_config
)

logger = logging.getLogger(__name__)


class ConfigLoader:
    """
    配置加载器

    负责：
    - 从配置文件加载交易员配置
    - 验证配置的完整性
    - 创建Trader实例
    - 初始化LLM客户端
    """

    def __init__(self, config_module=None):
        """
        初始化配置加载器

        Args:
            config_module: 配置模块（可选）
        """
        self.config_module = config_module or 'config.traders_config'
        self.traders_config = []
        self.llm_models_config = {}
        self.system_config = {}

        logger.info(f"ConfigLoader 初始化完成 (配置模块: {self.config_module})")

    def load_config(self) -> bool:
        """
        加载配置

        Returns:
            bool: 是否成功加载
        """
        try:
            # 验证配置
            is_valid, errors = validate_config()
            if not is_valid:
                logger.error("❌ 配置验证失败:")
                for error in errors:
                    logger.error(f"  - {error}")
                return False

            # 加载配置
            self.traders_config = get_traders_config()
            self.llm_models_config = get_llm_models_config()
            self.system_config = get_system_config()

            logger.info(f"✅ 配置加载成功")
            logger.info(f"  交易员数量: {len(self.traders_config)}")
            logger.info(f"  LLM模型: {', '.join(self.llm_models_config.keys())}")

            return True

        except Exception as e:
            logger.error(f"❌ 配置加载失败: {e}")
            import traceback
            traceback.print_exc()
            return False

    def load_traders(self, llm_factory: Optional[LLMClientFactory] = None) -> List[Trader]:
        """
        从配置加载所有交易员

        Args:
            llm_factory: LLM工厂实例（可选）

        Returns:
            List[Trader]: 交易员实例列表
        """
        if not self.traders_config:
            logger.error("❌ 未加载配置，无法创建交易员")
            return []

        # 如果没有提供LLM工厂，尝试创建
        if llm_factory is None:
            logger.info("创建LLM工厂...")
            try:
                llm_factory = self._create_llm_factory()
            except Exception as e:
                logger.error(f"❌ LLM工厂创建失败: {e}")
                return []

        traders = []

        for config in self.traders_config:
            try:
                trader = self._create_trader_from_config(config, llm_factory)
                if trader:
                    traders.append(trader)
            except Exception as e:
                logger.error(f"❌ 创建交易员失败 {config['trader_id']}: {e}")

        logger.info(f"✅ 成功创建 {len(traders)}/{len(self.traders_config)} 个交易员")
        return traders

    def _create_llm_factory(self) -> LLMClientFactory:
        """
        创建LLM工厂

        Returns:
            LLMClientFactory: LLM工厂实例
        """
        # 收集API密钥
        api_keys = {}
        base_urls = {}

        # 从环境变量读取各LLM的API密钥
        for llm_model in self.llm_models_config.keys():
            # 根据LLM模型查找环境变量名
            env_key = None
            if llm_model == 'deepseek':
                env_key = os.getenv('DEEPSEEK_API_KEY')
                if env_key:
                    api_keys['deepseek'] = env_key
                base_url = os.getenv('DEEPSEEK_BASE_URL')
                if base_url:
                    base_urls['deepseek'] = base_url
            elif llm_model == 'qwen':
                env_key = os.getenv('QWEN_API_KEY')
                if env_key:
                    api_keys['qwen'] = env_key
                base_url = os.getenv('QWEN_BASE_URL')
                if base_url:
                    base_urls['qwen'] = base_url
            elif llm_model == 'custom':
                env_key = os.getenv('CUSTOM_LLM_API_KEY')
                if env_key:
                    api_keys['custom'] = env_key
                base_url = os.getenv('CUSTOM_LLM_BASE_URL')
                if base_url:
                    base_urls['custom'] = base_url

        if not api_keys:
            raise ValueError("未找到任何API密钥，请设置环境变量")

        # 创建工厂
        factory = LLMClientFactory(api_keys, base_urls)
        logger.info(f"✅ LLM工厂创建成功，支持模型: {factory.list_available_models()}")

        return factory

    def _create_trader_from_config(
        self,
        config: Dict[str, Any],
        llm_factory: LLMClientFactory
    ) -> Optional[Trader]:
        """
        从配置创建单个交易员

        Args:
            config: 交易员配置
            llm_factory: LLM工厂

        Returns:
            Optional[Trader]: 交易员实例或None
        """
        trader_id = config['trader_id']
        name = config['name']
        llm_model = config['llm_model']
        initial_balance = config['initial_balance']
        api_key_env = config['api_key_env']
        symbols = config.get('symbols', [])

        # 获取API密钥
        api_key = os.getenv(api_key_env)
        if not api_key:
            logger.warning(f"⚠️  环境变量 {api_key_env} 未设置，跳过交易员 {trader_id}")
            return None

        # 创建LLM客户端
        llm_client = llm_factory.get_client(llm_model)
        if not llm_client:
            logger.warning(f"⚠️  LLM模型 {llm_model} 不可用，跳过交易员 {trader_id}")
            return None

        # 创建交易员
        trader = Trader(
            trader_id=trader_id,
            name=name,
            llm_model=llm_model,
            initial_balance=initial_balance,
            llm_client=llm_client,
            symbols=symbols
        )

        logger.info(f"✅ 创建交易员: {name}")
        return trader

    def get_trader_config(self, trader_id: str) -> Optional[Dict[str, Any]]:
        """
        获取单个交易员配置

        Args:
            trader_id: 交易员ID

        Returns:
            Optional[Dict]: 配置或None
        """
        for config in self.traders_config:
            if config['trader_id'] == trader_id:
                return config
        return None

    def get_system_config(self) -> Dict[str, Any]:
        """
        获取系统配置

        Returns:
            Dict: 系统配置
        """
        return self.system_config

    def list_traders(self) -> List[Dict[str, Any]]:
        """
        列出所有交易员配置

        Returns:
            List[Dict]: 交易员配置列表
        """
        return self.traders_config

    def print_summary(self):
        """打印配置摘要"""
        print("\n" + "="*60)
        print("配置加载摘要")
        print("="*60)
        print(f"配置模块: {self.config_module}")
        print(f"交易员数量: {len(self.traders_config)}")
        print(f"LLM模型数量: {len(self.llm_models_config)}")
        print(f"系统配置: {len(self.system_config)} 项")
        print("="*60)

        # 统计各LLM模型的使用情况
        llm_usage = {}
        for config in self.traders_config:
            llm = config['llm_model']
            if llm not in llm_usage:
                llm_usage[llm] = 0
            llm_usage[llm] += 1

        if llm_usage:
            print("\nLLM模型使用分布:")
            for llm, count in llm_usage.items():
                print(f"  {llm}: {count} 个交易员")

        # 统计总初始资金
        total_balance = sum(config['initial_balance'] for config in self.traders_config)
        print(f"\n总初始资金: ${total_balance:.2f}")

        print("="*60)


def create_traders_from_config(
    config_path: Optional[str] = None,
    llm_factory: Optional[LLMClientFactory] = None
) -> List[Trader]:
    """
    从配置创建交易员的便捷函数

    Args:
        config_path: 配置文件路径（可选）
        llm_factory: LLM工厂（可选）

    Returns:
        List[Trader]: 交易员实例列表
    """
    loader = ConfigLoader()

    if not loader.load_config():
        logger.error("配置加载失败")
        return []

    traders = loader.load_traders(llm_factory)

    if traders:
        loader.print_summary()

    return traders


if __name__ == '__main__':
    # 测试代码
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )

    print("="*60)
    print("配置加载器测试")
    print("="*60)

    # 创建加载器
    loader = ConfigLoader()

    # 加载配置
    if loader.load_config():
        # 打印摘要
        loader.print_summary()

        # 尝试创建交易员
        traders = loader.load_traders()

        if traders:
            print(f"\n✅ 成功创建 {len(traders)} 个交易员")
            for trader in traders:
                print(f"  - {trader.name} ({trader.llm_model})")
        else:
            print("\n❌ 未创建任何交易员")
    else:
        print("\n❌ 配置加载失败")
