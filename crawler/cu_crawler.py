from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import pandas as pd
import time

def crawl_cu(driver, search_condition="", label="1+1"):
    url = "https://cu.bgfretail.com/event/plus.do?category=event&pageCode=005"
    driver.get(url)

    # 상품 목록 로딩 대기
    WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.CSS_SELECTOR, "li.prod_list"))
    )

    # 2+1이면 JS로 탭 전환 실행
    if search_condition == "24":
        driver.execute_script("goDepth('24')")
        time.sleep(2)  # 탭 전환 후 로딩 대기

    products = []
    items = driver.find_elements(By.CSS_SELECTOR, "li.prod_list")
    print(f"[{label}] 발견된 상품 수: {len(items)}개")

    for item in items:
        try:
            name = item.find_element(By.CSS_SELECTOR, "div.name p").text.strip()
        except:
            name = ""

        try:
            price = item.find_element(By.CSS_SELECTOR, "div.price strong").text.strip()
        except:
            price = ""

        try:
            badge = item.find_element(By.CSS_SELECTOR, "div.badge span").text.strip()
        except:
            badge = ""

        products.append({
            "상품명": name,
            "가격": price,
            "행사종류": badge,
            "편의점": "CU"
        })

    return products

def main():
    options = webdriver.ChromeOptions()
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")

    print("Chrome 브라우저 실행 중...")
    driver = webdriver.Chrome(options=options)

    try:
        # 1+1 수집
        print("\n[1+1] 수집 시작!")
        products_1p1 = crawl_cu(driver, search_condition="", label="1+1")

        # 2+1 수집
        print("\n[2+1] 수집 시작!")
        products_2p1 = crawl_cu(driver, search_condition="24", label="2+1")

        # 합치기
        all_products = products_1p1 + products_2p1

        # 빈 항목 제거
        df = pd.DataFrame(all_products)
        df = df[df["상품명"].str.strip() != ""]
        df = df.reset_index(drop=True)

        df.to_csv("cu_products.csv", index=False, encoding="utf-8-sig")
        print(f"\n✅ 저장 완료! cu_products.csv (총 {len(df)}개 상품)")
        print(df["행사종류"].value_counts())

    finally:
        driver.quit()
        print("브라우저 종료")

if __name__ == "__main__":
    main()