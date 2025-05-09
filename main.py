from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup
import pandas as pd
import schedule
import time
from datetime import datetime
import random
import os

# Danh sách User-Agent để xoay vòng
#USER_AGENTS = [
    #'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
    #'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:89.0) Gecko/20100101 Firefox/89.0',
    #'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
    #'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.1.1 Safari/605.1.15',
#]

def setup_driver():
    chrome_options = Options()
    

    service = Service(executable_path="E:/TuDongHoaQuyTrinh/BaiTapLon/chromedriver.exe")
    driver = webdriver.Chrome(service=service, options=chrome_options)
    return driver

driver = setup_driver()
driver.get("https://vnexpress.net/")
print("Trình duyệt đã khởi chạy thành công!")
driver.quit()

def scrape_vnexpress_category(driver, category_url):
    """Scrape tất cả bài viết từ một chuyên mục cụ thể"""
    articles = []
    page = 1
    max_pages = 3  # Giới hạn số trang để demo
    
    while page <= max_pages:
        print(f"Đang xử lý trang {page}...")
        current_url = f"{category_url}-p{page}" if page > 1 else category_url
        
        try:
            driver.get(current_url)
            WebDriverWait(driver, 15).until(
                EC.presence_of_element_located((By.TAG_NAME, "article")))
            
            # Kiểm tra nếu bị chuyển hướng
            if driver.current_url != current_url:
                print(f"Bị chuyển hướng đến {driver.current_url}, dừng phân trang")
                break
                
            soup = BeautifulSoup(driver.page_source, 'html.parser')
            
            # Tìm tất cả bài viết với nhiều class khác nhau
            news_items = soup.find_all('article', class_=lambda x: x and any(
                cls in x for cls in ['item-news', 'item-news-common', 'article-item']
            ))
            
            if not news_items:
                print("Không tìm thấy bài viết nào, có thể đã hết trang")
                break
                
            for item in news_items:
                try:
                    # Bỏ qua bài quảng cáo
                    if item.find('span', class_='txt-ads'):
                        continue
                        
                    # Lấy tiêu đề với nhiều selector dự phòng
                    title_elem = (
                        item.find('h2', class_='title-news') or 
                        item.find('h3', class_='title-news') or
                        item.find('h2', class_='title-news') or 
                        item.find('h2') or 
                        item.find('h3') or
                        item.find('a', class_='title-news')
                    )
                    
                    if not title_elem:
                        continue
                        
                    title = title_elem.get_text(strip=True)
                    if not title:
                        continue
                    
                    # Lấy mô tả
                    desc_elem = (
                        item.find('p', class_='description') or 
                        item.find('p', class_='lead') or
                        item.find('p', class_='summary') or
                        item.find('p')
                    )
                    description = desc_elem.get_text(strip=True) if desc_elem else ''
                    
                    # Lấy link bài viết
                    link_elem = item.find('a', href=True)
                    if not link_elem:
                        continue
                        
                    link = link_elem['href']
                    if not link.startswith('http'):
                        link = 'https://vnexpress.net' + link
                    
                    # Scrape nội dung chi tiết với delay ngẫu nhiên
                    time.sleep(random.uniform(1, 3))
                    article_detail = scrape_article_detail(driver, link)
                    
                    articles.append({
                        'Tiêu đề': title,
                        'Mô tả': description,
                        'Hình ảnh': article_detail['image'],
                        'Nội dung': article_detail['content'],
                        'Link bài viết': link,
                        'Thời gian': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                        'Chuyên mục': category_url.split('/')[-1]  # Thêm tên chuyên mục
                    })
                    print(f"Đã lấy: {title}")

                except Exception as e:
                    print(f"Lỗi khi xử lý bài viết: {str(e)}")
                    continue
            
            page += 1
            time.sleep(random.uniform(2, 5))  # Delay giữa các trang
            
        except Exception as e:
            print(f"Lỗi khi scrape trang {page}: {str(e)}")
            break
    
    return articles

def scrape_article_detail(driver, url):
    """Scrape nội dung chi tiết từ một bài viết cụ thể"""
    try:
        driver.get(url)
        WebDriverWait(driver, 15).until(
            EC.presence_of_element_located((By.TAG_NAME, "article")))
        
        soup = BeautifulSoup(driver.page_source, 'html.parser')
        
        # Lấy ảnh đại diện - nhiều cách khác nhau
        image_elem = (
            soup.find('meta', property='og:image') or 
            soup.find('img', class_='lazy') or 
            soup.find('img', {'data-src': True}) or
            soup.find('img', class_='thumb')
        )
        
        image = ''
        if image_elem:
            if image_elem.get('content'):
                image = image_elem['content']
            elif image_elem.get('data-src'):
                image = image_elem['data-src']
            elif image_elem.get('src'):
                image = image_elem['src']
        
        # Lấy nội dung bài viết
        content_div = (
            soup.find('article', class_='fck_detail') or 
            soup.find('div', class_='content-detail') or
            soup.find('div', class_='body-content')
        )
        
        content = ''
        if content_div:
            # Loại bỏ các thẻ không cần thiết
            for elem in content_div.find_all(['script', 'style', 'iframe', 'ins', 'div', 'table', 'ul']):
                elem.decompose()
            
            # Lấy nội dung từ các thẻ p
            paragraphs = content_div.find_all('p')
            content = '\n'.join(p.get_text(strip=True) for p in paragraphs if p.get_text(strip=True))
        
        return {
            'image': image,
            'content': content
        }
        
    except Exception as e:
        print(f"Lỗi khi scrape chi tiết bài viết {url}: {str(e)}")
        return {
            'image': '',
            'content': ''
        }

