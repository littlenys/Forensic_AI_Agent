import csv
from tqdm import tqdm

# Đường dẫn file log và file csv
log_file_path = 'path_to_log_file.log'  # Thay thế bằng đường dẫn thực tế
csv_file_path = log_file_path.replace('.log', '.csv')

# Hàm chuyển đổi log sang csv
with open(log_file_path, 'r', encoding='utf-8') as log_file, open(csv_file_path, 'w', newline='', encoding='utf-8') as csv_file:
    log_lines = log_file.readlines()
    csv_writer = csv.writer(csv_file)
    
    # Giả sử log có định dạng key:value, key:value,...
    headers = []
    
    # Đọc từng dòng trong file log
    for line in tqdm(log_lines, desc='Converting log to CSV'):
        # Tách các cặp key:value
        pairs = line.strip().split(', ')
        row = {}
        
        for pair in pairs:
            key, value = pair.split(':')
            if key not in headers:
                headers.append(key)
            row[key] = value
        
        # Ghi header nếu chưa có
        if csv_writer.writerow == 0:
            csv_writer.writerow(headers)
        
        # Ghi dòng dữ liệu
        csv_writer.writerow([row.get(header, '') for header in headers])

# Sau khi chạy đoạn mã trên, file CSV sẽ được tạo tại cùng vị trí với file log.