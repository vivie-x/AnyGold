"""
AnyGold - 实时黄金价格监控桌面小工具

主入口文件
"""

from .widget import GoldPriceWidget


def main():
    """主函数"""
    widget = GoldPriceWidget()
    widget.run()


if __name__ == "__main__":
    main()

