from playwright.sync_api import sync_playwright
import pandas as pd
import time
import json
from datetime import datetime

def fetch_data():
    print("开始获取数据...")
    with sync_playwright() as p:
        try:
            print("启动浏览器...")
            browser = p.chromium.launch(headless=True)
            page = browser.new_page()
            
            print("访问网页...")
            page.goto("https://furthermore.app/")
            
            print("等待页面加载...")
            page.wait_for_selector("text=All Vaults Bribes", timeout=30000)
            
            print("等待表格加载...")
            page.wait_for_selector("table", timeout=30000)
            
            # 获取表头
            print("获取表头...")
            headers = page.query_selector_all("table thead th")
            header_texts = [header.inner_text().strip() for header in headers]
            print("实际表头:", header_texts)
            
            # 等待一段时间确保数据完全加载
            time.sleep(5)
            
            print("提取表格数据...")
            rows = page.query_selector_all("table tbody tr")
            data = []
            for row in rows:
                cells = row.query_selector_all("td")
                row_data = [cell.inner_text().strip() for cell in cells]
                data.append(row_data)
                print(f"提取到一行数据: {row_data}")

            if not data:
                print("警告：没有提取到任何数据！")
                return None

            # 创建 DataFrame
            df = pd.DataFrame(data, columns=[
                "Star", "Rank", "Name", "Incentivizer", "USD/BGT", "Efficiency", 
                "APR_1", "APR_2", "APR_3", "eAPY", "APY", "APR_4", "cAPR", "TVL", 
                "Incentives", "Depletion Time", "Daily Rate", "Rate/BGT", 
                "Protocol", "BGT Capture", "Annualized BGT"
            ])

            print("\n数据预览:")
            print(df.head())

            # 将数据转换为JSON格式并保存
            json_data = {
                "timestamp": datetime.now().isoformat(),
                "vaults": df.to_dict(orient="records")
            }
            
            with open("data/vaults.json", "w", encoding="utf-8") as f:
                json.dump(json_data, f, ensure_ascii=False, indent=2)
            
            print("\n数据已保存到 data/vaults.json")
            return df

        except Exception as e:
            print(f"发生错误: {str(e)}")
            return None
        finally:
            print("关闭浏览器...")
            browser.close()

if __name__ == "__main__":
    fetch_data()