def save_to_excel(data, filename_prefix='vnexpress_news'):
    """Lưu dữ liệu ra file Excel"""
    if not data:
        print("Không có dữ liệu để lưu")
        return
    
    df = pd.DataFrame(data)
    
    # Tạo thư mục nếu chưa tồn tại
    os.makedirs('output', exist_ok=True)
    
    # Tạo tên file với ngày giờ
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    filename = f"output/{filename_prefix}_{timestamp}.xlsx"
    
    try:
        # Lưu file Excel
        df.to_excel(filename, index=False, engine='openpyxl')
        print(f"Đã lưu {len(data)} bài viết vào file {filename}")
    except Exception as e:
        print(f"Lỗi khi lưu file Excel: {str(e)}")

def get_random_categories(num_categories=3):
    """Lấy ngẫu nhiên các chuyên mục từ danh sách"""
    all_categories = {
        'Thời sự': 'https://vnexpress.net/thoi-su',
        'Chính trị': 'https://vnexpress.net/thoi-su/chinh-tri',
        'Tinh gọn bộ máy': 'https://vnexpress.net/thoi-su/huong-toi-ky-nguyen-moi/tinh-gon-bo-may',
        'Thế giới': 'https://vnexpress.net/the-gioi',
        'Kinh doanh': 'https://vnexpress.net/kinh-doanh',
        'Khoa học công nghệ': 'https://vnexpress.net/khoa-hoc',
        'Giải trí': 'https://vnexpress.net/giai-tri',
        'Thể thao': 'https://vnexpress.net/the-thao',
        'Pháp luật': 'https://vnexpress.net/phap-luat',
        'Giáo dục': 'https://vnexpress.net/giao-duc',
        'Sức khỏe': 'https://vnexpress.net/suc-khoe',
        'Đời sống': 'https://vnexpress.net/doi-song',
        'Du lịch': 'https://vnexpress.net/du-lich',
        'Số hóa': 'https://vnexpress.net/so-hoa',
        'Xe': 'https://vnexpress.net/xe',
        'Ý kiến': 'https://vnexpress.net/y-kien',
        'Tâm sự': 'https://vnexpress.net/tam-su'
    }
    
    # Chọn ngẫu nhiên 3-5 chuyên mục
    selected_categories = random.sample(list(all_categories.items()), random.randint(2, 4))
    return dict(selected_categories)

def scrape_vnexpress():
    """Hàm chính để scrape VnExpress theo chuyên mục"""
    print(f"\nBắt đầu scrape VnExpress vào lúc {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # Khởi tạo trình duyệt
    driver = setup_driver()
    all_articles = []
    
    try:
        # Lấy ngẫu nhiên 3-5 chuyên mục
        categories = get_random_categories()
        print(f"\nCác chuyên mục được chọn ngẫu nhiên: {', '.join(categories.keys())}")
        
        for category_name, category_url in categories.items():
            print(f"\nĐang scrape chuyên mục: {category_name}")
            articles = scrape_vnexpress_category(driver, category_url)
            all_articles.extend(articles)
            print(f"Đã thu thập được {len(articles)} bài viết từ chuyên mục {category_name}")
            time.sleep(random.uniform(5, 10))
        
        if all_articles:
            save_to_excel(all_articles)
        else:
            print("Không thu thập được bài viết nào")
    
    finally:
        # Đóng trình duyệt khi hoàn thành
        driver.quit()
    
    print("Hoàn thành scrape VnExpress")

def job():
    """Hàm chạy theo lịch"""
    try:
        scrape_vnexpress()
    except Exception as e:
        print(f"Lỗi nghiêm trọng trong quá trình scrape: {str(e)}")

if __name__ == "__main__":
    # Chạy ngay lần đầu
    job()
    
    # Lên lịch chạy vào 6h sáng hàng ngày
    schedule.every().day.at("06:00").do(job)
    
    print("\nĐã lên lịch scrape hàng ngày vào 6h sáng...")
    print("Nhấn Ctrl+C để dừng chương trình")
    
    try:
        while True:
            schedule.run_pending()
            time.sleep(1)
    except KeyboardInterrupt:
        print("\nDừng chương trình...")