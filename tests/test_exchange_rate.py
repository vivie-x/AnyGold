"""
汇率API测试类 - 测试获取美元兑人民币汇率
"""

import requests
import re
from bs4 import BeautifulSoup
from datetime import datetime


class ExchangeRateTest:
    """汇率API测试类"""

    def __init__(self):
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Referer': 'https://jiage.jd.com/',
            'Accept': 'application/json, text/plain, */*'
        }

    def test_primary_api(self):
        """测试主汇率API - exchangerate-api.com"""
        print("\n" + "=" * 60)
        print("测试 1: 主汇率API (exchangerate-api.com)")
        print("=" * 60)

        url = "https://api.exchangerate-api.com/v4/latest/USD"
        print(f"请求地址: {url}")

        try:
            print("发送请求中...")
            response = requests.get(url, timeout=10)

            print(f"响应状态码: {response.status_code}")

            if response.status_code == 200:
                data = response.json()

                # 显示基本信息
                print(f"\n基准货币: {data.get('base', 'N/A')}")
                print(f"更新日期: {data.get('date', 'N/A')}")

                # 获取美元兑人民币汇率
                if 'rates' in data and 'CNY' in data['rates']:
                    rate = float(data['rates']['CNY'])
                    print(f"\n✓ 成功获取汇率: 1 USD = {rate:.4f} CNY")

                    # 显示部分相关货币汇率
                    print("\n其他主要货币汇率:")
                    for currency in ['EUR', 'GBP', 'JPY', 'HKD', 'CNY']:
                        if currency in data['rates']:
                            print(f"  {currency}: {data['rates'][currency]:.4f}")

                    return rate
                else:
                    print("✗ 错误: 响应数据中未找到CNY汇率")
                    return None
            else:
                print(f"✗ 请求失败: HTTP {response.status_code}")
                return None

        except requests.exceptions.Timeout:
            print("✗ 请求超时")
            return None
        except requests.exceptions.RequestException as e:
            print(f"✗ 请求异常: {e}")
            return None
        except Exception as e:
            print(f"✗ 未知错误: {e}")
            return None

    def test_boc_api(self):
        """测试备用汇率API - 中国银行官网"""
        print("\n" + "=" * 60)
        print("测试 2: 备用汇率API (中国银行官网)")
        print("=" * 60)

        url = "https://www.boc.cn/sourcedb/whpj/"
        print(f"请求地址: {url}")

        try:
            print("发送请求中...")
            response = requests.get(url, headers=self.headers, timeout=10)

            print(f"响应状态码: {response.status_code}")

            if response.status_code == 200:
                response.encoding = 'utf-8'
                soup = BeautifulSoup(response.text, 'html.parser')

                print("解析HTML页面...")

                # 查找包含美元汇率的表格行
                rows = soup.find_all('tr')
                print(f"找到 {len(rows)} 个表格行")

                for i, row in enumerate(rows):
                    cells = row.find_all('td')
                    if len(cells) > 0:
                        # 第一列是货币名称
                        currency_name = cells[0].get_text().strip()

                        if '美元' in currency_name:
                            print(f"\n找到美元行 (第 {i+1} 行)")
                            print(f"货币名称: {currency_name}")

                            # 显示所有列的数据
                            if len(cells) >= 4:
                                print("\n汇率详情:")
                                column_names = ['货币名称', '现汇买入价', '现钞买入价', '现汇卖出价', '现钞卖出价', '中行折算价', '发布时间']
                                for idx, cell in enumerate(cells):
                                    col_name = column_names[idx] if idx < len(column_names) else f"列{idx+1}"
                                    print(f"  {col_name}: {cell.get_text().strip()}")

                                # 获取现汇卖出价（第4列，索引3）
                                rate_text = cells[3].get_text().strip()
                                rate_text = re.sub(r'\s+', '', rate_text)

                                try:
                                    rate = float(rate_text)
                                    if rate > 0:
                                        # 转换为美元兑人民币（中国银行显示的是人民币兑100美元）
                                        rate_usd_to_cny = rate / 100
                                        print(f"\n✓ 成功获取汇率: 1 USD = {rate_usd_to_cny:.4f} CNY")
                                        print(f"  (原始值: 100 USD = {rate:.2f} CNY)")
                                        return rate_usd_to_cny
                                    else:
                                        print(f"✗ 错误: 无效的汇率值 {rate}")
                                        return None
                                except ValueError:
                                    print(f"✗ 错误: 无法解析汇率文本 '{rate_text}'")
                                    return None
                            else:
                                print(f"✗ 错误: 列数不足 (只有 {len(cells)} 列)")
                                return None

                print("\n✗ 错误: 未找到美元汇率数据")
                return None
            else:
                print(f"✗ 请求失败: HTTP {response.status_code}")
                return None

        except requests.exceptions.Timeout:
            print("✗ 请求超时")
            return None
        except requests.exceptions.RequestException as e:
            print(f"✗ 请求异常: {e}")
            return None
        except Exception as e:
            print(f"✗ 未知错误: {e}")
            import traceback
            traceback.print_exc()
            return None

    def run_all_tests(self):
        """运行所有测试"""
        print("\n" + "★" * 60)
        print("汇率API测试开始")
        print(f"测试时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("★" * 60)

        # 测试主API
        rate1 = self.test_primary_api()

        # 测试备用API
        rate2 = self.test_boc_api()

        # 汇总结果
        print("\n" + "=" * 60)
        print("测试结果汇总")
        print("=" * 60)

        print(f"\n主API (exchangerate-api.com): ", end="")
        if rate1 is not None:
            print(f"✓ 成功 - 1 USD = {rate1:.4f} CNY")
        else:
            print("✗ 失败")

        print(f"备用API (中国银行): ", end="")
        if rate2 is not None:
            print(f"✓ 成功 - 1 USD = {rate2:.4f} CNY")
        else:
            print("✗ 失败")

        # 比较两个汇率
        if rate1 is not None and rate2 is not None:
            diff = abs(rate1 - rate2)
            diff_percent = (diff / rate1) * 100
            print(f"\n汇率差异: {diff:.4f} CNY ({diff_percent:.2f}%)")

            if diff_percent < 1:
                print("✓ 两个数据源的汇率基本一致")
            else:
                print("! 注意: 两个数据源的汇率差异较大")

        # 推荐使用的汇率
        print("\n推荐使用的汇率:")
        if rate1 is not None:
            print(f"  → {rate1:.4f} CNY (来自主API)")
        elif rate2 is not None:
            print(f"  → {rate2:.4f} CNY (来自备用API)")
        else:
            print("  → 6.95 CNY (默认汇率)")

        print("\n" + "★" * 60)
        print("测试完成")
        print("★" * 60 + "\n")


if __name__ == "__main__":
    # 创建测试实例并运行所有测试
    tester = ExchangeRateTest()
    tester.run_all_tests()
