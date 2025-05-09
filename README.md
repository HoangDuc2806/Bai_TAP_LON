# VNExpress News Scraper

Ứng dụng tự động thu thập tin tức từ website VNExpress bằng Python, Selenium và BeautifulSoup. 
Dữ liệu được lưu dưới dạng file Excel.

## 🛠️ Các tính năng
- Thu thập tin tức từ nhiều chuyên mục khác nhau.
- Lưu thông tin bài viết gồm: tiêu đề, mô tả, hình ảnh, nội dung, link và thời gian.
- Lên lịch tự động chạy vào 6 giờ sáng hàng ngày.
- Hỗ trợ lưu dữ liệu dưới dạng file Excel.

## 🚀 Cài đặt

### 1. Clone project:
```bash
git clone <repository_url>
cd <project_folder>

2. Cài đặt các thư viện cần thiết:

 pip install -r requirements.txt

3. Tải và cấu hình ChromeDriver:

Tải ChromeDriver phù hợp với phiên bản Chrome của bạn tại: https://sites.google.com/chromium.org/driver/

Đặt đường dẫn đến ChromeDriver trong biến executable_path trong hàm setup_driver().

📝 Cách chạy chương trình

python vnexpress_scraper.py
Hoặc lên lịch tự động:
Chương trình sẽ tự động thu thập tin tức vào 6 giờ sáng hàng ngày.

Để dừng chương trình: Ctrl + C

📂 Đầu ra
Dữ liệu được lưu trong thư mục output/ với định dạng vnexpress_news_<timestamp>.xlsx.

⚠️ Lưu ý
Đảm bảo trình duyệt Chrome đã được cài đặt và tương thích với phiên bản ChromeDriver.

Chương trình có thể gặp lỗi do cấu trúc trang VNExpress thay đổi.


